# Copyright (c) 2007 Brandon Low
# Licensed under the GPL v2
from django import forms
from django.forms.util import flatatt,ValidationError
from models import Captcha
from settings import BASE_URL, MIN_LENGTH, MAX_LENGTH
from util import get_string

#------------------------------------------------------------------------------ 
class CaptchaWidget(forms.TextInput):

    def __init__(self, captcha=None, *args, **kwargs):
        self.captcha_id = captcha.id
        super(CaptchaWidget, self).__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        value = super(CaptchaWidget, self).render(*args, **kwargs)

        # I'd rather have this in the label, but they aren't per-instance
        img_src = "/".join([BASE_URL, str(self.captcha_id),""])
        image = "<img src='%s' alt='Captcha' />" % img_src
        return " ".join([image, value])

#------------------------------------------------------------------------------ 
class CaptchaField(forms.CharField):

    def __init__(self, captcha=None, *args, **kwargs):
        self.captcha = captcha
        self.widget = CaptchaWidget(captcha=captcha)
        # CharField takes care of setting the max length onto the widget
        super(CaptchaField, self).__init__(min_length=MIN_LENGTH,
                max_length=MAX_LENGTH, *args, **kwargs)

    def clean(self, value):
        value = super(CaptchaField, self).clean(value)
        if not self.captcha.text.lower() == value.lower():
            raise ValidationError(u'Enter the string exactly as shown')
        return value

#------------------------------------------------------------------------------ 
class CaptchaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CaptchaForm, self).__init__(*args, **kwargs)

        # The super.__init__ call does not actually set the data or initial
        # onto the fields/widgets, so we just need the captcha_id field and
        # widget to exist before self.get_captcha() is called
        self.fields['captcha_id'] = forms.IntegerField()
        self.fields['captcha_id'].widget = forms.HiddenInput()
        
        if not self.is_bound:
            # New form, new captcha
            c = Captcha(text=get_string())
            c.save()
            # Ensure that the hidden field is properly populated
            self.initial['captcha_id'] = c.id
        else:
            c = self.get_captcha()

        self.fields['captcha'] = CaptchaField(label="Turing test", captcha=c)

    #------------------------------------------------------------------------------ 
    # Only called on a bound form
    def get_captcha(self):
        # Somewhat hacky, but best way I had to get the captcha id
        f = self.fields['captcha_id']
        w = f.widget
        
        #value = w.value_from_datadict(self.data, None, self.add_prefix('captcha_id'))
        #make it work in 0.96, where value_from_datadict() have 2 arguments
        value = w.value_from_datadict(self.data, self.add_prefix('captcha_id'))
        
        captcha_id = f.clean(value)

        try:
            # Always clean expired captchas before getting one for validation
            Captcha.clean_expired()
            return Captcha.objects.get(pk=captcha_id)
        except Captcha.DoesNotExist:
            # The original captcha expired, make a new one for revalidation
            c = Captcha(id=captcha_id,text=get_string())
            c.save()
            return c

    #------------------------------------------------------------------------------ 
    def full_clean(self):
        super(CaptchaForm, self).full_clean()

        # Once the form has validated, the captcha is 'used up'
        if self.is_valid():
            self.fields['captcha'].captcha.delete()
