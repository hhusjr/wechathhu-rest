"""wechathhu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
import activity.views
import user.views
import reservation.views
import repair.views
import guide.views
from user.auth_views import general, wechat

admin.site.site_header = 'HHU计信院教师微服务'
admin.site.site_title  = 'HHU计信院教师微服务'
admin.site.index_title = '后台管理'

router = routers.DefaultRouter()
router.register(r'activities/clockins', activity.views.ClockinViewset, basename='clockin')
router.register(r'activities', activity.views.ActivityViewset, basename='activity')
router.register(r'enrollments', activity.views.EnrollmentViewset, basename='enrollment')
router.register(r'reservations', reservation.views.ReservationViewset, basename='reservation')
router.register(r'repairs', repair.views.RepairRequestViewset, basename='repair')
router.register(r'guides', guide.views.GuideViewset, basename='guide')
router.register(r'contacts', user.views.ContactViewset, basename='contact')

urlpatterns = (
    path('auth/wechat-code2token/', wechat.code2token),
    path('auth/wechat-auth/', wechat.wechat_auth_view),
    path('auth/get-token/', general.obtain_expiring_auth_token),
    path('current-user/meta/', user.views.current_usermeta_view),
    path('current-user/', user.views.current_user_view),
    path('friends/<int:pk>/', user.views.friend),

    path('meetingrooms/available/', reservation.views.available_meetingrooms),
    path('repairs/categories/', repair.views.get_categories),
    path('guides/<int:pk>/email/', guide.views.email_guide),

    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
