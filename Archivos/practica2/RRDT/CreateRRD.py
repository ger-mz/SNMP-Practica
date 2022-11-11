# !/usr/bin/env python
import rrdtool
ret = rrdtool.create("practica2.rrd",
                     "--start",'N',
                     "--step",'300',
                     "DS:multicas:COUNTER:120:U:U",
                     "DS:paquetesIP:COUNTER:120:U:U",
                     "DS:paquetesICMP:COUNTER:120:U:U",
                     "DS:segmentosTCP:COUNTER:120:U:U",
                     "DS:datagramas:COUNTER:120:U:U",
                     "RRA:AVERAGE:0.5:6:100",
                     "RRA:AVERAGE:0.5:1:200")

if ret:
    print (rrdtool.error())

# rrdtool.dump('practica2.rrd', 'practica2.xml')
