from django.apps import AppConfig


class RepairConfig(AppConfig):
    name = 'repair'
    verbose_name = '故障报修'

    notification_title = '故障报修申请'