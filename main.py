from file import agregarAgente, eliminarAgete, getAgente, pdfGenerator, encabezado, getRRDFILE, pdfContabilidad
from config import iniciarTap0, telnetConfigFile, mostarDirectorio, extractConfigFile, uploadFile
from RRDT import createRRD, updateRRD, creargraficas, updateRendimiento, createRRD_CPU_RAM_RED
from re import search, IGNORECASE
from threading import Thread
import time
import os

def generarReporte():
    interfaceInfo, snmpa = [], getAgente()
    if snmpa == -1:
        return
    MIB = snmpa.MIB

    sistemaOperativo = str(snmpa.getDatos(MIB+'.1.1.0')).split() # S.O (version, logo), solo funciona con windows y ubuntu

    for x in sistemaOperativo: # interfaceInfo.append('Sistema operativo:')
        if search('windows', x, IGNORECASE) or search('ubuntu', x, IGNORECASE) or search('linux', x, IGNORECASE):
            interfaceInfo.append('Sistema Operativo: ' + x)
            break

    interfaceInfo.append('Hostname: ' + str(snmpa.getDatos(MIB + '.1.5.0'))) # nombre / hostname
    interfaceInfo.append('Contacto: ' + str(snmpa.getDatos(MIB + '.1.4.0'))) # informacion de contacto
    interfaceInfo.append('Ubicacion: ' + str(snmpa.getDatos(MIB + '.1.6.0'))) # ubicacion
    numeroIntefaces = snmpa.getDatos(MIB + '.2.1.0')
    interfaceInfo.append('Numero de Interfaces: ' + str(numeroIntefaces)) # numero de interfaces

    for i in range(1, int(numeroIntefaces)+1): # Estatus de las interfaces y nombre de las interfaces
        name = snmpa.getDatos(MIB+'.2.2.1.2.'+str(i))
        status = snmpa.getDatos(MIB + '.2.2.1.7.' + str(i))
        interfaceInfo.append('Interface %d: %s' % (i, str(name)) +
                             ' Estatus: ' + ('up' if status == 1 else 'down' if status == 2 else 'testing'))
        # print(interfaceInfo[(4+i)])
        if i > 4:
            break

    # tiempo de actividad
    interfaceInfo.append('Tiempo de Actividad : %s %s' %(str(snmpa.getDatos(MIB+'.1.3.0')), 'hundredths of senconds'))
    # print(interfaceInfo[len(interfaceInfo)-1])

    pdfGenerator(interfaceInfo) # Generador de reporte pdf con el nombre del hostname

    print('\nProcess Succesfull\n')


def iniciarMonitoreo():
    snmpa = getAgente()
    if snmpa == -1:
        return

    secondstime = input("ingresa el tiempo en segundos para monitorear (10min == 600): ")
    rrdfilename = input("ingresa un nombre para el archivo rrd: ")

    createRRD(rrdfilename)
    tiempo = int(time.time())
    tiempofinal = tiempo + int(secondstime)
    print('El tiempo final sera:', str(tiempofinal))

    t = Thread(name='updaterrd', target=updateRRD, args=(tiempofinal, rrdfilename, snmpa))
    t.start()

    try:
        file = open("Datos/rrdfiles.csv", "r", encoding="utf8")
        file.close()
    except FileNotFoundError:
        file = open("Datos/rrdfiles.csv", "w", encoding="utf8")
        file.close()

    data = str(snmpa.getDatos('1.3.6.1.2.1.1.5.0'))
    mail = str(snmpa.getDatos('1.3.6.1.2.1.1.4.0'))

    file = open("Datos/rrdfiles.csv", "a", encoding="utf8")
    file.write('\n' + str(tiempo) + ', ' + str(tiempofinal) + ', ' + str(rrdfilename)+'.rrd' +
               ', ' + str(data) + ', ' + str(mail))

    file.close()


def reporteContabilidad():
    print('\ngenerado reporte de contabilidad\n')
    inicio, final, narchivo, device, mail = getRRDFILE()

    dataS = ["multicas", "paquetesIP", "paquetesICMP", "segmentosTCP", "datagramas"]
    msg = ["Paquetes Multicast", "Paquetes IP", "Mensajes ICMP", "Segmentos Retransmitidos TCP", "Datagramas enviados"]

    print("El tiempo inicia:",inicio)
    print("El tiempo termina:",final)
    settime = input("Para cambiar el tiempo de inicio o termino ingresa 1: ")

    if settime.strip() == '1':
        inicio = input("Ingresa el tiempo inicial: ")
        final = input("Ingresa el tiempo final: ")

    for i in range(0, 5):
        creargraficas("graficas/grafica"+str(i+1)+".png", str(inicio), str(final), dataS[i], narchivo, msg[i])

    pdfContabilidad(device, mail, msg)

    print('\n\nReporte Creado Correctamente\n\n')


def contabilidad():
    print(encabezado)
    print('-------------------------CONTABILIDAD-------------------------')
    print('Selecciona una de las siguientes opciones: ')
    print('\t1. Iniciar Monitoreo')
    print('\t2. Generar Reporte de contabilidad')
    opcion = int(input('Ingresa una opcion, -1 para terminar proceso: '))

    if opcion == 1:
        iniciarMonitoreo()
    elif opcion == 2:
        reporteContabilidad()
    else:
        print("\n\nError\n\n")

def monitorizarRendimiento():
    print('Inicio de Monitoreo de CPU, RAM y RED')

    secondstime = input("ingresa el tiempo en segundos para monitorear (10min == 600): ")
    tiempofinal = int(time.time()) + int(secondstime)
    print('El tiempo final sera:', str(tiempofinal))
    filename = str(input('Ingresa el nombre del archivo rrd: '))

    createRRD_CPU_RAM_RED('Datos/'+filename+'1', 'CPUMonitor', steps=1, RECMODE='LAST')
    createRRD_CPU_RAM_RED('Datos/'+filename+'2', 'RAMMonitor', steps=1)
    createRRD_CPU_RAM_RED('Datos/'+filename+'3', 'REDMonitor', steps=1, Modo='COUNTER', lw='U', up='U')
    snmp = getAgente()

    t = Thread(name='updateRendimiento', target=updateRendimiento, args=(tiempofinal, filename, snmp))
    t.start()

def configuracionCloud():
    print(encabezado)
    print('-------------------------CONFIGURACION-------------------------')
    print('Selecciona una de las siguientes opciones: ')
    print('\t1. Iniciar interfaz Tap0 de la red')
    print('\t2. Conexion telnet generar Archivo de Configuracion')
    print('\t3. Mostrar Archivos')
    print('\t4. Extraer Archivo')
    print('\t5. Surbir Archivo')
    opcion = int(input('Ingresa una opcion, -1 para terminar proceso: '))

    if opcion == 1:
        iniciarTap0()
    elif opcion == 2:
        telnetConfigFile()
    elif opcion == 3:
        mostarDirectorio()
    elif opcion == 4:
        extractConfigFile()
    elif opcion == 5:
        uploadFile()
    else:
        print("\n\nError\n\n")


if __name__ == '__main__':
    while True :
        print('\n',encabezado)
        print('-------------------------Inicio-------------------------')
        print('Selecciona una de las siguientes opciones: ')
        print('\t1. Agregar Agenete')
        print('\t2. Eliminar Agente')
        print('\t3. Generar Reporte')
        print('\t4. Contabilidad de uso')
        print('\t5. Monitorizar Rendimiento')
        print('\t6. Configuracion Remota')
        opcion = input('Ingresa una opcion, -1 para terminar proceso: ')

        os.system("clear")
        # os.system("cls")

        if opcion == '1':
            agregarAgente()

        elif opcion == '2':
            eliminarAgete()

        elif opcion == '3':
            generarReporte()

        elif opcion == '4':
            contabilidad()

        elif opcion == '5':
            monitorizarRendimiento()
        
        elif opcion == '6':
            configuracionCloud()

        elif opcion == '-1':
            print('\nPrograma Finalizado')
            break

        else:
            print('\nError opcion no valida\n')