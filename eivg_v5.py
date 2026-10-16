from lib_datos_ruc_v5 import get_datos_ruc

class Eivg:
    def __init__(self, id_eivg, origen, ruc, iniciales_reporte, estado, fiscalia_reporte, entrevistadores, ruta_carpeta,
                 fiscalia_repositorio, nombre_carpeta, carpeta_completa, nombre_correcto, fecha_carpeta,
                 iniciales_carpeta, duracion_videos):
        self.id_eivg = id_eivg
        self.origen = origen
        self.ruc = ruc
        self.iniciales_reporte = iniciales_reporte
        self.estado = estado
        self.fiscalia_reporte = fiscalia_reporte
        self.entrevistadores = entrevistadores
        self.ruta_carpeta = ruta_carpeta
        self.fiscalia_repositorio = fiscalia_repositorio
        self.nombre_carpeta = nombre_carpeta
        self.carpeta_completa = carpeta_completa
        self.nombre_correcto = nombre_correcto
        self.fecha_carpeta = fecha_carpeta
        self.iniciales_carpeta = iniciales_carpeta
        self.datos_saf = []
        self.duracion_videos = duracion_videos
        self.convertida = False

    def agrega_datos_carpeta(self, ruta_carpeta, fiscalia_carpeta, nombre_carpeta, carpeta_completa, nombre_correcto,
                             fecha_carpeta, iniciales_carpeta, duracion_videos):
        if self.ruta_carpeta is None:
            self.ruta_carpeta = ruta_carpeta
            self.fiscalia_repositorio = fiscalia_carpeta
            self.nombre_carpeta = nombre_carpeta
            self.carpeta_completa = carpeta_completa
            self.nombre_correcto = nombre_correcto
            self.fecha_carpeta = fecha_carpeta
            self.iniciales_carpeta = iniciales_carpeta
            self.duracion_videos = duracion_videos
        else:
            fiscalia = get_datos_ruc(self.ruc.upper())[0][2]
            # r = lambda p: '\\\\eivg-x\\EIVG-' + p.split('/var/www/html/habilitaEIV/origen_eiv/')[1].replace('/', '\\')
            print(f"\n\nEIVG Repetida: Primera:{self.ruta_carpeta}\n\t\tRepetición:{ruta_carpeta}\n\t\tFiscalia:{fiscalia}\n")

    def agrega_datos_saf(self, datos_saf):
        self.datos_saf = datos_saf

    def set_estado(self, estado):
        self.estado = estado

    def get_fiscalia(self):
        if self.fiscalia_repositorio is None:
            return self.fiscalia_reporte
        else:
            return self.fiscalia_repositorio

    def get_entrevistadores(self):
        if self.entrevistadores is None:
            return ''
        else:
            return str(self.entrevistadores)

    def get_region(self):
        if len(self.datos_saf) == 0 or self.datos_saf[0][3] is None:
            return 10
        else:
            return int(self.datos_saf[0][3])

    def get_ruc(self):
        return self.ruc

    def set_convertida(self):
        self.convertida = True

    def __str__(self):
        try:
            ret = f"{self.id_eivg}\t{self.origen}\t{self.ruc}\t{self.iniciales_reporte}\t{self.estado}\t" \
                  f"{self.fiscalia_reporte}\t{self.entrevistadores}\t{self.ruta_carpeta}\t" \
                  f"{self.fiscalia_repositorio}\t{self.nombre_carpeta}\t{self.carpeta_completa}\t" \
                  f"{self.nombre_correcto}\t{self.fecha_carpeta}\t{self.iniciales_carpeta}\t{self.datos_saf[0][2]}\t" \
                  f"{self.datos_saf[0][5]}\t{self.convertida}"
            return ret
        except IndexError:
            ret = f"{self.id_eivg}\t{self.origen}\t{self.ruc}\t{self.iniciales_reporte}\t{self.estado}\t" \
                  f"{self.fiscalia_reporte}\t{self.entrevistadores}\t{self.ruta_carpeta}\t" \
                  f"{self.fiscalia_repositorio}\t{self.nombre_carpeta}\t{self.carpeta_completa}\t" \
                  f"{self.nombre_correcto}\t{self.fecha_carpeta}\t{self.iniciales_carpeta}" \
                  f"\tERROR\tERROR\t{self.convertida}"
            return ret