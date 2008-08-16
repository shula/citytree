# -*- coding: utf-8 -*-

from django.core.mail import send_mail, BadHeaderError
from django.template import Context, loader
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

import settings
from cityblog.models import Blog
from accounts.models import Member

DUPLICATE_ERROR = 'duplicate error'
EMAIL_ERROR = 'email_error'
SUCCESS_ERROR = 'success'
DEMO_ERROR = 'demo success'

def register_new_user(donor, really_send_email=False):
    email = str(donor['email'])
    user_exists = User.objects.filter(email=email).count() != 0
    members_blogs = Blog.objects.filter(member_blog=True)
    if user_exists and really_send_email:
        return DUPLICATE_ERROR

    try:
        if not user_exists:
            password = User.objects.make_random_password(6)
            if really_send_email:
                user = Member.create_member(username=email, email=email, password=password,
                        )
                first_name = donor['first']
                last_name = donor['last']
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                for b in member_blogs:
                    user.blog_set.add(b)
                user.save()
        else:
            user = User.objects.get(email=email)
            password = 'user already exists - hope you know it!'

        t = loader.get_template('accounts/litrom_newuser_email.txt')
        site = Site.objects.get_current().name
        c = Context({ 'site': site,
                      'first': user.first_name,
                      'last': user.last_name,
                      'email': email,
                      'password': password})
        subject = u'תודה שאמרת כן להצעת החברות שלנו!'
        message = t.render(c)
        
        if not really_send_email:
            email = 'alonlevy1@gmail.com'

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except BadHeaderError:
        return EMAIL_ERROR
    if not really_send_email:
        send_mail('got one', email, settings.DEFAULT_FROM_EMAIL, ['tamizori@gmail.com'], fail_silently=True)
    if really_send_email:
        return SUCCESS_ERROR
    return DEMO_ERROR

