""" based on django FormWidget """
from django.core import validators
from django import forms
from django.conf import settings

USE_DOJO = getattr(settings, 'USE_DOJO', False)

class CheckboxWidget(forms.CheckboxField):
    def __init__(self, form_field):
        super(CheckboxWidget, self).__init__(form_field.field_name, form_field.checked_by_default, form_field.validator_list)

    def __repr__(self):
        return 'CheckboxWidget "%s"' % self.field_name

    def render(self, data):
        checked_html = ''
        ret = [
               '<label class="">%s</label>' % self.
               ]
        if data or (data is '' and self.checked_by_default):
            checked_html = ' checked="checked"'
        ret.append('<input type="checkbox" id="%s" class="v%s" name="%s"%s />' % \
            (self.get_id(), self.__class__.__name__,
            self.field_name, checked_html))
        return '\n'.join(ret)

class SelectWidget(forms.SelectField):
    def __init__(self, form_field):
        super(SelectWidget, self).__init__(form_field.field_name,
                                             form_field.choices,
                                             form_field.size,
                                             form_field.is_required,
                                             form_field.validator_list,
                                             getattr(form_field, 'member_name', None))
    def __repr__(self):
        return 'SelectWidget "%s"' % self.field_name

class NullSelectWidget(SelectWidget):
    "This SelectField converts blank fields to None"
    def __init__(self, form_field):
        super(NullSelectWidget, self).__init__(form_field)

    def html2python(data):
        if not data:
            return None
        return data
    html2python = staticmethod(html2python)

    def __repr__(self):
        return 'NullSelectWidget "%s"' % self.field_name

class  SelectMultipleWidget(forms.SelectMultipleField):
    def __init__(self, form_field):
        super(SelectMultipleWidget, self).__init__(form_field.field_name,
                                             form_field.choices,
                                             form_field.size,
                                             form_field.is_required,
                                             form_field.validator_list,
                                             getattr(form_field, 'member_name', None))
    def __repr__(self):
        return 'SelectMultipleWidget "%s"' % self.field_name

class FloatWidget(forms.FloatField):
    def __init__(self, form_field):
        super(FloatWidget, self).__init__(form_field.field_name,
                                          form_field.max_digits,
                                          form_field.decimal_places,
                                          form_field.is_required,
                                          form_field.validator_list)
    def __repr__(self):
        return 'FloatWidget "%s"' % self.field_name

class LargeTextWidget(forms.LargeTextField):
    def __init__(self, form_field):
        super(LargeTextWidget, self).__init__(form_field.field_name,
                                              form_field.rows,
                                              form_field.cols,
                                              form_field.is_required,
                                              form_field.validator_list,
                                              getattr(form_field, 'maxlength', None))
    def __repr__(self):
        return 'LargeTextWidget "%s"' % self.field_name
