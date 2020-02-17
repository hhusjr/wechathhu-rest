from django.apps import AppConfig


class ActivityConfig(AppConfig):
    name = 'activity'
    verbose_name = '活动报名与打卡'

    clockin_qrcode_expire = 25 # Seconds
