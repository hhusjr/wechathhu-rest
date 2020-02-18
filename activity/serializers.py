from rest_framework import serializers
from activity.models import Activity, Enrollment, ClockinMeta, ClockinRecord
from user.models import User
from rest_framework.validators import UniqueTogetherValidator
from django.utils import timezone
import json
from django.db import transaction

class ActivitySerializer(serializers.ModelSerializer):
    enrollment_count = serializers.ReadOnlyField()
    my_enrollment_count = serializers.ReadOnlyField()

    class Meta:
        model = Activity
        fields = [
            'id',
            'time_start',
            'time_end',
            'location',
            'name',
            'description',
            'form_metas',
            'open_for_enrollment',
            'enrollment_count',
            'my_enrollment_count',
            'participants_total_limit'
        ]

class EnrollmentFormFormatError(Exception):
    def __init__(self, detail = None, field = None):
        if detail is None:
            detail = '报名失败：报名表单不合法。'
        self.detail = detail
        if field is not None:
            self.detail += '（字段：' + field + '）'
        super().__init__()

class EnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Enrollment
        fields = [
            'id',
            'enroll_time',
            'activity',
            'user',
            'participating_metas'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Enrollment.objects.all(),
                fields=['activity', 'user'],
                message='你已经报名过该活动。'
            )
        ]

    def validate_activity(self, attrs):
        if not attrs.open_for_enrollment:
            raise serializers.ValidationError('报名通道暂未开启。')
        
        if timezone.now() > attrs.time_end:
            raise serializers.ValidationError('该活动已结束，无法继续报名。')

        if attrs.is_full():
            raise serializers.ValidationError('报名人数已经达到上限，无法继续报名。')

        return attrs

    '''
    e.g.
    {
        "用户名": {
            "required": true,
            "type": "text",
            "default": "ABC"
        },
        "学号": {
            "required": true,
            "type": "number"
        },
        "性别": {
            "required": false,
            "type": "radio",
            "default": "男",
            "choices": ["男", "女"]
        },
        "爱好": {
            "required": true,
            "type": "checkbox",
            "default": ["编程", "数学"],
            "choices": ["编程", "睡觉", "数学"]
        }
    }
    '''
    def validate(self, data):
        attrs = data['participating_metas']
        try:
            form_metas = json.loads(data['activity'].form_metas)
            attrs = json.loads(attrs)
            if not isinstance(form_metas, dict) or not isinstance(attrs, dict):
                raise EnrollmentFormFormatError

            common_default_values = {
                'checkbox': [],
                'radio': '',
                'text': '',
                'number': '',
                'textarea': ''
            }

            cleaners = {
                'text': lambda x, rules, name: str(x),
                'textarea': lambda x, rules, name: str(x),
                'number': lambda x, rules, name: int(x) if x.isdigit() else EnrollmentFormFormatError('数字不合法', name),
                'radio': lambda x, rules, name: x \
                    if x in rules['choices'] else EnrollmentFormFormatError('单选项不合法', name),
                'checkbox': lambda x, rules, name: x \
                    if isinstance(x, list) and set(x).issubset(set(rules['choices'])) else EnrollmentFormFormatError('多选项不合法', name)
            }

            for name, rules in form_metas.items():
                t = rules['type']

                # check if its required and add the default value
                required = 'required' in rules and rules['required']
                if name not in attrs or attrs[name] == '':
                    if not required:
                        attrs[name] = common_default_values[t] if 'default' not in rules else rules['default']
                        continue
                    else:
                        raise EnrollmentFormFormatError('必填项' + name + '不得为空。', name)

                # remove extra spacing, and do the cleaning
                attrs[name] = cleaners[t](attrs[name], rules, name)
                if (isinstance(attrs[name], EnrollmentFormFormatError)):
                    raise attrs[name]

        except EnrollmentFormFormatError as e:
            raise serializers.ValidationError(e.detail)
  
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            raise serializers.ValidationError('报名失败：报名表单不合法。')

        data['participating_metas'] = json.dumps(attrs)
        return data

    def create(self, validated_data):
        with transaction.atomic():
            activity = Activity.objects.select_for_update().get(id=validated_data['activity'].id)

            if activity.participants_total_limit is not None \
                and Enrollment.objects.filter(activity=activity).count() >= activity.participants_total_limit:
                transaction.set_rollback(True)
                raise serializers.ValidationError({
                    'non_field_errors': ['报名人数已经达到上限，无法继续报名。']
                })
            
            enrollment = Enrollment.objects.create(**validated_data)
        
        return enrollment

class ClockinSerializer(serializers.ModelSerializer):
    is_clockin = serializers.SerializerMethodField()

    def get_is_clockin(self, instance):
        return ClockinRecord.objects.filter(user=self.context['request'].user, clockin_meta=instance).count() > 0

    class Meta:
        model = ClockinMeta
        fields = (
            'label',
            'is_clockin'
        )