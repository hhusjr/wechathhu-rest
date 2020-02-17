from django.core.exceptions import ImproperlyConfigured
from simpleui.templatetags.simpletags import *
from django.contrib.admin.filters import ListFilter

class DateTimeFilter(ListFilter):
    parameter_name = None

    datetime_type = 'datetime'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        if self.parameter_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify a 'parameter_name'."
                % self.__class__.__name__
            )

        field_path = self.parameter_name
        self.field_path = field_path
        self.field_generic = '{}__'.format(field_path)
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_until = '%s__lt' % field_path

        self.links = [
            ('全部时间', {}),
        ]

        for target in self.expected_parameters():
            if target in params:
                value = params.pop(target)
                self.used_parameters[target] = value

    def has_output(self):
        return True

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_until]

    def choices(self, changelist):
        yield {}

@register.filter
def get_date_type(spec):
    try:
        field = spec.field
    except AttributeError:
        try:
            datetime_type = spec.datetime_type
        except AttributeError:
            return ''
        if spec.datetime_type == 'datetime':
            return 'datetime'
        elif spec.datetime_type == 'date':
            return 'date'
        elif spec.datetime_type == 'time':
            return 'time'
        else:
            return ''

    field_type = ''
    if isinstance(field, models.DateTimeField):
        field_type = 'datetime'
    elif isinstance(field, models.DateField):
        field_type = 'date'
    elif isinstance(field, models.TimeField):
        field_type = 'time'

    return field_type
