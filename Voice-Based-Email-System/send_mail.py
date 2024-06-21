import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, sender, recipients, password, type, msg_id):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    if type == "reply":
          msg.add_header('In-Reply-To', msg_id)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())