from django.apps import AppConfig


class GuideConfig(AppConfig):
    name = 'guide'
    verbose_name = '服务指南'

    guide_email_title = '服务指南文件传送'