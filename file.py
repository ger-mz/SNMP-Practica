from re import search, IGNORECASE
from classSNMP import SNMPA
from time import strftime
from fpdf import FPDF

encabezado = '''    \tSistema de Administración de Red
     Práctica 2 - Administración de Contabilidad
    Gerardo Martínez Medrano\t 4CM13\t 2020630297'''

def agregarAgente():
    ip = input("Ingresa la ip: ")
    puerto = input("Ingresa el puerto: ")
    version = input("Ingresa la version: ")
    comunidad = input("ingresa la comunidad: ")
    try:
        file = open("Datos/agentes.csv", "r", encoding="utf8")
        for line in file:
            if line.find(ip) != -1:
                print("\nIP ya registrada.\n")
                file.close()
                return
        file.close()
    except FileNotFoundError:
        file = open("Datos/agentes.csv", "w", encoding="utf8")
        file.close()

    file = open("Datos/agentes.csv", "a", encoding="utf8")
    file.write(ip + ', ' + puerto + ', ' + comunidad+', '+version+'\n')

    file.close()

    print('\nAgente Guaradado Exitosamente\n')
    return

def getAgente(filename='Datos/agentes.csv'):
    lista, contador = mostrarDatosGuardados(filename)
    agente = int(input("Ingresa el id del agenete: "))

    if agente < 1 or agente > contador:
        print('\nOperacion no valida\n')
        return -1

    print('')

    ip, puerto, comunidad, version = separarDatos(lista, agente-1)
    ip, puerto, comunidad, version = ip.strip(), puerto.strip(), comunidad.strip(), version.strip()

    snmpa = SNMPA(ip, puerto, comunidad, version)
    return snmpa


def separarDatos(ageneteLista, id):
    return ageneteLista[id].split(',')

def mostrarDatosGuardados(filename):
    try:
        file = open(filename, 'r', encoding='utf-8')
    except FileNotFoundError:
        print('\nNo se econtro lista de agentes\n')
        exit()
    print('')
    contador, lista = 0, []
    for line in file:
        contador += 1
        print(str(contador) + ': ' + line.strip('\n'))
        lista.append(line)
    file.close()
    return lista, contador

def eliminarAgete():
    # print agentes
    lista, contador = mostrarDatosGuardados('Datos/agentes.csv')
    agente = int(input("Ingresa el id del agenete que quieres eliminar: "))
    if agente <= -1 or agente > contador:
        print('\nOperacion Cancelada\n')
        return

    replacefile = open('Datos/agentes.csv', 'w', encoding='utf-8')
    contador = 0
    for line in lista:
        contador += 1
        if contador != agente:
            replacefile.write(line)
    replacefile.close()
    print('\nAgente Eliminado Correctamente\n')

def pdfHeader():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', 'B', 16)

    head = encabezado.split('\n')
    pdf.cell(0, 10, '        ' + head[0], 0, 1)
    pdf.cell(0, 10, '     ' + head[1], 0, 1)
    pdf.cell(0, 10, head[2], 0, 1)

    pdf.set_font('Times', '', 12)

    return pdf

def pdfGenerator(interfaceInfo):
    pdf = pdfHeader()
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

def pdfContabilidad(device, mail, msg):
    pdf = pdfHeader()

    pdf.cell(0, 5, "device: " + device, 0, 1)
    pdf.cell(0, 5, "description: Acounting " + device, 0, 1)
    pdf.cell(0, 5, "date: "+strftime("%d %b %Y %H:%M:%S"), 0, 1)
    pdf.cell(0, 5, "defaultProtocol: radius", 0, 1)
    pdf.cell(0, 5, "rdate: "+strftime("%d %b %Y %H:%M:%S"), 0, 1)
    pdf.cell(0, 5, "#User-name", 0, 1)
    pdf.cell(0, 5, "1:"+mail, 0, 1)

    pdf.cell(0, 5, '', 0, 1)

    contador, pos = 0, 90
    for i in msg:
        if contador == 3:
            pdf.add_page()
            pos = 15

        contador += 1
        pdf.cell(0, 50, i, 0, 1)
        pdf.image('graficas/grafica'+str(contador)+'.png', 70, pos, 120)
        pos += 45

    pdf.output("reporte.pdf" + str(strftime(" Hora %H Min %M segundos %S")) + '.pdf', 'F')

def getRRDFILE(): # se puede reducir el codigo
    lista, contador = mostrarDatosGuardados('Datos/rrdfiles.csv')
    rrdfile = int(input("Ingresa el id del archivo: "))

    if rrdfile < 1 or rrdfile > contador:
        print('\nOperacion no valida\n')
        return -1

    print('')
    tinicio, tfin, filename, device, mail = separarDatos(lista, rrdfile-1)

    return tinicio.strip(), tfin.strip(), filename.strip(), device.strip(), mail.strip()
