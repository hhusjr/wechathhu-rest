from django.contrib import admin
from reservation.models import Reservation
from user.models import User, Contact, UserMeta
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from django.db.models.functions import Concat

class UserMetaInline(admin.StackedInline):
    model = UserMeta

class ContactInline(admin.StackedInline):
    model = Contact
    fk_name = 'user'
    autocomplete_fields = ('friend_user', )

class UserResource(resources.ModelResource):
    id = Field('id', column_name='编号', readonly=True)
    username = Field('username', column_name='工号')
    last_name = Field('last_name', column_name='姓')
    first_name = Field('first_name', column_name='名')
    email = Field('email', column_name='电子邮箱')

    class Meta:
        model = User
        skip_unchanged = True
        report_skipped = True
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'email'
        )

class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = ('username', 'fullname', 'email', 'meta__department', 'meta__post', 'meta__phone')
    search_fields = ('username', 'fullname')
    list_filter = ('meta__department', 'meta__post')
    exclude = ('wechat_open_id', )
    search_placeholder = '按用户名或姓名查找...'

    def meta__department(self, obj):
        return obj.meta.department

    def meta__post(self, obj):
        return obj.meta.post

    def meta__phone(self, obj):
        return obj.meta.phone

    def fullname(self, obj):
        return obj.fullname

    inlines = (UserMetaInline, ContactInline)

UserAdmin.fullname.short_description = '真实姓名'
UserAdmin.meta__department.short_description = '部门'
UserAdmin.meta__post.short_description = '职位'
UserAdmin.meta__phone.short_description = '手机号'

class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend_user')
    search_fields = ('user__username', 'fullname')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(fullname=Concat('user__last_name', 'user__first_name'))

admin.site.register(User, UserAdmin)
admin.site.register(Contact, ContactAdmin)
