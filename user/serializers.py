from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from user.models import User, UserMeta, Contact, Department
from rest_framework import mixins
from pypinyin import lazy_pinyin, Style

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            'id',
            'name'
        )

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'groups',
            'department'
        )

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'department'
        )

class UserChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password', )
    
    def validate_password(self, value):
        try:
            password_validation.validate_password(value, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

class UserMetaSerializer(serializers.ModelSerializer):
    user_meta = serializers.SerializerMethodField(read_only=True)
    fullname = serializers.SerializerMethodField(read_only=True)
    alpha = serializers.SerializerMethodField(read_only=True)
    is_friend = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserMeta
        fields = (
            'user',
            'user_meta',
            'post',
            'qq',
            'wechat',
            'tel',
            'phone',
            'description',
            'fullname',
            'alpha',
            'is_friend'
        )
        read_only_fields = ('user', 'user_meta', 'fullname', 'alpha', 'is_friend')

    def get_fullname(self, instance):
        return instance.user.get_fullname()

    def get_is_friend(self, instance):
        return Contact.objects.filter(user=self.context['request'].user, friend_user=instance.user).count() > 0

    def get_user_meta(self, instance):
        return UserSerializer(instance.user).data

    def get_alpha(self, instance):
        py = lazy_pinyin(instance.user.last_name, style=Style.FIRST_LETTER)
        try:
            return str(py[0][0]).upper()
        except (IndexError, TypeError):
            return '?'