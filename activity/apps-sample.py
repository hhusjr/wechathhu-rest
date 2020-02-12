from django.apps import AppConfig


class ActivityConfig(AppConfig):
    name = 'activity'

    clockin_qrcode_expire = 25 # Seconds