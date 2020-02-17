from django.apps import AppConfig


class ReservationConfig(AppConfig):
    name = 'reservation'
    verbose_name = '会议室预约'
    reserve_task_timeout = 15
