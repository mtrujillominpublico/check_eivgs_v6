from datetime import datetime, timedelta
import time
from glob import glob
from re import compile
from os import stat
from eivg_v5 import Eivg
from lib_datos_ruc_v5 import get_datos_ruc
from ProgressBar_v5 import progress_bar


PLAZO_CARPETA = datetime.now() - timedelta(days=365*2)
PLAZO_CAUSA = datetime.now() - timedelta(days=365*2)

class ListaEivgs:
    def __init__(self):
        self.lista_eivgs = dict()
        print("Cargando Datos REPOSITORIO...")
        self.carga_datos_repositorio()
        # self.carga_datos_convertidas()
        print("Cargando Datos SAF...")
        self.carga_datos_saf()
        print("Cargando Convertidas...")
        self.print_mal_nombradas()
        self.print_ruc_no_existe()
        self.revisar_fiscalias()
        # self.revisar_terminadas()

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
                            convertidas.append((elemento.path[-17:-13], elemento.name))
                    busca_eivgs_convertidas(elemento.path)

        convertidas = []
        busca_eivgs_convertidas("/var/www/html/habilitaEIV/resul_eiv")
        fls = {"PUERTOMONTT": '1001', "OSORNO": '1002', "PUERTOVARAS": '1004', "CASTRO": '1005', "ANCUD": '1007',
               "CALBUCO": '1010', "QUINCHAO": '1011', "QUELLON": '1014', "FUTALEUFU": '1015', "MAULLIN": '1016',
               "RIONEGRO": '1017', "HUALAIHUE": '1018', "SACFI": '1020', 'INTERREGIONALES':'1099'}

        for e in self.lista_eivgs.values():
            if (fls[e.get_fiscalia()], e.get_ruc()) in convertidas:
                e.set_convertida()
            else:
                pass

    def carga_datos_repositorio(self):
        er_carpeta = compile("RUC[_\\s][0-9]{10}-[0-9K][\\s_][A-ZÑÁ(]{3,8}$|[0-9]{10}-[0-9K][\\s_][A-ZÑÁ(]{2,8}$")

        def busca_eivgs_repositorio(path):
            from os import scandir
            try:
                lista = scandir(path)
            except OSError:
                lista = []
                print(f"ERROR LEYENDO RUTA {path}")
            for elemento in lista:
                if elemento.is_dir():
                    # if "2600233174-7" in elemento.path:
                        # pass
                    if not str(elemento.path).endswith("ORIGINAL") and not str(elemento.path).endswith("EDITADO"):
                        rutas_repositorio.append(elemento.path)
                    if "EDITADO" not in str(elemento.path):
                        busca_eivgs_repositorio(elemento.path)

        rutas_repositorio = []
        rutas = [
            "\\\\eivg-x\\EIVGs\\FL-Ancud",
            "\\\\eivg-x\\EIVGs\\FL-Calbuco",
            "\\\\eivg-x\\EIVGs\\FL-Castro",
            "\\\\eivg-x\\EIVGs\\FL-Chaiten",
            "\\\\eivg-x\\EIVGs\\FL-Hualaihue",
            "\\\\eivg-x\\EIVGs\\FL-Maullin",
            "\\\\eivg-x\\EIVGs\\FL-Osorno",
            "\\\\eivg-x\\EIVGs\\FL-PuertoMontt",
            "\\\\eivg-x\\EIVGs\\FL-PuertoVaras",
            "\\\\eivg-x\\EIVGs\\FL-Quellon",
            "\\\\eivg-x\\EIVGs\\FL-Quinchao",
            "\\\\eivg-x\\EIVGs\\FL-RioNegro",
            "\\\\eivg-x\\EIVGs\\INTERREGIONALES" ]
        start_time, total_rutas, idx = time.time(), len(rutas), 0
        for ruta in rutas:
            busca_eivgs_repositorio(ruta)
            idx += 1
            txt_prog_causa = f"\rRUTAS FISCALIAS({idx}/{total_rutas}):{progress_bar(start_time, idx, total_rutas)}"
            print(txt_prog_causa, end='')
        print()
        start_time, total_rutas, idx = time.time(), len(rutas_repositorio), 0
        for ruta in rutas_repositorio:
            idx += 1
            txt_prog_causa = f"\rRUTAS EIVGs({idx}/{total_rutas}):{progress_bar(start_time, idx, total_rutas)}"
            print(txt_prog_causa, end='')
            nombre_carpeta = str(ruta).split('\\')[-1]
            if "INTERREGIONALES" in ruta:
                fiscalia_carpeta = str(ruta).split('\\')[-2].upper()
            else:
                fiscalia_carpeta = str(ruta).split('\\')[-3][3:].upper()
            if fiscalia_carpeta == 'CHAITEN':
                fiscalia_carpeta = 'FUTALEUFU'
            # if fiscalia_carpeta == 'GINAL':
                # pass
            # Carpetas incompletas
            carpeta_completa = True
            archivos_video = glob(ruta+'\\*.mp4') + glob(ruta+'\\*.avi')
            duracion = 0
            if len(archivos_video) < 2:
                carpeta_completa = False
            else:
                pass
            # Carpetas mal nombradas
            nombre_correcto = True
            if not bool(er_carpeta.match(nombre_carpeta)):
                nombre_correcto = False
            # Fecha carpeta
            fecha_carpeta = datetime.utcfromtimestamp(stat(ruta).st_ctime)
            if fecha_carpeta.date() == datetime.utcnow().date():
                continue
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
                                             iniciales_carpeta=nombre_carpeta[pos_guion + 3:], duracion_videos=duracion)
        print()

    def carga_datos_saf(self):
        start_time, total_items = time.time(), len(self.lista_eivgs)
        for idx, e in enumerate(self.lista_eivgs.values(), start=1):
            if e.origen == 'REPOSITORIO' or (e.fecha_carpeta is not None and e.fecha_carpeta <= PLAZO_CARPETA):
                e.agrega_datos_saf(get_datos_ruc(e.ruc))
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
            if e.origen == 'REPOSITORIO' and len(e.datos_saf) > 0 and e.get_region() == 10:
                iniciales_saf = []
                for dr in e.datos_saf:
                    nombre_completo = dr[1].split() if dr[1] else []
                    iniciales_nombre = ''
                    for parte in nombre_completo:
                        iniciales_nombre += parte[0]
                    iniciales_saf.append(iniciales_nombre)
                if e.iniciales_carpeta not in iniciales_saf:
                    print(f"x INICIALES: {str(e.ruta_carpeta)}\t POSIBLES:{iniciales_saf}")

    def revisar_fiscalias(self):
        lista_ordenada = sorted(self.lista_eivgs.values(), key=lambda x: x.get_region())
        # r = lambda p: '\\\\eivg-x\\EIVG-' + p.split('/var/www/html/habilitaEIV/origen_eiv/')[1].replace('/', '\\')
        for e in lista_ordenada:
            if e.fiscalia_repositorio != e.fiscalia_reporte and e.fiscalia_repositorio is not None:
                if e.fiscalia_reporte is not None:
                    print(f"MOVER EIVG:\t{e.fiscalia_repositorio} => {e.fiscalia_reporte}\t{e.ruta_carpeta}")
                    e.set_estado("SE DEBE MOVER")
                elif len(e.datos_saf) > 0:
                    fiscalia_saf = e.datos_saf[0][2] or ''
                    reemplazos = [[' ', ''], ['Ó', 'O'], ['Í', 'I'], ['Ú', 'U']]
                    for reemplazo in reemplazos:
                        fiscalia_saf = fiscalia_saf.replace(reemplazo[0], reemplazo[1])
                    if e.fiscalia_repositorio != fiscalia_saf and (e.fiscalia_repositorio != 'INTERREGIONALES' and fiscalia_saf != 'OTRAREGION'):
                        print(f"MOVER EIVG:\t{e.fiscalia_repositorio} => {str(fiscalia_saf)}({e.datos_saf[0][3]})\t{e.ruta_carpeta}")
                    e.set_estado("SE DEBE MOVER")

    def revisar_terminadas(self):
        for e in self.lista_eivgs.values():
            if len(e.datos_saf) > 0:
                for ds in e.datos_saf:
                    if (ds[5] == 'TERMINADO' and e.fecha_carpeta <= PLAZO_CARPETA and
                            datetime.strptime(ds[6], '%Y-%m-%d') <= PLAZO_CAUSA):
                        print(f"TERMINADA:\t{e.fiscalia_repositorio}\t{e.ruta_carpeta}\t"
                              f"{e.fecha_carpeta.strftime('%Y-%m-%d')}")
