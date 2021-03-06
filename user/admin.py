from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from reservation.models import Reservation
from user.models import User, Contact, UserMeta, Department
from import_export import resources
from import_export.admin import ImportExportMixin
from import_export.fields import Field
from import_export.widgets import Widget, ForeignKeyWidget
from django.db.models.functions import Concat
from django.contrib.auth.hashers import make_password

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    search_fields = ('name', )

admin.site.register(Department, DepartmentAdmin)

class UserMetaInline(admin.StackedInline):
    model = UserMeta

class ContactInline(admin.StackedInline):
    model = Contact
    fk_name = 'user'
    autocomplete_fields = ('friend_user', )

class UserResourceBase(resources.ModelResource):
    username = Field('username', column_name='工号')
    last_name = Field('last_name', column_name='姓氏')
    first_name = Field('first_name', column_name='名字')
    email = Field('email', column_name='电子邮箱')
    department = Field('department', column_name='系所', widget=ForeignKeyWidget(Department, 'name'))

    class Meta:
        model = User
        skip_unchanged = True
        report_skipped = True
        fields = (
            'username',
            'last_name',
            'first_name',
            'email',
            'department'
        )

class PasswordWidget(Widget):
    def clean(self, value, row=None):
        return make_password(value)

class UserResource(UserResourceBase):
    password = Field('password', column_name='初始密码', widget=PasswordWidget())

    class Meta(UserResourceBase.Meta):
        fields = UserResourceBase.Meta.fields + ('password', )

class CustomUserAdmin(ImportExportMixin, UserAdmin):
    resource_class = UserResource
    list_display = ('username', 'fullname', 'email', 'department', 'meta__post', 'meta__phone', 'date_joined')
    search_fields = ('username', 'fullname')
    list_filter = ('department', )
    exclude = ('wechat_open_id', )
    search_placeholder = '按用户名或姓名查找...'
    fieldsets = UserAdmin.fieldsets + (('系所', {'fields': ('department', )}), )
    autocomplete_fields = ('department', )

    def get_export_resource_class(self):
        return UserResourceBase

    def meta__post(self, obj):
        return obj.meta.post

    def meta__phone(self, obj):
        return obj.meta.phone

    def fullname(self, obj):
        return obj.fullname

    inlines = (UserMetaInline, ContactInline)

CustomUserAdmin.fullname.short_description = '真实姓名'
CustomUserAdmin.meta__post.short_description = '职位'
CustomUserAdmin.meta__phone.short_description = '手机号'

admin.site.register(User, CustomUserAdmin)
