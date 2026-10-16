import paramiko

def copy_file_from_linux(hostname, port, username, password, remote_filepath, local_filepath):
    # Crear una instancia del cliente SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectarse al servidor
        client.connect(hostname, port, username, password)

        # Usar SFTP para transferir archivos
        sftp = client.open_sftp()
        sftp.get(remote_filepath, local_filepath)
        sftp.close()
        print(f"Archivo copiado con éxito a {local_filepath}")
    except Exception as e:
        print(f"Error al copiar el archivo: {e}")
    finally:
        client.close()

# Datos del servidor y archivos
hostname = '172.17.163.19'
port = 22  # Puerto SSH típico
username = 'root'
password = 'Desa.2023!'
remote_filepath = '/var/www/html/habilitaEIV/application/logs/log-2024-06-19.php'
local_filepath = 'C:\\Users\\mtrujillo\\Desktop\\temp.csv'

# Llamar a la función
copy_file_from_linux(hostname, port, username, password, remote_filepath, local_filepath)
