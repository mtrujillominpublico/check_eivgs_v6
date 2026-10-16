from listaeivgs_v5 import ListaEivgs

if __name__ == "__main__":
    eivgs = ListaEivgs()
    output = open("/var/www/html/habilitaEIV/proceso/lista_eivgs.csv", "w")
    output.write(str(eivgs))
    output.close()
