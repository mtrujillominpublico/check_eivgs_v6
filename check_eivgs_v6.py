from listaeivgs_v6 import ListaEivgs

RUTA_CSV = "/var/www/html/habilitaEIV/proceso/lista_eivgs.csv"

if __name__ == "__main__":
    with open(RUTA_CSV, "w") as salida:
        salida.write(str(ListaEivgs()))
