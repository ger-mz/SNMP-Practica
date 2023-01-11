from telnetlib import Telnet
from ftplib import FTP
from time import sleep
from os import system

HOST1, user, password, HOST2 = '30.30.30.1', 'rcp', 'rcp', '192.168.1.2'
op = -1

def selectIP():
    global op
    while True:
        print("Selecciona un router: ")
        print("1.",HOST1)
        print("2.",HOST2)

        op = int(input("Ingresa una opccion: "))
        if(op == 1 or op == 2):
            break
    

def uploadFile():
    global HOST1, user, password, HOST2
    selectIP()
    HOST = HOST1 if op == 1 else HOST2

    filename = input("\nIngresa el nombre del archivo: ").strip()
    newname = input("Ingresa el nuevo nombre, -1 minsmo nombre, 0 nombre por default: ").strip()
    newname = filename if newname == "-1" else 'startup-config' if newname == "0" else newname

    with FTP(HOST, user, password) as ftp:
        with open(filename, 'rb') as fp:
            ftp.storbinary('STOR '+newname, fp)
    
    print(f'\nArchivo {filename} subido al servidor')

def extractConfigFile():
    global HOST1, user, password, HOST2

    mostarDirectorio()
    HOST = HOST1 if op == 1 else HOST2

    filename = input("\ningresa el nombre del archivo: ").strip()

    with FTP(HOST, user, password) as ftp:
        with open(filename, 'wb') as fp:
            ftp.retrbinary('RETR '+filename, fp.write)
    
    print(f'\nArchivo {filename} descargado')

def mostarDirectorio():
    global HOST1, user, password, HOST2

    selectIP()
    HOST = HOST1 if op == 1 else HOST2

    with FTP(HOST, user, password) as ftp:
        print("\nLos archivos en el directorio son: \n")
        ftp.dir()

def telnetConfigFile():
    global HOST1, user, password, HOST2
    
    selectIP()
    HOST = HOST1 if op == 1 else HOST2

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
    system(f'sudo route add -net 192.168.1.0 netmask 255.255.255.0 gw 30.30.30.1 dev tap0')
    return
