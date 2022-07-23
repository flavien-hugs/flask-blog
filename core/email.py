from threading import Thread

from flask import current_app
from . import mail
from flask_mail import Message


def send_async_email(app, message):
    with app.app_context():
        mail.send(message)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()
    return thr
