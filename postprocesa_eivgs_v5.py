from datetime import datetime
import pandas as pd
import os

def postprocesa_lista_eivgs():
    df = pd.read_csv("/var/www/html/habilitaEIV/proceso/lista_eivgs.csv", sep="\t")
    df = df.drop(columns=["origen", "iniciales_reporte", "estado", "fiscalia_reporte", "entrevistadores", "nombre_carpeta", "carpeta_completa", "nombre_correcto", "id_eivg", "ruta_carpeta", "fiscalia_carpeta", "iniciales_carpeta"])
    df = df.rename(columns={"estado.1": "estado_causa"}) if "estado.1" in df.columns else df
    cods = {"PUERTO MONTT":1001,"OSORNO":1002,"PUERTO VARAS":1004,"CASTRO":1005,"ANCUD":1007,"CALBUCO":1010,"QUINCHAO":1011,"QUELLÓN":1014,"FUTALEUFÚ":1015,"MAULLÍN":1016,"RIO NEGRO":1017,"HUALAIHUE":1018}
    df["cod_fiscalia"] = df["fiscalia"].map(cods)
    df["convertida"] = df["convertida"].astype(str)
    df = df[(df["estado_causa"].astype(str).str.strip() == "VIGENTE") &(df["cod_fiscalia"].notnull()) &(df["convertida"].str.strip() == "False")]
    df["cod_fiscalia"] = df["cod_fiscalia"].astype(int).astype(str)
    df = df.drop_duplicates(subset=["ruc"])
    df = df.sort_values(by="fecha_carpeta", ascending=False)
    df["Comando PHP 2"] = "php /var/www/html/habilitaEIV/index.php HabilitaEIVLNX HabilitaRuc eiv-x Minpub.24 " + df["ruc"] + " " + df["cod_fiscalia"] + " "
    hoy = datetime.now().strftime("%Y-%m-%d")
    path = f"/var/www/html/habilitaEIV/proceso/conversiones_{hoy}.sh"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(df["Comando PHP 2"]))
    os.chmod(path, 0o755)
    print(path)
    print(open(path).read())
