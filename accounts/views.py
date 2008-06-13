# -*- coding: utf-8 -*-

from django import newforms as forms
from django.db import models
from accounts.models import CapchaRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import django.newforms as forms
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.mail import send_mail
import settings

from utils.randomUtils import make_random_hash

class RegisterForm(forms.Form):
    username   = forms.CharField(label='שם משתמש', max_length=100)
    first_name = forms.CharField(label='שם פרטי', max_length=200)
    last_name  = forms.CharField(label='שם משפחה', max_length=200)
    email      = forms.EmailField(label='כתובת דואל', max_length=200)
    password   = forms.CharField(label='סיסמה', max_length=15, widget=forms.PasswordInput)
    capcha_response = forms.CharField(label='רשום את האותיות המופיעות מתחת', max_length=200)
    hash       = forms.CharField(max_length=200, widget=forms.HiddenInput)

def send_email_to(template, to, subject, context_dict):
    recipient_list = [to]
    t = loader.get_template(template)
    c = Context(context_dict)
    message = t.render(c)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

def create_account(request, hash=None):
    """hash is filled by the hidden input in the form - this is a hash into the
    CapchaRequest table to figure out if the user solved it correctly.
    """
    create_account_template = 'workshop/create_account.html'
    capcha = None # filled for GET - for POST it isn't rendered.
    if request.method == 'GET':
        form = RegisterForm()
        # fill in capcha
        hash = make_random_hash()
        form['hash'] = hash
        capcha_request = CapchaRequest()
        capcha_request.hash = hash
        capcha_request.letters = 
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            username = cleaned_data['username']
            password = cleaned_data['password']
            hash     = cleaned_data['hash']
            capcha_response = cleaned_data['capcha_response']
            capcha_request = get_object_or_404(CapchaRequest, hash=hash)
            if capcha_request.letters != capcha_response:
                form.errors['capcha_response']=[u'סליחה, התשובה לא מתקמפלת']
            if User.objects.filter(username=username).count() != 0:
                form.errors['username']=[u'שם המשתמש תפוס']
            if len(set(password))<4 or len(password) < 6:
                form.errors['password']=[u'ססמה חייבת להיות לפחות 6 תווים, 4 שונים לפחות.']
            if len(form.errors) == 0:
                email = form.cleaned_data['email']
                user = User.objects.create_user(username=username,
                        email=email,
                        password=password)
                user.first_name = cleaned_data['first_name']
                user.last_name = cleaned_data['last_name']
                user.save()
                cleaned_data['password'] = password
                send_email_to('workshop/create_acount_email.txt', email, 'פרטי חשבון עץ בעיר',
                            cleaned_data)
                return HttpResponseRedirect('/workshop/login/')
    return render_to_response(create_account_template,
            {
                'form':form,
            },
            context_instance=RequestContext(request))
    
def capcha_image(request, hash):
    # this way only this request fails if for some reason this import is missing or buggy
    from utils.hebrew_capcha import generate_capcha
    
    image_data = generate_capcha(letters)
    return HttpResponse(image_data, mimetype="image/png")

def profile(request):
    form = forms.form_for_instance(request.user)
    return render_to_response('accounts/profile.html', 
                {'user'       : request.user, 
                 'form'       : form
                 }, 
                context_instance=RequestContext(request))

profile = login_needed(profile)

