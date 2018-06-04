import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

def create_message(from_addr, to_addr, subject, body, bcc_addrs=''):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Bcc'] = bcc_addrs
    msg['Date'] = formatdate()
    return msg

def send(server_address, password, msg):
    with smtplib.SMTP(server_address, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(msg['From'], password)
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
