import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendMail(to: str, subject: str, message: str, html: bool = False):
    import env as e

    # Create a SSL Context

    context = ssl.create_default_context()

    mail = MIMEMultipart("alternative")
    mail["Subject"] = subject
    mail["From"] = e.mail_sender
    mail["To"] = to

    if html:
        msg = MIMEText(message, "html")
    else:
        msg = MIMEText(message, "plain")

    mail.attach(msg)

    with smtplib.SMTP_SSL(e.mail_host, e.mail_port, context=context) as server:

        server.login(
            user=e.mail_sender,
            password=e.mail_password
        )

        server.sendmail(
            from_addr=e.mail_sender,
            to_addrs=to,
            msg=mail.as_string()
        )

        return True
