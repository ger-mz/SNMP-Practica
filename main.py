from re import search, IGNORECASE
from pysnmp.hlapi import *
from fpdf import FPDF
import os
MIB = '1.3.6.1.2.1'
ip, puerto, comunidad = 0, 0 ,0

def agregarAgente():
    ip = input("Ingresa la ip: ")
    puerto = input("Ingresa el puerto: ")
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
    file.write(ip + ', ' + puerto + ', ' + comunidad+'\n')

    file.close()

    print('\nAgente Guaradado Exitosamente\n')
    return

def mostrarAgentesGuardados():
    try:
        file = open('agentes.csv', 'r', encoding='utf-8')
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
    lista, contador = mostrarAgentesGuardados()
    agente = int(input("Ingresa el id del agenete que quieres eliminar: "))
    if agente == -1 or agente < -1 or agente > contador:
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
    pdf.set_font('Times', '', 12)
    if search('windows', interfaceInfo[1], IGNORECASE):
        pdf.image('images/Windows8.jpeg', 170, 8, 33)

    if search('ubuntu', interfaceInfo[1], IGNORECASE):
        pdf.image('images/ubuntu.png', 170, 8, 33)

    for info in interfaceInfo:
        pdf.cell(0, 10, info, 0, 1)
    pdfname = interfaceInfo[0]
    pdf.output(pdfname[pdfname.find(':') + 2:] + '.pdf', 'F')

def generarReporte():
    # seleccionar agente, enviar solicitudes snmp para solicitar informacion
    print('')
    interfaceInfo = []
    lista, contador = mostrarAgentesGuardados()
    agente = int(input("Ingresa el id del agenete: "))

    if agente < 1 or agente > contador:
        print('\nOperacion no valida\n')
        return

    print('')

    global ip, puerto, comunidad
    ip, puerto, comunidad = getAgenteId(lista, agente-1)
    ip, puerto, comunidad = ip.strip(), puerto.strip(), comunidad.strip()

    # nombre / hostname
    interfaceInfo.append('Hostname: '+str(getDatos(MIB+'.1.5.0')))
    print(interfaceInfo[0])

    # S.O (version, logo), solo funciona con windows y ubuntu
    sistemaOperativo = str(getDatos(MIB+'.1.1.0')).split()
    for x in sistemaOperativo:
        if search('windows', x, IGNORECASE) or search('ubuntu', x, IGNORECASE):
            interfaceInfo.append('Sistema Operativo: ' + x)
            print(interfaceInfo[1])
            break

    # ubicacion
    interfaceInfo.append('Ubicacion: ' + str(getDatos(MIB+'.1.6.0')))
    print(interfaceInfo[2])

    # numero de interfaces
    numeroIntefaces = getDatos(MIB+'.2.1.0')
    interfaceInfo.append('Numero de Interfaces: '+ str(numeroIntefaces))
    print(interfaceInfo[3])

    # Estatus de las interfaces
    # Nombre de las interfaces
    print('Estatus de las interfaces: ')
    for i in range(1, int(numeroIntefaces)+1):
        name = getDatos(MIB+'.2.2.1.2.'+str(i))
        status = getDatos(MIB + '.2.2.1.7.' + str(i))
        interfaceInfo.append('Interface %d: %s' % (i, str(name)) +
              ' Estatus: ' + ('up' if status == 1 else 'down' if status == 2 else 'testing'))
        print(interfaceInfo[(3+i)])
        if i > 4:
            break

    # tiempo de actividad
    interfaceInfo.append('Tiempo de Actividad: %d %s' %(getDatos(MIB+'.1.3.0')//6000, 'Minutos'))
    print(interfaceInfo[len(interfaceInfo)-1])

    # Generador de reporte pdf con el nombre del hostname
    pdfGenerator(interfaceInfo)

    print('\nProcess Succesfull\n')

if __name__ == '__main__':
    while True :
        print('-----Inicio-----')
        print('Selecciona una de las siguientes opciones: ')
        print('1. Agregar Agenete')
        print('2. Eliminar Agente')
        print('3. Generar Reporte')
        opcion = input('Ingresa una opcion, -1 para terminar proceso: ')

        if opcion == '1':
            agregarAgente()

        elif opcion == '2':
            eliminarAgete()

        elif opcion == '3':
            generarReporte()

        elif opcion == '-1':
            break
        else:
            os.system("cls")
            print('\nError opcion no valida\n')

    # Recordar como cambiar la comunidad
    # Revisar net-snmp.org ejecutable getsnmpget
    # Instalaciones necesarias pysnmp fpdf