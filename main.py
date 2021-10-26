from ipaddress import IPv4Address
from jinja2 import Template
import pandas as pd
from os.path import exists
from os import system
from sys import exit
from datetime import datetime


def convertir_excel_csv(filename,log):

    """
    Funcion para convertir el archivo con la info de los sitios
    de formato xlsx (excel) a formato csv
    """

    filename_csv = filename.replace('xlsx','csv')
    csv_existe = exists(filename_csv)

    if not csv_existe:

        file_xl = pd.read_excel (filename)
        file_xl.to_csv (filename_csv, index = None, header=True)
        log.write(f'{datetime.now()}: Archivo CSV creado\n')

    else:
        log.write(f'{datetime.now()}: Archivo CSV ya existe\n')

    return filename_csv


def subnetting_sitio(subnet_sitio,log):

    """
    Funcion para hacer el subnetting de un sitio
    """

    subnet = IPv4Address(subnet_sitio)
    ips_sitio = dict()

    ips_sitio['mgmt_ip'] = subnet + 254
    ips_sitio['datos_ip'] = subnet + 1

    log.write(f'{datetime.now()}:Subnetting creado\n')

    return ips_sitio


def crear_valores_jinja(line,ips_sitio,log):

    """
    Funcion para crear un diccionario con los valores especificos de un sitio
    """

    valores = {
    "HOSTNAME":line[0] + line[1] + 'RTR' + line[3],
    "IP_MGMT": ips_sitio['mgmt_ip'],
    "IP_DATOS": ips_sitio['datos_ip'],
    "REGION": line[2],
    "SUBRED_SITIO" : line[4],
    "DATA_HELPER" : ['172.18.25.1','172.18.26.2','172.18.27.3'],
    "IP_SYSLOG_N": '192.168.10.254',
    "IP_SYSLOG_S": '192.168.33.1',
    }

    log.write(f'{datetime.now()}:Diccionario de valores creado\n')

    return valores


def crear_jinja_data(plantilla,valores,log):

    """
    Funcion para crear una instancia de la configuracion utilizando la plantilla Jinja
    """

    with open(plantilla,'r') as j:
        j2_plantilla = Template(j.read())
        jinja_data = j2_plantilla.render(valores)

    log.write(f'{datetime.now()}:Plantilla Jinja creada\n')

    return jinja_data


def crear_archivo_config(valores,jinja_data,log):

    """
    Funcion para guardar la instancia de configuracion en un archivo TXT
    """

    archivo = valores['HOSTNAME'] + '.txt'

    with open(f'configs/{archivo}', 'w') as f:
        for line in jinja_data:
            f.write(line)

    log.write(f'{datetime.now()}:Archivo TXT creado\n')


def main():

    """
    Funcion para ejecutar todas las demas funciones
    """

    inicio = datetime.now()
    log_str = inicio.strftime('%Y%m%d_%H%M%S')
    archivo_log = f'log_configs_{log_str}.log'

    if not exists('logs'):
            system('mkdir logs')

    if not exists('configs'):
            system('mkdir configs')

    with open(f'logs/{archivo_log}','w') as log:

        log.write(f'{datetime.now()}: Iniciando ejecucion del programa\n')

        try:

            archivo_csv = convertir_excel_csv('docs/Direccionamiento_Sucursales.xlsx',log)


        except FileNotFoundError:

            print(f'ERROR! No se encontro la base de datos ni en formato xlsx ni en csv')
            exit(0)

        with open(archivo_csv) as d:

                for row in d:
                    clean_row = row.replace('\n','')
                    line = clean_row.split(',')

                    if line[0] != 'PAIS':

                        log.write(f'{datetime.now()}: Trabajando en la linea: {line}\n')

                        try:
                            ips_sitio = subnetting_sitio(line[4],log)
                            valores = crear_valores_jinja(line,ips_sitio,log)
                            jinja_data = crear_jinja_data('docs/plantilla_config.j2',valores,log)
                            crear_archivo_config(valores,jinja_data,log)

                        except:
                            print(f'ERROR! Problemas en linea: {line}')
                            log.write(f'{datetime.now()}: ERROR! Problemas en linea: {line}\n')

        final = datetime.now()
        delta = final - inicio

        log.write(f'{datetime.now()}: Tiempo de ejecucion - {delta}\n')
        log.write(f'{datetime.now()}: Trabajo Finalizado!\n')
        print('Trabajo Finalizado!')

if __name__ == '__main__':

    main()
