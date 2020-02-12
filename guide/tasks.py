from celery import shared_task
from guide.models import Guide
from guide.apps import GuideConfig
from django.core.mail import EmailMultiAlternatives
from wechathhu.settings import DEFAULT_FROM_EMAIL
from email.header import make_header
import os

@shared_task
def send_guide_email(id, email):
    guide = Guide.objects.get(id=id)
    file = guide.file
    file_name = os.path.basename(file.path)
    name = guide.name
    fd = open(file.path, 'rb')
    header = make_header([(file_name, 'utf-8')]).encode('utf-8')
    subject = name + ' - ' + GuideConfig.guide_email_title
    body = '您通过微服务APP向邮箱发送了服务指南：' + name + ' 【' + file_name + '】'

    msg = EmailMultiAlternatives(subject, body, DEFAULT_FROM_EMAIL, (email, ))
    msg.attach(header, fd.read())

    msg.send()