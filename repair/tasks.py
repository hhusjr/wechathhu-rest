from celery import shared_task
from django.core.mail import send_mass_mail
from repair.models import NotificationUser, FaultCategory, RepairRequest
from repair.apps import RepairConfig
from wechathhu.settings import DEFAULT_FROM_EMAIL
from django.db.models import Q

@shared_task(queue='multi')
def send_notification_email(id):
    repair_request = RepairRequest.objects.get(id=id)
    notifications = NotificationUser.objects.filter(Q(category=repair_request.category) | Q(category__isnull=True)).all()

    if repair_request.category == None:
        return
    
    messages = []
    
    subject = repair_request.location + repair_request.category.name + RepairConfig.notification_title
    
    for notification in notifications:
        message = ' \
        您好，{notification_user}。您收到了新的故障报修申请： \n \
        【申请人】{request_user} \n \
        【申请时间】{created} \n \
        【故障类别】{category} \n \
        【故障地点】{location} \n \
        【概要】{description} \n \
        '.format(
            notification_user=notification.name,
            request_user=repair_request.user.last_name + repair_request.user.first_name,
            created=repair_request.created.strftime(r'%Y-%m-%d %H:%M:%S'),
            category=repair_request.category.name,
            location=repair_request.location,
            description=repair_request.description
        )

        messages.append((subject, message, DEFAULT_FROM_EMAIL, (notification.email, )))

    send_mass_mail(messages)