from ipaddress import IPv4Address
from jinja2 import Template
import pandas as pd
from os import system
from os.path import exists
from datetime import datetime

def convertir_excel_csv(filename,l):

    filename_csv = filename.replace('xlsx','csv')
    csv_existe = exists(filename_csv)

    if csv_existe:

        response = f'{filename_csv} ya existe no es necesario convertir'

    else:

        file_xl = pd.read_excel (filename)
        file_xl.to_csv (filename_csv, index = None, header=True)
        response = f'Archivo {filename_csv} creado'

    l.write(f'{datetime.now()}: {response} \n')

    return filename_csv


def subnetting_sitio(subnet_sitio,l):

    subnet = IPv4Address(subnet_sitio)
    ips_sitio = dict()

    ips_sitio['mgmt_ip'] = subnet + 254
    ips_sitio['datos_ip'] = subnet + 1
    ips_sitio['voz_ip'] = subnet + 129

    response = f'Subnetting para {subnet_sitio} completo'

    l.write(f'{datetime.now()}: {response} \n')

    return ips_sitio


def crear_valores_jinja(line,ips_sitio, l):

    valores = {
    "HOSTNAME": line[0] + line[1] + 'RTR' + line[3],
    "IP_MGMT": ips_sitio['mgmt_ip'],
    "IP_DATOS": ips_sitio['datos_ip'],
    "REGION": line[2],
    "SUBRED_SITIO" : line[4],
    "DATA_HELPER" : ['172.18.25.1','172.18.26.2','172.18.27.3'],
    "IP_SYSLOG_N": '192.168.10.254',
    "IP_SYSLOG_S": '192.168.33.1',
    }

    response = f'Diccionario de valores para sitio ID: {line[3]} completo'
    l.write(f'{datetime.now()}: {response} \n')

    return valores


def crear_jinja_data(plantilla,valores,l):
    
    with open(plantilla,'r') as j:
        j2_plantilla = Template(j.read())
        jinja_data = j2_plantilla.render(valores)

    response = f'Config para router {valores["HOSTNAME"]} creada'
    l.write(f'{datetime.now()}: {response} \n')

    return jinja_data


def crear_archivo_config(valores,jinja_data,l):
    
    archivo = valores['HOSTNAME'] + '.txt'

    with open(f'configs/{archivo}', 'w') as f:
        for line in jinja_data:
            f.write(line)

    response = f'Archivo {archivo} creado'
    l.write(f'{datetime.now()}: {response} \n')


def main():

    inicio_dt = datetime.now()
    log_dt = inicio_dt.strftime('%m%d%Y_%H%M%S')

    if not exists('logs'):
            system('mkdir logs')
    
    with open(f'logs/crear_configs_{log_dt}.log','w') as l:

        l.write(f'{inicio_dt}: Comenzando tarea! \n')

        if not exists('configs'):
            system('mkdir configs')
            l.write(f'{datetime.now()}: Directorio "configs" creado\n')

        archivo_csv = convertir_excel_csv('docs/Direccionamiento_Sucursales.xlsx',l)

        with open(archivo_csv) as d:
            
                for row in d:
                    clean_row = row.replace('\n','')
                    line = clean_row.split(',')
                    if line[0] != 'PAIS':
                        
                        try:
                            ips_sitio = subnetting_sitio(line[4],l)
                            valores = crear_valores_jinja(line,ips_sitio,l)
                            jinja_data = crear_jinja_data('docs/plantilla_config.j2',valores,l)
                            crear_archivo_config(valores,jinja_data,l)

                        except:
                            l.write(f'{datetime.now()}: *** ERROR ***\n')
                            print(f'ADVERTENCIA! Problemas en linea: {line}')

        final_dt = datetime.now()
        delta = final_dt -inicio_dt
        l.write(f'{final_dt}: Tiempo de ejecucion: {delta}\n')

    print('Trabajo Finalizado!')


if __name__ == '__main__':
    main()
