import smtplib
from time import strftime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '
# Define params
# rrdpath = '../RRD/'
# imgpath = '../IMG/'
rrdpath = 'Datos/'
imgpath = 'Datos/'
fname = 'trend.rrd'

mailsender = "dummycuenta3@gmail.com"
# mailreceip = "ngermtz@gmail.com"
mailreceip = "dummycuenta3@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'dvduuffmlhspbmjj'

def send_alert_attached(subject, pngname, snmpa):
    """ Envía un correo electrónico adjuntando la imagen en IMG
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    body = f'INVENTARIO:\n NombreDispositivo: {snmpa.getDatos("1.3.6.1.2.1.1.5.0")}'
    body += f'\nVersion del software SO: {snmpa.getDatos("1.3.6.1.2.1.1.1.0")}'
    body += f'\nTiempo de Actividad sistema: {snmpa.getDatos("1.3.6.1.2.1.25.1.1.0")}'
    body += f'\nFecha y hora del host: {strftime("%d %b %Y %H:%M:%S")}'
    # imgpath+'deteccion_'+pngname+'.png'
    texto = MIMEText(body)
    msg.attach(texto)
    fp = open(imgpath+'deteccion_'+pngname+'.png', 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()