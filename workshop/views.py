# -*- coding: utf-8 -*-

from django import newforms as forms
from django.db import models
from workshop.models import Workshop, ExternalParticipant
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import django.newforms as forms
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.mail import send_mail
import settings

#------------  Registration to new workshops -------------------

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

# --------------- Display of existing workshops to users ----------------

def latest(request):
    # get workshops, sort by date, display using template
    raise NotImplemented()

def byday(request, day):
    # get day workshops, sort by hour, display using template (with different title)
    raise NotImplemented()

def workshop(request, slug):
    # get workshop, get all workshopevents for it, get all workshopeventparts (ok - delegate)
    # render using template. add registration form at the bottom (reuse top - or just move it here)
    raise NotImplemented()

