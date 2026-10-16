import os
import datetime


def scan_directories(root_path):
    # Obtener el año actual
    current_year = datetime.datetime.now().year

    # Lista para almacenar las rutas de las carpetas que contienen archivos de este año
    directories_with_current_year_files = []

    # Caminar por todos los directorios y archivos en la ruta proporcionada
    for subdir, dirs, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(subdir, file)
            # Obtener la fecha de última modificación del archivo
            file_mod_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            # Verificar si el archivo fue modificado este año
            if file_mod_time.year == current_year:
                if subdir not in directories_with_current_year_files:
                    directories_with_current_year_files.append(subdir)
                break  # Ya que encontramos un archivo de este año, no necesitamos revisar más archivos en esta carpeta

    return directories_with_current_year_files


# Usar la función en una ruta específica
path_to_scan = "\\\\eivg-x\\EIVGs\\"
folders = scan_directories(path_to_scan)
print("Carpetas que contienen archivos modificados este año:")
i=0
for folder in folders:
    i += 1
    print(i, folder)
