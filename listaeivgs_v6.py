import time
from datetime import datetime
from glob import glob
from os import scandir, stat
from re import compile

from eivg_v6 import Eivg
from lib_datos_ruc_v6 import get_datos_ruc
from ProgressBar_v6 import progress_bar

RUTA_BASE = "\\\\eivg-x\\EIVGs"
CARPETAS_FISCALIAS = [
    "FL-Ancud", "FL-Calbuco", "FL-Castro", "FL-Chaiten", "FL-Hualaihue",
    "FL-Maullin", "FL-Osorno", "FL-PuertoMontt", "FL-PuertoVaras",
    "FL-Quellon", "FL-Quinchao", "FL-RioNegro", "INTERREGIONALES",
]

RE_CARPETA = compile(
    r"RUC[_\s][0-9]{10}-[0-9K][\s_][A-ZÑÁ(]{3,8}$"
    r"|[0-9]{10}-[0-9K][\s_][A-ZÑÁ(]{2,8}$"
)

ENCABEZADO = (
    "id_eivg\truc\testado\truta_carpeta\tfiscalia_carpeta\tnombre_carpeta\tcarpeta_completa"
    "\tnombre_correcto\tfecha_carpeta\tiniciales_carpeta\tfiscalia\testado\n"
)


def _progreso(etiqueta, inicio, idx, total):
    print(f"\r{etiqueta}({idx}/{total}):{progress_bar(inicio, idx, total)}", end="")


def _buscar_carpetas(path, rutas):
    """Recorre path y agrega a `rutas` todas las subcarpetas, salvo ORIGINAL/EDITADO."""
    try:
        elementos = scandir(path)
    except OSError:
        print(f"ERROR LEYENDO RUTA {path}")
        return
    for elemento in elementos:
        if elemento.is_dir():
            ruta = str(elemento.path)
            if not ruta.endswith(("ORIGINAL", "EDITADO")):
                rutas.append(elemento.path)
            if "EDITADO" not in ruta:
                _buscar_carpetas(elemento.path, rutas)


class ListaEivgs:
    def __init__(self):
        self.lista_eivgs = {}
        print("Cargando Datos REPOSITORIO...")
        self.carga_datos_repositorio()
        print("Cargando Datos SAF...")
        self.carga_datos_saf()
        self.print_mal_nombradas()
        self.print_ruc_no_existe()
        self.revisar_fiscalias()

    def __str__(self):
        return ENCABEZADO + "".join(f"{e}\n" for e in self.lista_eivgs.values())

    def carga_datos_repositorio(self):
        rutas = [f"{RUTA_BASE}\\{nombre}" for nombre in CARPETAS_FISCALIAS]
        rutas_repositorio = []

        inicio, total = time.time(), len(rutas)
        for idx, ruta in enumerate(rutas, start=1):
            _buscar_carpetas(ruta, rutas_repositorio)
            _progreso("RUTAS FISCALIAS", inicio, idx, total)
        print()

        inicio, total = time.time(), len(rutas_repositorio)
        for idx, ruta in enumerate(rutas_repositorio, start=1):
            _progreso("RUTAS EIVGs", inicio, idx, total)

            fecha_carpeta = datetime.utcfromtimestamp(stat(ruta).st_ctime)
            if fecha_carpeta.date() == datetime.utcnow().date():
                continue

            partes = str(ruta).split("\\")
            nombre_carpeta = partes[-1]
            pos_guion = nombre_carpeta.find("-")
            ruc = nombre_carpeta[pos_guion - 10:pos_guion + 2]
            iniciales_carpeta = nombre_carpeta[pos_guion + 3:]
            key = ruc + iniciales_carpeta

            if key in self.lista_eivgs:
                self.lista_eivgs[key].avisa_repetida(ruta)
                continue

            if "INTERREGIONALES" in ruta:
                fiscalia_carpeta = partes[-2].upper()
            else:
                fiscalia_carpeta = partes[-3][3:].upper()
            if fiscalia_carpeta == "CHAITEN":
                fiscalia_carpeta = "FUTALEUFU"

            self.lista_eivgs[key] = Eivg(
                id_eivg=key, ruc=ruc, ruta_carpeta=ruta, fiscalia_repositorio=fiscalia_carpeta,
                nombre_carpeta=nombre_carpeta,
                carpeta_completa=len(glob(ruta + "\\*.mp4") + glob(ruta + "\\*.avi")) >= 2,
                nombre_correcto=bool(RE_CARPETA.match(nombre_carpeta)),
                fecha_carpeta=fecha_carpeta, iniciales_carpeta=iniciales_carpeta)
        print()

    def carga_datos_saf(self):
        inicio, total = time.time(), len(self.lista_eivgs)
        for idx, e in enumerate(self.lista_eivgs.values(), start=1):
            e.agrega_datos_saf(get_datos_ruc(e.ruc))
            _progreso("EIVGs", inicio, idx, total)
        print()

    def print_mal_nombradas(self):
        for e in self.lista_eivgs.values():
            if not e.nombre_correcto:
                print(f"NOMBRE INCORRECTO: {e.ruta_carpeta}")

    def print_ruc_no_existe(self):
        for e in self.lista_eivgs.values():
            if not e.datos_saf:
                print(f"RUC NO EXISTE: {e.ruta_carpeta}")

    def revisar_fiscalias(self):
        reemplazos = [(" ", ""), ("Ó", "O"), ("Í", "I"), ("Ú", "U")]
        con_datos = [e for e in self.lista_eivgs.values() if e.datos_saf]
        for e in sorted(con_datos, key=lambda x: x.get_region()):
            fiscalia_saf = e.datos_saf[0][2] or ""
            for viejo, nuevo in reemplazos:
                fiscalia_saf = fiscalia_saf.replace(viejo, nuevo)
            if (e.fiscalia_repositorio != fiscalia_saf
                    and e.fiscalia_repositorio != "INTERREGIONALES"
                    and fiscalia_saf != "OTRAREGION"):
                print(f"MOVER EIVG:\t{e.fiscalia_repositorio} => {fiscalia_saf}({e.datos_saf[0][3]})\t{e.ruta_carpeta}")
                e.set_estado("SE DEBE MOVER")
