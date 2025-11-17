import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_notification_email(config, subject: str, body: str) -> bool:
    msg = MIMEMultipart()
    msg['From'] = config.notification_email
    msg['To'] = config.notification_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL(config.smtp_server, config.smtp_port) as server:
            server.login(config.smtp_user, config.smtp_password)
            server.send_message(msg)
        print(f"Email notification sent to {config.notification_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
