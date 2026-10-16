from datetime import datetime
import os
from cx_Oracle import *
import re

ER_CARPETA = re.compile("RUC[_\s][0-9]{10}-[0-9K][\s_][A-ZÁ]{3,6}$|[0-9]{10}-[0-9K][\s_][A-ZÑÁ]{3,6}$")


def get_datos_ruc(ruc):
    con = connect('REGIONX_INFO', 'REGIONX_INFO', '172.18.1.145/safstby', encoding='UTF-8')
    cur = con.cursor()
    cur.execute(f"SELECT DISTINCT IDF_ROLUNICO RUC, TRIM(P.IDF_NOMBRES)||' '||TRIM(P.IDF_PATERNO)||' '||TRIM("
                f"P.IDF_MATERNO) NOMBRE, TRIM(F.GLS_DESCFISCALIA) FISCALIA, (SELECT COUNT(1) FROM "
                f"MINPROD.TASG_ASIGNACION A WHERE A.TIP_ASIGNACION = 5 AND A.CRR_CASO=C.CRR_IDCASO) FROM "
                f"MINPROD.TATP_CASO C, MINPROD.TATP_SUJETO S, MINPROD.TATP_PERSONA P, MINPROD.TATP_FISCALIA F WHERE "
                f"C.CRR_IDCASO=S.CRR_CASO AND S.CRR_PERSONA=P.CRR_IDPERSONA AND C.COD_FISCALIA = F.COD_FISCALIA AND "
                f"S.TIP_SUJETO = 6 AND C.IDF_ROLUNICO = '{ruc}'")
    res = cur.fetchall()
    return res


def busca_eivgs(path):
    lista = os.scandir(path)
    for elemento in lista:
        if elemento.is_dir():
            if not str(elemento.path).endswith("ORIGINAL") and not str(elemento.path).endswith("EDITADO"):
                archivos = os.listdir(elemento.path)
                if len(archivos) < 2 and 'EDITADO' not in str(elemento.path):
                    print(f"CARPETA INCOMPLETA:\t{elemento.path}\t{len(archivos)}")
                nombre_carpeta = str(elemento.path).split('\\')[5]
                if not bool(ER_CARPETA.match(nombre_carpeta)):
                    print(f"IDENTIFICAR CARPETA:{elemento.path}\t{nombre_carpeta}")
                else:
                    posicion_guion = nombre_carpeta.find('-')
                    ruc = nombre_carpeta[posicion_guion - 10:posicion_guion + 2]
                    datos_ruc = get_datos_ruc(ruc)
                    if len(datos_ruc) == 0:
                        print(f"RUC NO EXISTE:\t{elemento.path}\t{ruc}")
                    else:
                        if ruc in rutas_buscadas:
                            print(f"\x1b[01;37;44mRUTA BUSCADA: {str(elemento.path)}\x1b[0m")
                        iniciales_ruc = []
                        fiscalia_ruc = []
                        transferencias = datos_ruc[0][3]
                        nombres_ruc = []
                        for datoRuc in datos_ruc:
                            partes = datoRuc[1].split()
                            inic = ''
                            for parte in partes:
                                inic += parte[0]
                            iniciales_ruc.append(inic)
                            if 'L' in inic:
                                pos_l = inic.find('L')
                                inic2 = inic[:pos_l]+'L'+inic[pos_l:]
                                iniciales_ruc.append(inic2)
                            if 'C' in inic:
                                pos_c = inic.find('C')
                                inic2 = inic[:pos_c+1]+'H'+inic[pos_c+1:]
                                iniciales_ruc.append(inic2)
                            reemplazos = [[' ', ''], ['Ó', 'O'], ['Í', 'I'], ['Ú', 'U']]
                            fl = str(datoRuc[2])
                            for reemplazo in reemplazos:
                                fl = fl.replace(reemplazo[0], reemplazo[1])
                            fiscalia_ruc.append(fl)
                            nombres_ruc.append(ruc+partes[0])
                        iniciales_carpeta = nombre_carpeta[posicion_guion + 3:]
                        if iniciales_carpeta not in iniciales_ruc:
                            print(f"CORREGIR INICIALES:\t{elemento.path}\t{iniciales_carpeta}\t{iniciales_ruc}")
                        fiscalia_carpeta = str(elemento.path).split('\\')[3][8:].upper()
                        if fiscalia_carpeta == 'CHAITEN':
                            fiscalia_carpeta = 'FUTALEUFU'
                        if fiscalia_carpeta not in fiscalia_ruc:
                            print(f"MOVER EIVG:\t\t{nombre_carpeta}\t{fiscalia_carpeta} "
                                  f"=> {str(set(fiscalia_ruc))[2:-2]}\t", end='')
                            if transferencias > 0:
                                print(f"({transferencias} TRANSFERENCIAS)")
                            else:
                                print(f"(SIN TRANSFERENCIAS)")
                        else:
                            registrada = False
                            ruc_inic = ruc+iniciales_carpeta
                            if ruc_inic in todas_las_eivg.keys():
                                registrada = True
                            else:
                                for ini in iniciales_ruc:
                                    ruc_ini = ruc+ini
                                    if ruc_ini in todas_las_eivg.keys():
                                        registrada = True
                                        ruc_inic = ruc_ini
                                        break
                            if not registrada:
                                fecha_carpeta = datetime.utcfromtimestamp(os.stat(elemento.path).st_ctime)
                                fecha_inicio = datetime(2022, 10, 3)
                                if fecha_carpeta >= fecha_inicio:
                                    print(f"NO REGISTRADA:\t{nombre_carpeta}\t{fecha_carpeta.strftime('%Y-%m-%d')}")
                            elif todas_las_eivg[ruc_inic] == 'REALIZADA':
                                todas_las_eivg[ruc_inic] = 'ENCONTRADA'
                            elif todas_las_eivg[ruc_inic] == 'ENCONTRADA':
                                pass
                            elif todas_las_eivg[ruc_inic] == 'NO REALIZADA':
                                print(f"NO REALIZADA:\t{nombre_carpeta}\t{str(entrevistadores[ruc])[1:-1]}")
            busca_eivgs(elemento.path)
        else:
            if str(elemento.path)[-4:] not in ['.mp4', '.txt', '.avi', '.pdf', '.ini', 's.db', '.xml']:
                print(f"EXTENSION NO RECONOCIDA:\t{str(elemento.path)[-4:]}\t{str(elemento.path)}")


if __name__ == "__main__":
    rutas_buscadas = ['2200405298-K','2200433343-1','2200459668-8','2200870422-1','2200932939-4','2200947515-3','2200953554-7','2200989470-9','2201005972-4']
    rutas = ['\\\\eivg-x\\EIVG-FL-Ancud', '\\\\eivg-x\\EIVG-FL-Calbuco', '\\\\eivg-x\\EIVG-FL-Castro',
             '\\\\eivg-x\\EIVG-FL-Hualaihue', '\\\\eivg-x\\EIVG-FL-Maullin', '\\\\eivg-x\\EIVG-FL-Osorno',
             '\\\\eivg-x\\EIVG-FL-PuertoMontt', '\\\\eivg-x\\EIVG-FL-PuertoVaras', '\\\\eivg-x\\EIVG-FL-Quellon',
             '\\\\eivg-x\\EIVG-FL-RioNegro', '\\\\eivg-x\\EIVG-FL-Chaiten', '\\\\eivg-x\\EIVG-FL-Quinchao']
    file_todas = open('C:\\Users\\mtrujillo\\PycharmProjects\\check_eivg\\eivgs_realizadas.csv', 'r')
    todas = file_todas.readlines()
    file_todas.close()
    todas_las_eivg = dict()
    entrevistadores = dict()
    for eivg in todas:
        la = str(eivg).split(';')
        ind_entrevistadores = [50, 57, 69, 76, 88, 95, 107, 114]
        eves = set()
        for idx in ind_entrevistadores:
            eves.add(la[idx])
        if '' in eves:
            eves.remove('')
        if len(eves) == 0:
            eves.add('SIN ENTREVISTADORES')
        entrevistadores[la[6]] = eves
        inic = str()
        for i in la[18].split():
            inic = inic + i[0]
        if 'EIVG Realizada' in eivg:
            todas_las_eivg[la[6]+inic] = 'REALIZADA'
        else:
            todas_las_eivg[la[6]+inic] = 'NO REALIZADA'
    for ruta in rutas:
        print(f"\n\x1b[1;37;40m{ruta[14:]}\x1b[0m")
        busca_eivgs(ruta)
    print(f"\nFALTAN:")
    faltan = []
    for eivg in todas_las_eivg.keys():
        if todas_las_eivg[eivg] == 'REALIZADA':
            for e in todas:
                if eivg[0:12] in e:
                    la = e.split(";")
                    faltan.append(la)
                    break
    faltan.sort(key=lambda e: e[3])
    for f in faltan:
        print(f"{f[3]}\t{f[6]}\t{f[18]}")
