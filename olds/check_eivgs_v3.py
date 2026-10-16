from datetime import datetime, timedelta
from cx_Oracle import connect
from ProgressBar import progress_bar
# from moviepy.editor import VideoFileClip
# import sys

PLAZO_CARPETA = datetime.now() - timedelta(days=365*2)
PLAZO_CAUSA = datetime.now() - timedelta(days=365*2)


# class Printer:
#     def __init__(self, data):
#         sys.stdout.write("\r\x1b[K"+str(data))
#         sys.stdout.flush()

def get_datos_ruc(ruc, database):
    """
    :param ruc: str(12)
    :param database: base de datos
    :return: datos_ruc[]
        0: RUC; 1: NOMBRE VICTIMA; 2: FISCALIA; 3: REGION; 4: TRANSFERENCIAS; 5:ESTADO; 6:F_TERMINO
    """
    sql = f"SELECT DISTINCT IDF_ROLUNICO RUC, " \
          f"    TRIM(P.IDF_NOMBRES)||' '||TRIM(P.IDF_PATERNO)||' '||TRIM(P.IDF_MATERNO) NOMBRE," \
          f"    TRIM(F.GLS_DESCFISCALIA) FISCALIA, F.COD_REGION, " \
          f"    (SELECT COUNT(1) FROM MINPROD.TASG_ASIGNACION A " \
          f"        WHERE A.TIP_ASIGNACION=5 AND A.CRR_CASO=C.CRR_IDCASO) TRANSFERENCIAS, " \
          f"    E.GLS_ESTCASO ESTADO, C.FEC_CAMBIOEST F_TERMINO " \
          f"FROM MINPROD.TATP_CASO C, MINPROD.TATP_SUJETO S, MINPROD.TATP_PERSONA P, " \
          f"    MINPROD.TATP_FISCALIA F, MINPROD.TG_ESTCASO E " \
          f"WHERE C.CRR_IDCASO=S.CRR_CASO AND S.CRR_PERSONA=P.CRR_IDPERSONA AND E.EST_CASO = C.EST_CASO " \
          f"AND C.COD_FISCALIA = F.COD_FISCALIA AND S.TIP_SUJETO IN (6,15) AND C.IDF_ROLUNICO = '{ruc}'"
    res = database.query(sql)
    return res


class Oracle:
    def __init__(self):
        self.con = connect('REGIONX_INFO_2', '7ED098E18D', '172.18.1.145/safstby', encoding='UTF-8')
        self.cur = self.con.cursor()

    def query(self, sql):
        self.cur.execute(sql)
        resultado = self.cur.fetchall()
        return resultado

    def cerrar(self):
        del self.cur
        self.con.close()


class Eivg:
    def __init__(self, id_eivg, origen, ruc, iniciales_reporte, estado, fiscalia_reporte, entrevistadores, ruta_carpeta,
                 fiscalia_repositorio, nombre_carpeta, carpeta_completa, nombre_correcto, fecha_carpeta,
                 iniciales_carpeta, duracion_videos, db):
        self.id_eivg = id_eivg
        self.origen = origen
        self.ruc = ruc
        self.db = db
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
            print(f"EIVG Repetida:\tPrimera:{self.ruta_carpeta}\n"
                  f"\t\t\t\tRepetición:{ruta_carpeta}\n"
                  f"\t\t\t\tFiscalía actual:{get_datos_ruc(self.ruc, self.db)[0][2]}")

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
            return self.datos_saf[0][3]

    def get_ruc(self):
        return self.ruc

    def set_convertida(self):
        self.convertida = True

    def __str__(self):
        try:
            ret = f"{self.id_eivg}\t{self.origen}\t{self.ruc}\t{self.iniciales_reporte}\t{self.estado}\t" \
                  f"{self.fiscalia_reporte}\t{self.entrevistadores}\t{self.ruta_carpeta}\t{self.fiscalia_repositorio}\t" \
                  f"{self.nombre_carpeta}\t{self.carpeta_completa}\t{self.nombre_correcto}\t{self.fecha_carpeta}\t" \
                  f"{self.iniciales_carpeta}\t{self.datos_saf[0][2]}\t{self.datos_saf[0][5]}\t{self.convertida}"
            return ret
        except IndexError:
            ret = f"{self.id_eivg}\t{self.origen}\t{self.ruc}\t{self.iniciales_reporte}\t{self.estado}\t" \
                  f"{self.fiscalia_reporte}\t{self.entrevistadores}\t{self.ruta_carpeta}\t{self.fiscalia_repositorio}\t" \
                  f"{self.nombre_carpeta}\t{self.carpeta_completa}\t{self.nombre_correcto}\t{self.fecha_carpeta}\t" \
                  f"{self.iniciales_carpeta}\tERROR\tERROR\t{self.convertida}"
            return ret


class ListaEivgs:
    def __init__(self, db):
        self.db = db
        self.lista_eivgs = dict()
        print("Cargando Datos REPOSITORIO...")
        self.carga_datos_repositorio(self.db)
        print("Cargando Datos SAF...")
        self.carga_datos_saf(self.db)
        print("Cargando Convertidas...")
        self.carga_datos_convertidas()
        self.print_mal_nombradas()
        self.print_ruc_no_existe()
        # self.print_incompletas()
        # self.revisar_iniciales()
        self.revisar_fiscalias()
        self.revisar_terminadas()

    def __str__(self):
        rt = ("id_eivg\torigen\truc\tiniciales_reporte\testado\tfiscalia_reporte\tentrevistadores\truta_carpeta"
              "\tfiscalia_carpeta\tnombre_carpeta\tcarpeta_completa\tnombre_correcto\tfecha_carpeta"
              "\tiniciales_carpeta\tfiscalia\testado\tconvertida\n")
        for e in self.lista_eivgs.values():
            rt += str(e)+"\n"
        return rt

    def get_values(self):
        return self.lista_eivgs.values()

    def carga_datos_convertidas(self):
        from re import compile
        er_ruc = compile("[0-9]{10}-[0-9K]$")

        def busca_eivgs_convertidas(path):
            from os import scandir, listdir
            try:
                lista = scandir(path)
            except OSError:
                lista = []
                print(f"ERROR LEYENDO RUTA {path}")
            for elemento in lista:
                if elemento.is_dir():
                    if bool(er_ruc.match(elemento.name)):
                        if listdir(elemento.path):
                            convertidas.append(elemento.name)
                    busca_eivgs_convertidas(elemento.path)

        convertidas=[]
        busca_eivgs_convertidas("\\\\eivg-x\\EIVG-VISUALIZACIONES\\VISUALIZACIONES")
        for e in self.lista_eivgs.values():
            if e.get_ruc() in convertidas:
                e.set_convertida()

    def carga_datos_repositorio(self, db):
        from glob import glob
        from re import compile
        from os import stat
        er_carpeta = compile("RUC[_\\s][0-9]{10}-[0-9K][\\s_][A-ZÑÁ(]{2,8}$|[0-9]{10}-[0-9K][\\s_][A-ZÑÁ(]{2,8}$")

        def busca_eivgs_repositorio(path):
            from os import scandir
            try:
                lista = scandir(path)
            except OSError:
                lista = []
                print(f"ERROR LEYENDO RUTA {path}")
            for elemento in lista:
                if elemento.is_dir():
                    if not str(elemento.path).endswith("ORIGINAL") and not str(elemento.path).endswith("EDITADO"):
                        rutas_repositorio.append(elemento.path)
                    if "EDITADO" not in str(elemento.path):
                        busca_eivgs_repositorio(elemento.path)

        rutas_repositorio = []
        rutas = ['\\\\eivg-x\\EIVG-FL-Ancud', '\\\\eivg-x\\EIVG-FL-Calbuco', '\\\\eivg-x\\EIVG-FL-Castro',
                 '\\\\eivg-x\\EIVG-FL-Hualaihue', '\\\\eivg-x\\EIVG-FL-Maullin', '\\\\eivg-x\\EIVG-FL-Osorno',
                 '\\\\eivg-x\\EIVG-FL-PuertoMontt', '\\\\eivg-x\\EIVG-FL-PuertoVaras', '\\\\eivg-x\\EIVG-FL-Quellon',
                 '\\\\eivg-x\\EIVG-FL-RioNegro', '\\\\eivg-x\\EIVG-FL-Chaiten', '\\\\eivg-x\\EIVG-FL-Quinchao']
        # rutas = ['\\\\eivg-x\\EIVG-FL-Chaiten']
        for ruta in rutas:
            busca_eivgs_repositorio(ruta)
        for ruta in rutas_repositorio:
            nombre_carpeta = str(ruta).split('\\')[5]
            fiscalia_carpeta = str(ruta).split('\\')[3][8:].upper()
            if fiscalia_carpeta == 'CHAITEN':
                fiscalia_carpeta = 'FUTALEUFU'
            # Carpetas incompletas
            carpeta_completa = True
            archivos_video = glob(ruta+'\\*.mp4') + glob(ruta+'\\*.avi')
            duracion = 0
            if len(archivos_video) < 2:
                carpeta_completa = False
            else:
                pass
                # codigo para determinar duracion de videos COMENTADO por que demora mucho
                # for video in archivos_video:
                    # vid = VideoFileClip(video)
                    # duracion += vid.duration
            # Carpetas mal nombradas
            nombre_correcto = True
            if not bool(er_carpeta.match(nombre_carpeta)):
                nombre_correcto = False
            # Fecha carpeta
            fecha_carpeta = datetime.utcfromtimestamp(stat(ruta).st_ctime)
            pos_guion = nombre_carpeta.find('-')
            ruc = nombre_carpeta[pos_guion - 10:pos_guion + 2]
            key = ruc + nombre_carpeta[pos_guion + 3:]
            if key in self.lista_eivgs.keys():
                self.lista_eivgs[key].agrega_datos_carpeta(ruta_carpeta=ruta, fiscalia_carpeta=fiscalia_carpeta,
                                                           nombre_carpeta=nombre_carpeta,
                                                           carpeta_completa=carpeta_completa,
                                                           nombre_correcto=nombre_correcto,
                                                           fecha_carpeta=fecha_carpeta,
                                                           iniciales_carpeta=nombre_carpeta[pos_guion + 3:],
                                                           duracion_videos=duracion)
            else:
                self.lista_eivgs[key] = Eivg(id_eivg=key, origen='REPOSITORIO', ruc=ruc, iniciales_reporte=None,
                                             estado=None, fiscalia_reporte=None, entrevistadores=None,
                                             ruta_carpeta=ruta, fiscalia_repositorio=fiscalia_carpeta,
                                             nombre_carpeta=nombre_carpeta, carpeta_completa=carpeta_completa,
                                             nombre_correcto=nombre_correcto, fecha_carpeta=fecha_carpeta,
                                             iniciales_carpeta=nombre_carpeta[pos_guion + 3:], duracion_videos=duracion,
                                             db=db)

    def carga_datos_saf(self, db):
        import time
        total_items = len(self.lista_eivgs)
        average_time_per_cycle = 0  # Promedio acumulado del tiempo por ciclo
        start_time = time.time()
        for idx, e in enumerate(self.lista_eivgs.values(), start=1):
            if e.origen == 'REPOSITORIO' or (e.fecha_carpeta is not None and e.fecha_carpeta <= PLAZO_CARPETA):
                e.agrega_datos_saf(get_datos_ruc(e.ruc, db))
            txt_prog_causa = f"\rEIVGs({idx}/{total_items}):{progress_bar(start_time, idx, total_items)}"
            print(txt_prog_causa, end='')
        print()

    def print_mal_nombradas(self):
        for e in self.lista_eivgs.values():
            if e.nombre_correcto is not None and not e.nombre_correcto:
                print(f"NOMBRE INCORRECTO: {str(e.ruta_carpeta)}")

    def print_ruc_no_existe(self):
        for e in self.lista_eivgs.values():
            if e.origen == 'REPOSITORIO' and len(e.datos_saf) == 0:
                print(f"RUC NO EXISTE: {str(e.ruta_carpeta)}")

    def print_incompletas(self):
        for e in self.lista_eivgs.values():
            if e.carpeta_completa is not None and not e.carpeta_completa:
                print(f"INCOMPLETA: {str(e.ruta_carpeta)}")

    def revisar_iniciales(self):
        for e in self.lista_eivgs.values():
            if e.origen == 'REPOSITORIO' and len(e.datos_saf) > 0:
                iniciales_saf = []
                for dr in e.datos_saf:
                    nombre_completo = dr[1].split()
                    iniciales_nombre = ''
                    for parte in nombre_completo:
                        iniciales_nombre += parte[0]
                    iniciales_saf.append(iniciales_nombre)
                if e.iniciales_carpeta not in iniciales_saf:
                    print(f"x INICIALES: {str(e.ruta_carpeta)}\t POSIBLES:{iniciales_saf}")

    def revisar_fiscalias(self):
        lista_ordenada = sorted(self.lista_eivgs.values(), key=lambda x: x.get_region())
        for e in lista_ordenada:
            if e.fiscalia_repositorio != e.fiscalia_reporte and e.fiscalia_repositorio is not None:
                if e.fiscalia_reporte is not None:
                    print(f"MOVER EIVG:\t{e.fiscalia_repositorio} => {e.fiscalia_reporte}\t{e.ruta_carpeta}")
                    e.set_estado("SE DEBE MOVER")
                elif len(e.datos_saf) > 0:
                    fiscalia_saf, reemplazos = e.datos_saf[0][2], [[' ', ''], ['Ó', 'O'], ['Í', 'I'], ['Ú', 'U']]
                    for reemplazo in reemplazos:
                        fiscalia_saf = fiscalia_saf.replace(reemplazo[0], reemplazo[1])
                    if e.fiscalia_repositorio != fiscalia_saf:
                        print(f"MOVER EIVG:\t{e.fiscalia_repositorio} => {str(fiscalia_saf)}({e.datos_saf[0][3]})"
                              f"\t{e.ruta_carpeta}")
                    e.set_estado("SE DEBE MOVER")


    def revisar_terminadas(self):
        for e in self.lista_eivgs.values():
            if len(e.datos_saf) > 0:
                for ds in e.datos_saf:
                    if ds[5] == 'TERMINADO' and e.fecha_carpeta <= PLAZO_CARPETA and ds[6] <= PLAZO_CAUSA:
                        print(f"TERMINADA:\t{e.fiscalia_repositorio}\t{e.ruta_carpeta}\t"
                              f"{e.fecha_carpeta.strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    bd = Oracle()
    eivgs = ListaEivgs(bd)
    bd.cerrar()
    output = open("lista_eivgs.csv","w")
    output.write(str(eivgs))
    output.close()
