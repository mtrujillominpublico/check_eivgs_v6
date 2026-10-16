import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
from time import sleep

import requests

CACHE_DIR = "C:\\Users\\mtrujillo\\PycharmProjects\\check_eivg\\cache_ruc"
URL_SAF = "http://fnlb-ph-01.minpublico.cl:8073/APIS/ws_getCasos/apiSAF"
DIAS_VIGENCIA_CACHE = 7

os.makedirs(CACHE_DIR, exist_ok=True)


def _ruta_cache(ruc):
    return os.path.join(CACHE_DIR, f"{ruc}.txt")


def cargar_cache_ruc(ruc):
    path = _ruta_cache(ruc)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        contenido = json.load(f)
    datos = contenido.get("datos", [])
    if not datos:
        return None
    if datos[0][5] == "TERMINADO":
        return datos
    if len(datos[0]) > 2 and datos[0][2] == "OTRA REGION":
        return None
    fecha_guardado = datetime.strptime(contenido["fecha"], "%Y-%m-%d").date()
    if datetime.now().date() - fecha_guardado <= timedelta(days=DIAS_VIGENCIA_CACHE):
        return datos
    return None


def guardar_cache_ruc(ruc, datos):
    with open(_ruta_cache(ruc), "w", encoding="utf-8") as f:
        json.dump({"fecha": datetime.now().strftime("%Y-%m-%d"), "datos": datos},
                  f, ensure_ascii=False, indent=2)


@lru_cache(maxsize=None)
def get_datos_ruc(ruc):
    """Devuelve [[rol, None, fiscalia, region, 0, estado_caso, fecha_cambio_estado]] o [] si no hay datos."""
    if ruc == "":
        return []
    datos_cached = cargar_cache_ruc(ruc)
    if datos_cached:
        return datos_cached

    body_caso = {"ruc": ruc, "usrRegion": "FRLOSLAGOS", "usrLDAP": "mtrujillo"}
    response_caso = requests.get(URL_SAF, json=body_caso)
    sleep(0.89)

    datos_ruc = []
    if response_caso.status_code == 200:
        datos_caso = response_caso.json()["data"][0]
        fecha_str = datos_caso.get("FECHACAMBIOESTADO")
        fecha_termino = datetime.strptime(fecha_str, "%d/%m/%Y") if fecha_str else None
        datos_ruc.append([
            datos_caso["ROLUNICO"],
            None,
            datos_caso["FISCALIA"].strip(),
            datos_caso["REGION"],
            0,
            datos_caso["ESTADOCASO"],
            fecha_termino.strftime("%Y-%m-%d") if fecha_termino else None,
        ])
    else:
        respuesta = str(json.loads(response_caso.content.decode("utf-8"))["message"])
        if "FISCALIA DE USUARIO NO CORRESPONDE" in respuesta:
            datos_ruc.append([ruc, None, "OTRA REGION", 0, None, None, None])

    if datos_ruc:
        guardar_cache_ruc(ruc, datos_ruc)
    elif os.path.exists(_ruta_cache(ruc)):
        os.remove(_ruta_cache(ruc))
    return datos_ruc
