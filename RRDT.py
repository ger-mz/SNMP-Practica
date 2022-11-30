from Notify import send_alert_attached
from time import time, sleep
import rrdtool

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

def createRRD_CPU_RAM_RED(filename, DSName,steps='300', Modo='GAUGE', lw='0', up='100', RECMODE='AVERAGE'):
    ret = rrdtool.create(str(filename)+".rrd",
                         "--start",'N',
                         "--step", str(steps),
                         "DS:"+DSName+":"+Modo+":60:"+lw+":"+up,
                         # "DS:RAMMonitor:GAUGE:60:0:100",
                         # "DS:REDMonitor:COUNTER:120:U:U",
                         "RRA:"+RECMODE+":0.5:6:150",
                         "RRA:"+RECMODE+":0.5:1:300")
    if ret:
        print(rrdtool.error())


def updateRendimiento(endtime, filename, snmp):
    print("Inicio Monitoreo de Rendimiento---------------------------------")
    ub1, ub2, ub3 = False, False, False
    while time() < endtime:
        UCPU = int(snmp.walkDatos('1.3.6.1.2.1.25.3.3.1.2')) // 8
        # GBRAM = int((100 * int(snmp.walkDatos('1.3.6.1.2.1.25.5.1.1.2'))) / 8562956)
        # REDU = int(snmp.getDatos('1.3.6.1.2.1.2.2.1.10.54')) + int(snmp.getDatos('1.3.6.1.2.1.2.2.1.16.54')) * 8

        # valor = "N:"+str(UCPU)+":"+str(GBRAM)+":"+str(REDU)
        valor = "N:"+str(UCPU)
        print('CPU:',valor)

        rrdtool.update('Datos/'+filename+'1'+'.rrd', "N:"+str(UCPU))
        rrdtool.dump('Datos/'+filename+'1'+'.rrd', 'Datos/'+filename+'.xml')

        # rrdtool.update('Datos/'+filename+'2'+'.rrd', "N:"+str(GBRAM))
        # rrdtool.dump('Datos/'+filename+'2'+'.rrd', 'Datos/'+filename+'.xml')
        #
        # rrdtool.update('Datos/'+filename+'3'+'.rrd', "N:"+str(REDU))
        # rrdtool.dump('Datos/'+filename+'3'+'.rrd', 'Datos/'+filename+'.xml')
        ub1, ub2, ub3 = graficaRendimiento(filename+'1',
                           '0', '100',
                           'Carga del CPU del agente Usando SNMP y RRDtools \n Detección de umbrales',
                           'CPUMonitor',
                           'cargaCPU',
                           'CPU',
                           'Carga de CPU',
                           'Carga CPU mayor que 10',
                           '35', '60', '80',
                           ub1, ub2, ub3,
                           'LAST', snmp)
        # graficaRendimiento(filename+'2',
        #                    '0', '100',
        #                    'Carga de la RAM del agente Usando SNMP y RRDtools \n Detección de umbrales',
        #                    'RAMMonitor',
        #                    'cargaRAM',
        #                    'RAM',
        #                    'Carga de RAM',
        #                    'Carga RAM mayor que 10',
        #                    '70', '80', '90')
        # graficaRendimiento(filename+'3',
        #                    'U', 'U',
        #                    'Carga de la RED del agente Usando SNMP y RRDtools \n Detección de umbrales',
        #                    'REDMonitor',
        #                    'cargaRED',
        #                    'RED',
        #                    'Carga de RED',
        #                    'Carga RED mayor que 10',
        #                    '30', '60', '90')

        sleep(1)
    print('Fin del Monitoreo')
def graficaRendimiento(filename, lower, upper, title, DS, dname, pngname, msj1, msj2, u1, u2, u3, ub1, ub2, ub3, RECMODE, snmp):
    rrdpath = 'Datos/'
    imgpath = 'Datos/'

    ultima_lectura = int(rrdtool.last(rrdpath+filename+".rrd"))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - 1800

    ret = rrdtool.graphv(imgpath+"deteccion_"+pngname+".png",
                          "--start",str(tiempo_inicial),
                          "--end",str(tiempo_final),
                          "--vertical-label="+dname,
                          '--lower-limit', lower,
                          '--upper-limit', upper,
                          "--title="+title,
                          "DEF:"+dname+"="+rrdpath+filename+".rrd:"+DS+":"+RECMODE,
                          "VDEF:cargaMAX="+dname+",MAXIMUM",
                          "VDEF:cargaMIN="+dname+",MINIMUM",
                          "VDEF:cargaSTDEV="+dname+",STDEV",
                          "VDEF:cargaLAST="+dname+",LAST",
                          # "CDEF:cargaEscalada="+dname+",8,*", #Multiplicar por 8
                          # "CDEF:umbral"+u1+"=cargaEscalada,"+u1+",LT,0,cargaEscalada,IF", #Umbral 1
                          # "CDEF:umbral"+u2+"=cargaEscalada,"+u2+",LT,0,cargaEscalada,IF", #Umbral 2
                          # "CDEF:umbral"+u3+"=cargaEscalada,"+u3+",LT,0,cargaEscalada,IF", #Umbral 3
                          "CDEF:umbral"+u1+"="+dname+","+u1+",LT,0,"+dname+",IF", #Umbral 1
                          "CDEF:umbral"+u2+"="+dname+","+u2+",LT,0,"+dname+",IF", #Umbral 2
                          "CDEF:umbral"+u3+"="+dname+","+u3+",LT,0,"+dname+",IF", #Umbral 3
                          "AREA:"+dname+"#00FF00:"+msj1,
                          "HRULE:"+u1+"#ffe532:Umbral "+u1+" - 5%",
                          "HRULE:"+u2+"#FF9F00:Umbral "+u2+" - 5%",
                          "HRULE:"+u3+"#e60024:Umbral "+u3+" - 5%",
                          "AREA:umbral"+u1+"#ffe532:"+msj2,
                          "AREA:umbral"+u2+"#FF9F00:"+msj2,
                          "AREA:umbral"+u3+"#e60024:"+msj2,
                          "PRINT:cargaLAST:%6.2lf",
                          "GPRINT:cargaMIN:%6.2lf %SMIN",
                          "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                          "GPRINT:cargaLAST:%6.2lf %SLAST" )
    # print(ret)

    #-------------------------------------------------------------------------------------------------------------------
    ultimo_valor=float(ret['print[0]'])
    if ultimo_valor > int(u1) and ultimo_valor < int(u2) and ub1 == False:
        send_alert_attached("GerardoMartinez "+pngname+" Sobrepasa Primer Umbral", pngname, snmp)
        ub1 = True
    if ultimo_valor >= int(u2) and ultimo_valor < int(u3) and ub2 == False:
        send_alert_attached("GerardoMartinez "+pngname+" Sobrepasa Segundo Umbral", pngname, snmp)
        ub2 = True
    if ultimo_valor >= int(u3) and ub3 == False:
        send_alert_attached("GerardoMartinez "+pngname+" Sobrepasa Tercer Umbral", pngname, snmp)
        ub3 = True

    return ub1, ub2, ub3

    # if ultimo_valor>60:
        # send_alert_attached("Sobrepasa Umbral línea base")
        # print("Sobrepasa Umbral línea base")

# stress-ng --matrix 0 -t 1m
#  Gone girl pelicula