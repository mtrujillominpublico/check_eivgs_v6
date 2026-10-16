import os


def encontrar_carpetas_vacias(ruta):
    carpetas_vacias = []

    # Recorre todos los directorios y subdirectorios
    for directorio_actual, subdirectorios, archivos in os.walk(ruta):
        # Comprueba si el directorio actual está vacío
        if not subdirectorios and not archivos:
            carpetas_vacias.append(directorio_actual)

    return carpetas_vacias


# Ejemplo de uso:
ruta_base = '\\\\eivg-x\\EIVG-VISUALIZACIONES\\VISUALIZACIONES'
carpetas_vacias_encontradas = encontrar_carpetas_vacias(ruta_base)

if carpetas_vacias_encontradas:
    print("Carpetas vacías encontradas:")
    for carpeta in carpetas_vacias_encontradas:
        acarpeta = carpeta.split('\\')
        print(f"php /var/www/html/habilitaEIV/index.php HabilitaEIVLNX HabilitaRuc eiv-x Minpub.24 {acarpeta[6]} {acarpeta[5]}")
else:
    print("No se encontraron carpetas vacías en la ruta especificada.")