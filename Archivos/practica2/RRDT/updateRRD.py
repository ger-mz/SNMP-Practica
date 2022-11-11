import time
import rrdtool
from getSNMP import consultaSNMP

while 1:
    multicas = str(consultaSNMP('gerardo', '172.18.0.1', '1.3.6.1.2.1.2.2.1.18.55')) #12.4 getsmulticast
    paquetesIP = str(consultaSNMP('comunidadASR', '172.18.0.1', '1.3.6.1.2.1.4.10.0'))
    paquetesICMP = str(consultaSNMP('comunidadASR', '172.18.0.1', '1.3.6.1.2.1.5.1.0'))
    segmentosTCP = str(consultaSNMP('comunidadASR', '172.18.0.1', '1.3.6.1.2.1.6.12.0'))
    datagramas = str(consultaSNMP('comunidadASR', '172.18.0.1', '1.3.6.1.2.1.7.4.0'))


    # valor = "N:" + str(tcp_in_segments) + ':' + str(tcp_out_segments)
    valor = "N:"+str(multicas)+':'+str(paquetesIP)+':'+str(paquetesICMP)+':'+str(segmentosTCP)+':'+str(datagramas)
    print(valor)
    rrdtool.update('practica2.rrd', valor)
    rrdtool.dump('practica2.rrd', 'practica2.xml')
    time.sleep(1)

if ret:
    print(rrdtool.error())
    time.sleep(300)

# step 300 segundos
# 200 muestras
# 100 muestras
# se ajusta para monitorizar un dia entero
# Reporte parecido a RADIUS (no usarlo)
