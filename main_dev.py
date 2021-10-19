from ipaddress import IPv4Address
from jinja2 import Template
import pandas as pd
from os.path import exists


def convertir_excel_csv(filename):

    filename_csv = filename.replace('xlsx','csv')
    csv_existe = exists(filename_csv)

    if not csv_existe:
    
        file_xl = pd.read_excel (filename)
        file_xl.to_csv (filename_csv, index = None, header=True)

    return filename_csv


def subnetting_sitio(subnet_sitio):

    subnet = IPv4Address(subnet_sitio)
    ips_sitio = dict()

    ips_sitio['mgmt_ip'] = subnet + 254
    ips_sitio['datos_ip'] = subnet + 1

    return ips_sitio


def crear_valores_jinja(line,ips_sitio):

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

    return valores


def crear_jinja_data(plantilla,valores):
    
    with open(plantilla,'r') as j:
        j2_plantilla = Template(j.read())
        jinja_data = j2_plantilla.render(valores)

    return jinja_data


def crear_archivo_config(valores,jinja_data):
    
    archivo = valores['HOSTNAME'] + '.txt'
    
    with open(f'configs/{archivo}', 'w') as f:
        for line in jinja_data:
            f.write(line)


def main():

    archivo_csv = convertir_excel_csv('docs/Direccionamiento_Sucursales.xlsx')

    with open(archivo_csv) as d:
        
            for row in d:
                clean_row = row.replace('\n','')
                line = clean_row.split(',')
                
                if line[0] != 'PAIS':
                    
                    try:
                        ips_sitio = subnetting_sitio(line[4])
                        valores = crear_valores_jinja(line,ips_sitio)
                        jinja_data = crear_jinja_data('docs/plantilla_config.j2',valores)
                        crear_archivo_config(valores,jinja_data)

                    except:
                        print(f'ADVERTENCIA! Problemas en linea: {line}')

    print('Trabajo Finalizado!')

if __name__ == '__main__':
    main()