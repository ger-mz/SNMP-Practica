import time
from re import search, IGNORECASE
# from RRDT.rrdpy import RRDPY
from threading import Thread
from pysnmp.hlapi import *
from fpdf import FPDF
from time import strftime
import rrdtool
import os

MIB = '1.3.6.1.2.1'
ip, puerto, comunidad, version = 0, 0 ,0, 0
encabezado = '''    \tSistema de Administración de Red
     Práctica 2 - Administración de Contabilidad
    Gerardo Martínez Medrano\t 4CM13\t 2020630297'''

global globaltime
def agregarAgente():
    ip = input("Ingresa la ip: ")
    puerto = input("Ingresa el puerto: ")
    version = input("Ingresa la version: ")
    comunidad = input("ingresa la comunidad: ")
    try:
        file = open("agentes.csv", "r", encoding="utf8")
        for line in file:
            if line.find(ip) != -1:
                print("\nIP ya registrada.\n")
                file.close()
                return
        file.close()
    except FileNotFoundError:
        file = open("agentes.csv", "w", encoding="utf8")
        file.close()

    file = open("agentes.csv", "a", encoding="utf8")
    file.write(ip + ', ' + puerto + ', ' + comunidad+', '+version+'\n')

    file.close()

    print('\nAgente Guaradado Exitosamente\n')
    return

def mostrarAgentesGuardados(filename):
    try:
        file = open(filename, 'r', encoding='utf-8')
    except FileNotFoundError:
        print('\nNo se econtro lista de agentes\n')
        exit()
    contador = 0
    lista = []
    for line in file:
        contador += 1
        print(str(contador) + ': ' + line.strip('\n'))
        lista.append(line)
    file.close()
    return lista, contador

def eliminarAgete():
    # print agentes
    lista, contador = mostrarAgentesGuardados('agentes.csv')
    agente = int(input("Ingresa el id del agenete que quieres eliminar: "))
    if agente <= -1 or agente > contador:
        print('\nOperacion Cancelada\n')
        return

    replacefile = open('agentes.csv', 'w', encoding='utf-8')
    contador = 0
    for line in lista:
        contador += 1
        if contador != agente:
            replacefile.write(line)
    replacefile.close()
    print('\nAgente Eliminado Correctamente\n')

def createIterator(OID, comunidad, ip, puerto):
    return getCmd(
        SnmpEngine(),
        CommunityData(comunidad, mpModel=0),
        # ip to connect, default port for snmp
        UdpTransportTarget((ip, puerto)),
        ContextData(),
        ObjectType(ObjectIdentity(OID))
    )

def getDatos(OID):
    global ip, puerto, comunidad
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(comunidad, mpModel=0),
        # ip to connect, default port for snmp
        UdpTransportTarget((ip, puerto)),
        ContextData(),
        ObjectType(ObjectIdentity(OID))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        return varBinds[0][1]

def getAgenteId(ageneteLista, id):
    return ageneteLista[id].split(',')

def pdfGenerator(interfaceInfo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', 'B', 16)

    head = encabezado.split('\n')
    pdf.cell(0, 10, '        ' + head[0], 0, 1)
    pdf.cell(0, 10, '     ' + head[1], 0, 1)
    pdf.cell(0, 10, head[2], 0, 1)

    pdf.set_font('Times', '', 12)
    if search('windows', interfaceInfo[0], IGNORECASE):
        pdf.image('Images/Windows8.jpeg', 170, 8, 33)

    if search('ubuntu', interfaceInfo[0], IGNORECASE):
        pdf.image('Images/ubuntu.png', 170, 8, 33)

    if search('linux', interfaceInfo[0], IGNORECASE):
        pdf.image('Images/linux.jpg', 170, 8, 33)

    for info in interfaceInfo:
        pdf.cell(0, 10, info, 0, 1)

    pdfname = interfaceInfo[1]
    pdf.output(pdfname[pdfname.find(':') + 2:] + str(strftime(" Hora %H Min %M segundos %S")) + '.pdf', 'F')

def generarReporte():
    # seleccionar agente, enviar solicitudes snmp para solicitar informacion
    print('')
    interfaceInfo = []
    lista, contador = mostrarAgentesGuardados('agentes.csv')
    agente = int(input("Ingresa el id del agenete: "))

    if agente < 1 or agente > contador:
        print('\nOperacion no valida\n')
        return

    print('')

    global ip, puerto, comunidad, version
    ip, puerto, comunidad, version = getAgenteId(lista, agente-1)
    ip, puerto, comunidad, version = ip.strip(), puerto.strip(), comunidad.strip(), version.strip()

    # S.O (version, logo), solo funciona con windows y ubuntu
    sistemaOperativo = str(getDatos(MIB+'.1.1.0')).split()
    # interfaceInfo.append('Sistema operativo:')
    for x in sistemaOperativo:
        if search('windows', x, IGNORECASE) or search('ubuntu', x, IGNORECASE) or search('linux', x, IGNORECASE):
            interfaceInfo.append('Sistema Operativo: ' + x)
            print(interfaceInfo[0])
            break


    # nombre / hostname
    interfaceInfo.append('Hostname: ' + str(getDatos(MIB + '.1.5.0')))
    print(interfaceInfo[1])

    # informacion de contacto
    interfaceInfo.append('Contacto: '+ str(getDatos(MIB + '.1.4.0')))
    print(interfaceInfo[2])

    # ubicacion
    interfaceInfo.append('Ubicacion: ' + str(getDatos(MIB+'.1.6.0')))
    print(interfaceInfo[3])

    # numero de interfaces
    numeroIntefaces = getDatos(MIB+'.2.1.0')
    interfaceInfo.append('Numero de Interfaces: '+ str(numeroIntefaces))
    print(interfaceInfo[4])

    # Estatus de las interfaces
    # Nombre de las interfaces
    print('Estatus de las interfaces: ')
    for i in range(1, int(numeroIntefaces)+1):
        name = getDatos(MIB+'.2.2.1.2.'+str(i))
        status = getDatos(MIB + '.2.2.1.7.' + str(i))
        interfaceInfo.append('Interface %d: %s' % (i, str(name)) +
              ' Estatus: ' + ('up' if status == 1 else 'down' if status == 2 else 'testing'))
        print(interfaceInfo[(4+i)])
        if i > 4:
            break

    # tiempo de actividad
    interfaceInfo.append('Tiempo de Actividad : %s %s' %(str(getDatos(MIB+'.1.3.0')), 'hundredths of senconds'))
    print(interfaceInfo[len(interfaceInfo)-1])

    # Generador de reporte pdf con el nombre del hostname
    pdfGenerator(interfaceInfo)

    print('\nProcess Succesfull\n')

def createRRD(filename):
    ret = rrdtool.create(str(filename)+".rrd",
                     "--start",'N',
                     "--step",'300',
                     "DS:multicas:COUNTER:120:U:U",
                     "DS:paquetesIP:COUNTER:120:U:U",
                     "DS:paquetesICMP:COUNTER:120:U:U",
                     "DS:segmentosTCP:COUNTER:120:U:U",
                     "DS:datagramas:COUNTER:120:U:U",
                     "RRA:AVERAGE:0.5:6:100",
                     "RRA:AVERAGE:0.5:1:300")

    if ret:
        print(rrdtool.error())

def updateRRD():
    global globaltime, rrdfilename
    print("Inicion de Update")
    while time.time() < globaltime:
        multicas = str(getDatos('1.3.6.1.2.1.2.2.1.18.55'))  # 12.4 getsmulticast
        # multicas = str(getDatos('1.3.6.1.2.1.2.2.1.18.38'))  # 12.4 getsmulticast
        paquetesIP = str(getDatos('1.3.6.1.2.1.4.10.0'))
        paquetesICMP = str(getDatos('1.3.6.1.2.1.5.1.0'))
        segmentosTCP = str(getDatos('1.3.6.1.2.1.6.12.0'))
        datagramas = str(getDatos('1.3.6.1.2.1.7.4.0'))

        valor = "N:" + str(multicas) + ':' + str(paquetesIP) + ':' + str(paquetesICMP) + ':' + str(
            segmentosTCP) + ':' + str(datagramas)

        # print(valor)

        rrdtool.update(rrdfilename+'.rrd', valor)
        rrdtool.dump(rrdfilename+'.rrd', rrdfilename+'.xml')
        time.sleep(1)

    print("Fin de update")

def iniciarMonitoreo():
    global globaltime, rrdfilename, ip, puerto, comunidad
    print('')
    interfaceInfo = []
    lista, contador = mostrarAgentesGuardados('agentes.csv')
    agente = int(input("Ingresa el id del agenete: "))

    if agente < 1 or agente > contador:
        print('\nOperacion no valida\n')
        return

    print('')

    global ip, puerto, comunidad, version
    ip, puerto, comunidad, version = getAgenteId(lista, agente-1)
    ip, puerto, comunidad, version = ip.strip(), puerto.strip(), comunidad.strip(), version.strip()

    secondstime = input("Ingresa el tiempo en segundos para monitorear (10min == 600): ")
    rrdfilename = input("Ingresa un nombre para el archivo rrd: ")

    createRRD(rrdfilename)

    tiempo = int(time.time())
    tiempofinal = tiempo + int(secondstime)

    print('Tiempo final:',str(tiempofinal))
    globaltime = tiempofinal

    t = Thread(name='updaterrd', target=updateRRD)

    t.start()

    try:
        file = open("rrdfiles.csv", "r", encoding="utf8")
        file.close()
    except FileNotFoundError:
        file = open("rrdfiles.csv", "w", encoding="utf8")
        file.close()

    file = open("rrdfiles.csv", "a", encoding="utf8")
    file.write('\n' + str(tiempo) + ', ' + str(tiempofinal) + ', ' + str(rrdfilename)+'.rrd' +
               ', ' + str(ip) + ', ' + str(puerto) + ', ' + str(comunidad) + ', ' + str(version))

    file.close()

    # print('\n\nFin de monitoreo\n\n')


def reporteContabilidad():
    print('\nGenerado Reporte de Contabilidad\n')

    lista, contador = mostrarAgentesGuardados('rrdfiles.csv')
    agente = int(input("Ingresa el id del agenete para graficar: "))
    if agente <= -1 or agente > contador:
        print('\nOperacion Cancelada\n')
        return

    global ip, puerto, comunidad, version
    inicio, final, narchivo, ip, puerto, comunidad, version = getAgenteId(lista, agente-1)
    inicio, final, narchivo, ip, puerto, comunidad, version = inicio.strip(), final.strip(), narchivo.strip(), ip.strip(), puerto.strip(), comunidad.strip(), version.strip()

    dataS = ["multicas", "paquetesIP", "paquetesICMP", "segmentosTCP", "datagramas"]
    msg = ["Paquetes Multicast", "Paquetes IP", "Mensajes ICMP", "Segmentos Retransmitidos TCP", "Datagramas enviados"]

    print("El tiempo inicia en:",inicio)
    print("El tiempo termina en:",final)
    settime = input("Para ingresar inicio y termino personalisado ingresa 1: ")

    if int(settime) == 1:
        inicio = input("Ingresa el tiempo inicial: ")
        final = input("Ingresa el tiempo final: ")

    for i in range(0, 5):
        creargraficas("graficas/grafica"+str(i+1)+".png", str(inicio), str(final), dataS[i], narchivo, msg[i])

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', 'B', 16)
    head = encabezado.split('\n')
    pdf.cell(0, 10, '                              ' + head[0], 0, 1)
    pdf.cell(0, 10, '                         ' + head[1], 0, 1)
    pdf.cell(0, 10, '                    '+head[2], 0, 1)

    pdf.set_font('Times', '', 12)

    data = str(getDatos('1.3.6.1.2.1.1.5.0'))
    pdf.cell(0, 5, "device: " + data, 0, 1)
    pdf.cell(0, 5, "description: Acounting " + data, 0, 1)
    pdf.cell(0, 5, "date: "+strftime("%d %b %Y %H:%M:%S"), 0, 1)
    pdf.cell(0, 5, "defaultProtocol: radius", 0, 1)
    pdf.cell(0, 5, "rdate: "+strftime("%d %b %Y %H:%M:%S"), 0, 1)
    pdf.cell(0, 5, "#User-name", 0, 1)
    pdf.cell(0, 5, "1:"+str(getDatos("1.3.6.1.2.1.1.4.0")), 0, 1)

    pdf.cell(0, 5, '', 0, 1)

    contador, pos = 0, 90
    for i in msg:
        if contador == 3:
            pdf.add_page()
            pos = 15

        contador += 1
        pdf.cell(0, 50, i, 0, 1)
        # nombre, escala,

        pdf.image('graficas/grafica'+str(contador)+'.png', 70, pos, 120)
        pos += 45

    pdf.output("reporte.pdf" + str(strftime(" Hora %H Min %M segundos %S")) + '.pdf', 'F')

    print('\n\nGraficas creadas correctamente\n\n')

def creargraficas(filename, inicio, final, paquetes, rrdfname, message):
    ret = rrdtool.graph(filename, #"traficoRED.png",
                        "--start", inicio,
                        "--end", final, #"N",
                        "--vertical-label=Bytes/s",
                        "--title=Tráfico de Red de un agente \n Usando SNMP y RRDtools",
                        "DEF:traficoEntrada="+rrdfname+":"+paquetes+":AVERAGE",
                        "CDEF:escalaIn=traficoEntrada,8,*",
                        "AREA:escalaIn#00FF00:"+message)

def contabilidad():
    print('\n\n')
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

if __name__ == '__main__':
    while True :
        print('\n\n')
        print(encabezado)
        print('-------------------------Inicio-------------------------')
        print('Selecciona una de las siguientes opciones: ')
        print('\t1. Agregar Agenete')
        print('\t2. Eliminar Agente')
        print('\t3. Generar Reporte')
        print('\t4. Contabilidad de uso')
        opcion = input('Ingresa una opcion, -1 para terminar proceso: ')

        if opcion == '1':
            agregarAgente()

        elif opcion == '2':
            eliminarAgete()

        elif opcion == '3':
            generarReporte()

        elif opcion == '4':
            contabilidad()

        elif opcion == '-1':
            break

        else:
            os.system("cls")
            # os.system("clear")
            print('\nError opcion no valida\n')