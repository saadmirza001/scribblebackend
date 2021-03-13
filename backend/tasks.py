from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from datetime import date
from celery import Celery
from celery.decorators import task


@task
def SendMailTask(email, receiverName,likedUser, blogTitle):
    today = date.today()
    from_email = settings.EMAIL_HOST_USER
    to_mail = [email]
    msg = ""
    sub = "Liked Mail.."
    html = get_template("liked_mail.html").render({"receiverName": receiverName,
                                                   "likedUser": likedUser,
                                                   "blogTitle": blogTitle, "date": today})

    send_mail(sub, msg, from_email, to_mail, html_message=html, fail_silently=True)
    print("Its Done....")
