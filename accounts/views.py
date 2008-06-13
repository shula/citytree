# -*- coding: utf-8 -*-

from django.db import models
from django import newforms as forms
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.mail import send_mail
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site

import settings
from accounts.models import CapchaRequest
from utils.randomUtils import make_random_hash
from utils.hebrew_capcha import get_random_hebrew_alphabet_string, generate_capcha

login_needed = user_passes_test(lambda u: u.is_authenticated(), login_url='/accounts/login/')

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

def new_capcha_request(form):
    hash = make_random_hash()
    form['hash'].field.initial = hash
    capcha_request = CapchaRequest()
    capcha_request.hash = hash
    capcha_request.letters = get_random_hebrew_alphabet_string()
    capcha_request.save()
    return hash

def unicode_reverse(u):
    return ''.join(list(reversed(u)))

def create_account(request):
    """hash is filled by the hidden input in the form - this is a hash into the
    CapchaRequest table to figure out if the user solved it correctly.
    """
    create_account_template = 'accounts/create_account.html'
    if request.method == 'GET':
        form = RegisterForm()
        hash = new_capcha_request(form)
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            username = cleaned_data['username']
            password = cleaned_data['password']
            hash     = cleaned_data['hash']
            capcha_response = cleaned_data['capcha_response']
            capcha_request = get_object_or_404(CapchaRequest, hash=hash)
            # ok - it's the reversed. But just in case something screwi happens - I'm
            # willing to cut search space in half.
            if capcha_request.letters not in [capcha_response, unicode_reverse(capcha_response)]:
                form.errors['capcha_response']=[u'סליחה, התשובה לא מתקמפלת']
                # reset capcha
                # TODO: this is no good right now. There is an extra GET generated after
                # a failed POST, I can't figure out why. But the upshot is that
                # I have one hash in the form, and another in the link. And the form is still
                # with the old value. So for now, just redirect.
                capcha_request.delete() # make sure it isn't used twice.
                return HttpResponseRedirect('/accounts/create_account')
                #hash = new_capcha_request(form)
            capcha_request.delete() # or set a flag success or not, store ip? nah
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
                send_email_to('accounts/create_acount_email.txt', email, 'פרטי חשבון עץ בעיר',
                            cleaned_data)
                return HttpResponseRedirect('/accounts/registration_success')
        else:
            import pdb
            pdb.set_trace()
        
    site = Site.objects.get_current().name
    #site='citytree.saymoo.org:9192' # TODO!!! change back to above line before commit.
    return render_to_response(create_account_template,
            {
                'form':form,
                'hash':hash,
                'site':site
            },
            context_instance=RequestContext(request))
    
def registration_success(request):
    return render_to_response('accounts/registration_success.html')

def capcha_image(request, hash):
    capcha_request = get_object_or_404(CapchaRequest, hash=hash)
    image_data = generate_capcha(capcha_request.letters)
    return HttpResponse(image_data, mimetype="image/png")

class UserForm(forms.ModelForm):
    #post_date = forms.DateField(widget = forms.widgets.SplitDateTimeWidget())
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')

def profile(request):
    # sucks: only about 5 fields that should actually be shown,
    # need hebrew help text for those.
    if request.method == 'GET':
        form = UserForm(instance=request.user)
    elif request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    return render_to_response('accounts/profile.html', 
                {'user'       : request.user, 
                 'form'       : form
                 }, 
                context_instance=RequestContext(request))

profile = login_needed(profile)

