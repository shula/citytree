# -*- coding: utf-8 -*-

from django.core.mail import send_mail, BadHeaderError
from django.template import Context, loader
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
import settings

DUPLICATE_ERROR = 'duplicate error'
EMAIL_ERROR = 'email_error'
SUCCESS_ERROR = 'success'

def register_new_user(donor, really_send_email=False):
    email = str(donor['email'])
    if User.objects.filter(email=email).count() != 0:
        return DUPLICATE_ERROR

    try:
        password = User.objects.make_random_password(6)
        user = User.objects.create_user(username=email, email=email, password=password)
        first_name = donor['first']
        last_name = donor['last']
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        t = loader.get_template('accounts/litrom_newuser_email.txt')
        site = Site.objects.get_current().name
        c = Context({ 'site': site,
                      'first': donor['first'],
                      'last': donor['last'],
                      'email': email,
                      'password': password})
        subject = u'תודה שתרמתם לעץבעיר!'
        message = t.render(c)
        
        if not really_send_email:
            email = 'alonlevy1@gmail.com'

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except BadHeaderError:
        return EMAIL_ERROR
    return SUCCESS_ERROR

