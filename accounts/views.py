# -*- coding: utf-8 -*-

from django.db import models
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site

import settings
from accounts.models import CapchaRequest
from frontpage.views import show_front_page
from frontpage.models import FrontPage
from utils.randomUtils import make_random_hash
from utils.hebrew_capcha import get_random_hebrew_alphabet_string, generate_capcha
from utils.email import send_email_to


login_needed = user_passes_test(lambda u: u.is_authenticated(), login_url='/accounts/login/')

class LoginForm(forms.Form):
    username   = forms.CharField(label='שם משתמש', max_length=100)
    password   = forms.CharField(label='סיסמה', max_length=15, widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    username   = forms.CharField(label='שם משתמש', max_length=100)
    first_name = forms.CharField(label='שם פרטי', max_length=200)
    last_name  = forms.CharField(label='שם משפחה', max_length=200)
    email      = forms.EmailField(label='כתובת דואל', max_length=200)
    password   = forms.CharField(label='סיסמה', max_length=15, widget=forms.PasswordInput)
    optin_citytree_list = forms.BooleanField(required=False, label='הצטרפות לרשימת התפוצה של עץ בעיר')
    capcha_response = forms.CharField(label='רשום את האותיות המופיעות מתחת', max_length=200)
    hash       = forms.CharField(max_length=200, widget=forms.HiddenInput)

def new_capcha_request(form, reuse_hash=None):
    if reuse_hash:
        hash = reuse_hash
        capcha_request = CapchaRequest.objects.get(hash=hash)
    else:
        hash = make_random_hash()
        capcha_request = CapchaRequest()
    form['hash'].field.initial = hash
    capcha_request.hash = hash
    capcha_request.letters = get_random_hebrew_alphabet_string()
    capcha_request.save()
    return hash

def unicode_reverse(u):
    return ''.join(list(reversed(u)))

def password_check(password):
    return len(set(password)) >= 4 and len(password) >= 6

class SharedLoginRegister(object):
    
    def __init__(s):
        s.response = None
        s.template = create_account_template = 'accounts/login_and_register.html'
        s.user = None
        s.status = 'nothing'
        s.rform = None # registration
        s.lform = None # login
        s.hash = None
        s.first_time_user = False
 
    def register_new_account(s, request):
        registration_success_template = 'accounts/registration_success.html'
        s.rform = RegisterForm(request.POST, prefix="register")

        if not s.rform.is_valid():
            s.status = 'rform_not_valid'
            s.hash = request.POST['register-hash']
        else:
            cleaned_data = s.rform.cleaned_data
            # TODO: hash gets out of sync
            if cleaned_data['hash'] != request.POST['hash2']:
                import pdb
                pdb.set_trace()
            cleaned_data['hash'] = request.POST['hash2']
            username = cleaned_data['username']
            password = cleaned_data['password']
            s.hash     = cleaned_data['hash']
            capcha_response = cleaned_data['capcha_response']
            try:
                capcha_request = CapchaRequest.objects.get(hash=s.hash)
            except DoesNotExist:
                # known bug - try to work around it
                #s.response = HttpResponseRedirect('/accounts/login_and_register')
                s.status = 'capcha_request not found for %s' % s.hash
                return
            # ok - it's the reversed. But just in case something screwi happens - I'm
            # willing to cut search space in half.
            if capcha_request.letters not in [capcha_response, unicode_reverse(capcha_response)]:
                s.rform.errors['capcha_response'] = [u'סליחה, התשובה לא מתקמפלת']
                # reset capcha
                s.hash = new_capcha_request(s.rform, reuse_hash=s.hash) # yes, I reuse the hash for a different set of letters. Not really a problem I think? ok, it might be.
                #s.response = HttpResponseRedirect('/accounts/login_and_register/')
                return
            if User.objects.filter(username=username).count() != 0:
                s.rform.errors['username'] = [u'שם המשתמש תפוס']
            if not password_check(password):
                s.rform.errors['password'] = [u'ססמה חייבת להיות לפחות 6 תווים, 4 שונים לפחות.']
            if len(s.rform.errors) == 0:
                print "no errors in reg form"
                capcha_request.delete() # NOTE: only delete capcha if rest of form is ok. This means user doesn't have to resolve the capcha if the other information is wrong.
                email = s.rform.cleaned_data['email']
                user = User.objects.create_user(username=username,
                        email=email,
                        password=password)
                user.first_name = cleaned_data['first_name']
                user.last_name = cleaned_data['last_name']
                user.save()
                cleaned_data['password'] = password
                send_email_to('accounts/create_acount_email.txt', email, 'פרטי חשבון עץ בעיר',
                            cleaned_data)
                s.template = registration_success_template
                # login already
                user = authenticate(username=username, password=password)
                login(request, user)
            else:
                s.status = 'regfailed'

    def post_login_form(s, request):
        s.lform = LoginForm(request.POST, prefix='login')
        if s.lform.is_valid():
            cleaned_data = s.lform.cleaned_data
            user = authenticate(username=cleaned_data['username'],
                                password=cleaned_data['password'])
            if not user:
                s.status = 'failed'
            else:
                if user.is_active:
                    s.first_time_user = user.last_login == user.date_joined
                    login(request, user)
                    # check if this is a first time login
                    if request.user.is_authenticated() and s.first_time_user:
                        front_page = get_object_or_404(FrontPage, title=settings.NEW_MEMBERS_FRONTPAGE_TITLE)
                        s.response = show_front_page(request, front_page=front_page)
                    else:
                        # redirect normal users to frontpage
                        s.response = HttpResponseRedirect('/')
                else:
                    s.status = 'failed' # TODO: seperate message for non active users?
        else:
            s.status = 'lform_not_valid'

    def new_reg_form(s):
        s.rform = RegisterForm(prefix='register')
        s.hash = new_capcha_request(s.rform)

    def new_login_form(s):
        s.lform = LoginForm(prefix='login')

    def process(s, request):
        """ This is both a login and a registration page. It contains two forms. It handles possiblility
        of either being filled. Not sure if this is normal, or even makes sense, but let's do it cause Tami asked!
        
        hash is filled by the hidden input in the form - this is a hash into the
        CapchaRequest table to figure out if the user solved it correctly.
        """
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')

        if request.method == 'GET':
            s.new_login_form()
            s.new_reg_form()
        else: # POST
            if request.GET.has_key('login'):
                s.post_login_form(request)
                s.new_reg_form()
            else: # register form
                s.register_new_account(request)
                s.new_login_form()

        if s.response is not None:
            return s.response

        site = Site.objects.get_current().name
        #site='citytree.saymoo.org:9192' # TODO!!! change back to above line before commit.
        # NOTE: media_url is used heavily in the templates (specifically all css is gone if it evaluates to none.
        #  It only works if the context_instance attribute is a RequestContext (instead of the default Context).
        # TODO: This (above note) is annoying. Is there a way to make this normal?
        return render_to_response(s.template,
                {
                    'status':s.status,
                    'lform':s.lform,
                    'rform':s.rform,
                    'hash':s.hash,
                    'site':site
                 # TODO:  'next':'something here'
                },
                context_instance=RequestContext(request))
 

def login_and_register(request):
    return SharedLoginRegister().process(request)
   
def capcha_image(request, hash):
    capcha_request = get_object_or_404(CapchaRequest, hash=hash)
    image_data = generate_capcha(capcha_request.letters)
    return HttpResponse(image_data, mimetype="image/png")

class UserForm(forms.ModelForm):
    #post_date = forms.DateField(widget = forms.widgets.SplitDateTimeWidget())
    username = forms.CharField(label='שם משתמש (כינוי)')
    first_name = forms.CharField(label='שם פרטי')
    last_name = forms.CharField(label = 'שם משפחה')
    email = forms.EmailField(label = 'דואל')
    old_password = forms.CharField(label='סיסמה ישנה', required=False, widget=forms.PasswordInput)
    new_password_1 = forms.CharField(label='סיסמה חדשה', required=False, widget=forms.PasswordInput)
    new_password_2 = forms.CharField(label='שוב סיסמה חדשה', required=False, widget=forms.PasswordInput)
    class Meta:
        model = User
        #fields = ('first_name', 'last_name', 'email', 'password')
        fields = ('username', 'first_name', 'last_name', 'email')

def profile(request):
    # sucks: only about 5 fields that should actually be shown,
    # need hebrew help text for those.
    if request.method == 'GET':
        form = UserForm(instance=request.user)
    elif request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            # check for password change
            data = form.cleaned_data
            new1, new2 = data['new_password_1'], data['new_password_2']
            if not request.user.check_password(data['old_password']):
                form.errors['old_password']=[u'ססמה מוטעית, נסו שנית']
            elif (new1 != '' or new2 != '') and new1 != new2:
                form.errors['new_password_1'] = [u'הססמאות החדשות לא תואמות']
            elif not password_check(new1):
                form.errors['new_password_1'] = [u'הססמה החדשה לא לפחות באורך 6 ועם 4 אותיות שונות']
            else:
                form.save()
                request.user.set_password(new1)
                request.user.save()
    return render_to_response('accounts/profile.html', 
                {'user'       : request.user, 
                 'form'       : form
                 }, 
                context_instance=RequestContext(request))

profile = login_needed(profile)

def userhome(request):
    return render_to_response('accounts/userhome.html', {},
            context_instance=RequestContext(request))

