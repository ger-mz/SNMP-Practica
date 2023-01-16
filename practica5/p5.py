import smtplib
from time import strftime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '
mailsender = "dummycuenta3@gmail.com"
# mailreceip = "ngermtz@gmail.com"
# mailreceip = "dummycuenta3@gmail.com"
mailreceip = "germartinez0153@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'pevownkjheqyazdn'

def send_alert_attached(subject):
    """ Envía un correo electrónico adjuntando la imagen en IMG"""
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    body = 'Alerta linkDown enviada por el router RCP-1 \n Gerardo Martinez Medrano'

    texto = MIMEText(body)
    msg.attach(texto)
    
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()

print("Enviando por correo Alerta de tipo linkDown")
send_alert_attached("Alerta LinkDown Gerardo Martinez")