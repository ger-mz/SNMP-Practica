from pysnmp.hlapi import *

class SNMPA:
    def __init__(self, ip, puerto, comunidad,  version):
        self.ip = ip
        self.comunidad = comunidad
        self.puerto = puerto
        self.version = version
        self.MIB = '1.3.6.1.2.1'

    def createIterator(self, OID):
        return getCmd(
            SnmpEngine(),
            CommunityData(self.comunidad, mpModel=0),
            # ip to connect, default port for snmp
            UdpTransportTarget((self.ip, self.puerto)),
            ContextData(),
            ObjectType(ObjectIdentity(OID))
        )

    def getDatos(self, OID):
        iterator = self.createIterator(OID)

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            return varBinds[0][1]