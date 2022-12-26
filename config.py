from telnetlib import Telnet
from os import system

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

    return 0