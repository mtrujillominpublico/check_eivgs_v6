import os
import json
from datetime import datetime, timedelta
from time import sleep
from functools import lru_cache
import requests

CACHE_DIR = "C:\\Users\\mtrujillo\\PycharmProjects\\check_eivg\\cache_ruc"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def cargar_cache_ruc(ruc):
    path = os.path.join(CACHE_DIR, f"{ruc}.txt")
    if not os.path.exists(path):
        return None
    f = open(path, "r", encoding="utf-8")
    try:
        contenido = json.load(f)
    finally:
        f.close()
    datos = contenido.get("datos", [])
    if not datos:
        return None
    if datos[0][5] == "TERMINADO":
        return datos
    if len(datos[0]) > 2 and datos[0][2] == 'OTRA REGION':
        return None
    fecha_guardado = datetime.strptime(contenido["fecha"], "%Y-%m-%d").date()
    if datetime.now().date() - fecha_guardado <= timedelta(days=7):
        return datos
    return None

def guardar_cache_ruc(ruc, datos):
    path = os.path.join(CACHE_DIR, f"{ruc}.txt")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "datos": datos
        }, f, ensure_ascii=False, indent=2)

@lru_cache(maxsize=None)
def get_datos_ruc(ruc):
    if ruc=='':
        return []
    datos_cached = cargar_cache_ruc(ruc)
    if datos_cached:
        return datos_cached

    # url = "http://fnlb-ph-01.minpublico.cl:8070/APIS/ws_getDatos/apiSAF"
    url = "http://fnlb-ph-01.minpublico.cl:8073/APIS/ws_getCasos/apiSAF"
    datos_caso, datos_sujeto, datos_asignaciones = None, None, None
    body_caso = {
        "ruc": ruc,
        "usrRegion": "FRLOSLAGOS",
        "usrLDAP": "mtrujillo"
    }
    response_caso = requests.get(url, json=body_caso)
    sleep(0.89)
    if response_caso.status_code == 200:
        datos_caso = response_caso.json()["data"][0]
    #     body_sujeto = {
    #         "ruc": ruc,
    #         "contexto": "api/sujeto",
    #         "usrRegion": "FRLOSLAGOS",
    #         "usrLDAP": "mtrujillo"
    #     }
    #     response_sujeto = requests.get(url, json=body_sujeto)
    #     if response_sujeto.status_code == 200:
    #         datos_sujeto = response_sujeto.json()["data"]
    #         body_asignaciones = {
    #             "ruc": ruc,
    #             "contexto": "api/asignacion",
    #             "usrRegion": "FRLOSLAGOS",
    #             "usrLDAP": "mtrujillo"
    #         }
    #         response_asignaciones = requests.get(url, json=body_asignaciones)
    #         if response_asignaciones.status_code == 200:
    #             datos_asignaciones = response_asignaciones.json()["data"]

    transferencias = 0
    # if datos_asignaciones is not None:
    #     for asig in datos_asignaciones:
    #         if str(asig["ASIGNACION"]).startswith("Transferido"):
    #             transferencias += 1

    victimas = None
    # if datos_sujeto is not None:
    #     for vict in datos_sujeto:
    #         if vict["TIPOSUJETO"] == "VICTIMA":
    #             victimas.append(vict["NOMBRESAPELLIDOS"])

    if datos_caso is not None:
        fecha_str = datos_caso.get("FECHACAMBIOESTADO")
        fecha_termino = datetime.strptime(fecha_str, "%d/%m/%Y") if fecha_str else None
    else:
        fecha_termino = None

    datos_ruc = []
    if datos_caso is not None:
        if victimas:
            for victima in victimas:
                datos_ruc.append([
                    datos_caso["ROLUNICO"],
                    victima,
                    datos_caso["FISCALIA"].strip(),
                    datos_caso["REGION"],
                    transferencias,
                    datos_caso["ESTADOCASO"],
                    fecha_termino.strftime("%Y-%m-%d") if fecha_termino else None
                ])
        else:
            datos_ruc.append([
                datos_caso["ROLUNICO"],
                None,
                datos_caso["FISCALIA"].strip(),
                datos_caso["REGION"],
                transferencias,
                datos_caso["ESTADOCASO"],
                fecha_termino.strftime("%Y-%m-%d") if fecha_termino else None
            ])
    else:
        respuesta = str(json.loads(response_caso.content.decode('utf-8'))['message'])
        if "FISCALIA DE USUARIO NO CORRESPONDE" in respuesta:
            datos_ruc.append([
                ruc,
                None,
                'OTRA REGION',
                0,
                None,
                None,
                None
            ])
        elif "NO SE PUDO OBTENER REGION DE RUC" in respuesta:
            datos_ruc = []
        else:
            datos_ruc = []

    if not datos_ruc:
        path = os.path.join(CACHE_DIR, f"{ruc}.txt")
        if os.path.exists(path):
            os.remove(path)
    else:
        guardar_cache_ruc(ruc, datos_ruc)
    return datos_ruc
