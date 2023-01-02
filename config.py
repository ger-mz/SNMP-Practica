from telnetlib import Telnet
from ftplib import FTP
from time import sleep
from os import system

HOST, user, password = '30.30.30.1', 'rcp', 'rcp'

def uploadFile():
    global HOST, user, password
    filename = input("\ningresa el nombre del archivo: ").strip()

    with FTP(HOST, user, password) as ftp:
        with open(filename, 'rb') as fp:
            ftp.storbinary('STOR '+filename, fp)
    
    print(f'\nArchivo {filename} subido al servidor')

def extractConfigFile():
    global HOST, user, password
    mostarDirectorio()

    filename = input("\ningresa el nombre del archivo: ").strip()

    with FTP(HOST, user, password) as ftp:
        with open(filename, 'wb') as fp:
            ftp.retrbinary('RETR '+filename, fp.write)
    
    print(f'\nArchivo {filename} descargado')

def mostarDirectorio():
    # HOST = '30.30.30.1'
    # user = 'rcp'
    # password = 'rcp'
    global HOST, user, password

    with FTP(HOST, user, password) as ftp:
        print("\nLos archivos en el directorio son: \n")
        ftp.dir()

def telnetConfigFile():
    global HOST, user, password
    # password = getpass.getpass()
    # print('\n','pass: ',password, ' ', type(password))
    # https://youtube.com/shorts/MEmV1FTk_YE?feature=share
    
    with Telnet(HOST) as tn:
        tn.read_until(b"User: ")
        tn.write(user.encode('ascii') + b"\n")
        # if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")

        tn.write(b"ena\n")
        tn.write(b"conf\n")

        tn.write(b"copy run start\n")

        tn.write(b"exit\n")
        tn.write(b"exit\n")
        sleep(0.5)
        print(tn.read_very_eager().decode('ascii'))
    
    print('\n','El archivo de configuracion ha sido creado','\n')


def iniciarTap0():
    usr = input('Ingresa el Usuario, ingresa \"0\" para la configuracion por default: ')

    ip = '30.30.30.2/24'
    gw = '30.30.30.1'
    nt = '255.255.255.0'
    net = '30.30.30.0'

    if int(usr) != 0:
        ip = input('Ingresa la IP de la interfaz Tap0: ')
        gw = input('Ingresa el GateWay de la red: ')
        nt = input('Ingresa la netmask de la red: ')
        net = input('Ingresa la ip global de la red: ')
    else :
        usr = 'ger'
    
    system(f'sudo tunctl -u {usr}')
    system(f'sudo ifconfig tap0 {ip} up')
    system(f'sudo route add -net {net} netmask {nt} gw {gw} dev tap0')

    return
