from lib_datos_ruc_v6 import get_datos_ruc

REGION_POR_DEFECTO = 10


class Eivg:
    def __init__(self, id_eivg, ruc, ruta_carpeta, fiscalia_repositorio, nombre_carpeta,
                 carpeta_completa, nombre_correcto, fecha_carpeta, iniciales_carpeta):
        self.id_eivg = id_eivg
        self.ruc = ruc
        self.ruta_carpeta = ruta_carpeta
        self.fiscalia_repositorio = fiscalia_repositorio
        self.nombre_carpeta = nombre_carpeta
        self.carpeta_completa = carpeta_completa
        self.nombre_correcto = nombre_correcto
        self.fecha_carpeta = fecha_carpeta
        self.iniciales_carpeta = iniciales_carpeta
        self.estado = None
        self.datos_saf = []

    def avisa_repetida(self, ruta_repetida):
        fiscalia = get_datos_ruc(self.ruc.upper())[0][2]
        print(f"\n\nEIVG Repetida: Primera:{self.ruta_carpeta}\n\t\tRepetición:{ruta_repetida}\n\t\tFiscalia:{fiscalia}\n")

    def agrega_datos_saf(self, datos_saf):
        self.datos_saf = datos_saf

    def set_estado(self, estado):
        self.estado = estado

    def get_region(self):
        if len(self.datos_saf) == 0 or self.datos_saf[0][3] is None:
            return REGION_POR_DEFECTO
        return int(self.datos_saf[0][3])

    def __str__(self):
        try:
            fiscalia_saf, estado_saf = self.datos_saf[0][2], self.datos_saf[0][5]
        except IndexError:
            fiscalia_saf = estado_saf = "ERROR"
        campos = (self.id_eivg, self.ruc, self.estado,
                  self.ruta_carpeta, self.fiscalia_repositorio, self.nombre_carpeta,
                  self.carpeta_completa, self.nombre_correcto, self.fecha_carpeta,
                  self.iniciales_carpeta, fiscalia_saf, estado_saf)
        return "\t".join(str(c) for c in campos)
