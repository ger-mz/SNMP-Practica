from time import time, sleep
import rrdtool

# class RRD:
#     def __init__(self, ):
#         print('Hola Mundo')

def createRRD(filename, steps='300'):
    ret = rrdtool.create(str(filename)+".rrd",
                     "--start",'N',
                     "--step", str(steps),
                     "DS:multicas:COUNTER:120:U:U",
                     "DS:paquetesIP:COUNTER:120:U:U",
                     "DS:paquetesICMP:COUNTER:120:U:U",
                     "DS:segmentosTCP:COUNTER:120:U:U",
                     "DS:datagramas:COUNTER:120:U:U",
                     "RRA:AVERAGE:0.5:6:100",
                     "RRA:AVERAGE:0.5:1:300")
    if ret:
        print(rrdtool.error())

def updateRRD(endtime, rrdfilename, snmpa, printvalor=False):
    print("Inicion de Update-------------------------------------------")
    while time() < endtime:
        multicas = str(snmpa.getDatos('1.3.6.1.2.1.2.2.1.18.1'))  # 12.4 getsmulticast
        paquetesIP = str(snmpa.getDatos('1.3.6.1.2.1.4.10.0'))
        paquetesICMP = str(snmpa.getDatos('1.3.6.1.2.1.5.1.0'))
        segmentosTCP = str(snmpa.getDatos('1.3.6.1.2.1.6.12.0'))
        datagramas = str(snmpa.getDatos('1.3.6.1.2.1.7.4.0'))

        valor = "N:" + str(multicas) + ':' + str(paquetesIP) + ':' + str(paquetesICMP) + ':' + str(
            segmentosTCP) + ':' + str(datagramas)

        if printvalor == True:
            print(valor)
            rrdtool.dump(rrdfilename+'.rrd', rrdfilename+'.xml')

        rrdtool.update(rrdfilename+'.rrd', valor)
        sleep(1)
    print("Fin de update-----------------------------------------------")

def creargraficas(filename, inicio, final, paquetes, rrdfname, message):
    ret = rrdtool.graph(filename, #"traficoRED.png",
                        "--start", inicio,
                        "--end", final, #"N",
                        "--vertical-label=Bytes/s",
                        "--title=Tráfico de Red de un agente \n Usando SNMP y RRDtools",
                        "DEF:traficoEntrada="+rrdfname+":"+paquetes+":AVERAGE",
                        "CDEF:escalaIn=traficoEntrada,8,*",
                        "AREA:escalaIn#00FF00:"+message)
