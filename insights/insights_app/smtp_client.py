import contextlib
import smtplib


@contextlib.contextmanager
def smtp_client(host: str, port: str, user: str, password: str):
    with smtplib.SMTP(host, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user, password)
        yield smtp
