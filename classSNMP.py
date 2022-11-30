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
    def walkIterator(self, OID):
        return bulkCmd(
            SnmpEngine(),
            CommunityData(self.comunidad, mpModel=0),
            # ip to connect, default port for snmp
            UdpTransportTarget((self.ip, self.puerto)),
            ContextData(),
            0, 500,
            ObjectType(ObjectIdentity(OID))
        )

    def walkDatos(self, OID):
        iterator = self.walkIterator(OID)
        contador = 0
        while True:
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            if errorIndication:
                print(errorIndication)
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            else:
                # if '1.3.6.1.2.1.25.5.1.1.2' != str(varBinds[0][0][:11]):
                if OID != str(varBinds[0][0][:11]):
                    break
                contador += int(varBinds[0][1])
        return contador

        # print('\nValor en KB:',contador,'\nValor en MB:',contador*0.000977,'\nValor en GB:',contador*0.00000095367431640625)