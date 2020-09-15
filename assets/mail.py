import smtplib
from socket import gaierror


def sendMail(to: str, subject: str, message: str):
    import env as e
    try:
        with smtplib.SMTP(e.mail_host, e.mail_port) as server:
            server.login(e.mail_username, e.mail_password)
            server.sendmail(from_addr=e.mail_sender, to_addrs=to, msg=message)
    except (gaierror, ConnectionRefusedError):
        return "failed to connect to the server"
    except smtplib.SMTPServerDisconnected:
        return "Failed to connect to the server with the given credentials"
    except smtplib.SMTPException as e:
        return "SMTP error occured: " + str(e)
    server.close()
    return True
