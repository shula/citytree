# -*- coding: utf-8 -*-

from django import newforms as forms
from django.db import models
from accounts.models import 
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import django.newforms as forms
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.mail import send_mail
import settings

def registerForm(default_workshop, request):

    initial = default_workshop is not None and default_workshop.id or id_names_pairs[0][0]

    workshops = Workshop.objects.all()
    id_names_pairs = sorted([(unicode(w.id), w.name) for w in workshops])

    class UserRegisterForm(forms.Form):
        workshop=forms.ChoiceField(label='סדנה', choices= id_names_pairs, initial = initial)

    class ExternalParticipantRegisterForm(forms.ModelForm):
        #workshop = forms.ChoiceField(label='סדנה', choices=slugs_names_pairs, initial=initial)
        class Meta:
            model = ExternalParticipant
    ExternalParticipantRegisterForm.base_fields['workshop'].empty_label = None
    ExternalParticipantRegisterForm.base_fields['workshop'].initial = initial

    post = request.method == 'POST' and request.POST or None
    clazz = request.user.is_authenticated() and UserRegisterForm or ExternalParticipantRegisterForm
    return clazz(post)

def register( request, workshop_slug = None ):
    participant = None # filled if unauthenticated and valid registration

    register_template = 'workshop/register.html'
    registration_complete_template = 'workshop/registration_complete.html'
    template = register_template

    if request.method == 'POST':
        post = request.POST.copy()
        workshop_id = post['workshop']
        workshop = get_object_or_404(Workshop, id=workshop_id)
    else:
        if workshop_slug is not None:
            workshop = get_object_or_404(Workshop, slug=workshop_slug)
            if request.method == 'POST':
                post['workshop_id'] = workshop.id
        else:
            workshop = None

    form = registerForm(default_workshop = workshop, request = request)

    # we present one form for authenticated users, another for anonymous users:
    if request.user.is_authenticated():
        if request.method == 'GET':
            status = 'authenticated GET'
        elif request.method == 'POST':
            workshop.users.add(request.user)
            template = registration_complete_template
    else:
        if request.method == 'GET':
            status = 'anonymous GET'
        elif request.method == 'POST':
            if form.is_valid():
                participant = form.save()
                template = registration_complete_template

    return render_to_response(template,
            {
                'form':form,
                'participant':participant
            },
            context_instance=RequestContext(request))

class RegisterForm(forms.Form):
    username   = forms.CharField(label='שם משתמש', max_length=100)
    first_name = forms.CharField(label='שם פרטי', max_length=200)
    last_name  = forms.CharField(label='שם משפחה', max_length=200)
    email      = forms.EmailField(label='כתובת דואל', max_length=200)
    password   = forms.CharField(labell='סיסמה', max_length=15, widget=forms.PasswordInput)
    #capcha_response = forms.CharField(label='רשום את האותיות המופיעות מתחת', max_length=200)

def send_email_to(template, to, subject, context_dict):
    recipient_list = [to]
    t = loader.get_template(template)
    c = Context(context_dict)
    message = t.render(c)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

def create_account(request):
    create_account_template = 'workshop/create_account.html'
    if request.method == 'GET':
        form = RegisterForm()
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            username=cleaned_data['username']
            password = form.cleaned_data['password']
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
                #'capcha':capcha,
            },
            context_instance=RequestContext(request))
    
def capcha_image(request, seed=None):
    # this way only this request fails if for some reason this import is missing or buggy
    from utils.hebrew_capcha import generate_capcha
    image_data = generate_capcha()
    return HttpResponse(image_data, mimetype="image/png")

def profile(request):
    form = forms.form_for_instance(request.user)
    return render_to_response('accounts/profile.html', 
                {'user'       : request.user, 
                 'form'       : form
                 }, 
                context_instance=RequestContext(request))

profile = login_needed(profile)

