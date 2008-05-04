#from django import forms
#from widgets import widget_factory
#
#class FormWrapper(forms.FormWrapper):
#    def __getitem__(self, key):
#        for field in self.manipulator.fields:
#            if field.field_name == key:
#                data = field.extract_data(self.data)
#                return FormWidgetWrapper(field, data, self.error_dict.get(field.field_name, []))
#        if self.edit_inline:
#            self.fill_inline_collections()
#            for inline_collection in self._inline_collections:
#                if inline_collection.name == key:
#                    return inline_collection
#        raise KeyError, "Could not find Formfield or InlineObjectCollection named %r" % key
#
#class FormWidgetWrapper(forms.FormFieldWrapper):
#    "A bridge between the template system and an individual form field. Used by FormWrapper."
#    def __init__(self, formfield, data, error_list):
#        self.data, self.error_list = data, error_list
#        self.formfield = widget_factory(formfield)
#        self.field_name = self.formfield.field_name # for convenience in templates
#        
#    def __repr__(self):
#        return '<FormWidgetWrapper for "%s">' % self.formfield.field_name
