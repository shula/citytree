# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.db import models
from django import forms
from django.template import Context, loader
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_detail as generic_object_detail
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

import settings
from utils.email import send_email_to
from workshop.models import Workshop, WorkshopEvent, ExternalParticipant
from cityblog.models import Flag, Post
from citytree.utils.hebCalView import FRONTPAGE_URL_TYPE, CALENDAR_URL_TYPE_REGISTRY

#------------  Registration to new workshops -------------------

def registerForm(workshop, workshop_event_id, request):

    workshop_events = WorkshopEvent.objects.all()
    if workshop is not None and workshop_event_id is None:
        workshop_events = workshop_events.filter(workshop=workshop)
    # TODO: better name for the workshop in the list (must make the user sure he is registering
    # to the right workshop).
    id_names_pairs = sorted([(unicode(w.id), unicode(w)) for w in workshop_events])
    initial = workshop_event_id or id_names_pairs[0][0]

    class UserRegisterForm(forms.Form):
        workshop_event = forms.ChoiceField(label='סדנה', choices= id_names_pairs, initial = initial)

    class ExternalParticipantRegisterForm(forms.ModelForm):
        #workshop = forms.ChoiceField(label='סדנה', choices=slugs_names_pairs, initial=initial)A
        class Meta:
            model = ExternalParticipant
    ExternalParticipantRegisterForm.base_fields['workshop_event'].empty_label = None
    ExternalParticipantRegisterForm.base_fields['workshop_event'].initial = initial

    post = request.method == 'POST' and request.POST or None
    clazz = request.user.is_authenticated() and UserRegisterForm or ExternalParticipantRegisterForm
    return clazz(post)

def register( request, workshop_slug = None, workshop_event_id = None ):
    participant = None # filled if unauthenticated and valid registration

    register_template = 'workshop/register.html'
    registration_complete_template = 'workshop/registration_complete.html'
    template = register_template

    if request.method == 'POST':
        post = request.POST.copy()
        workshop_event_id = post['workshop_event']
        workshop_event = get_object_or_404(WorkshopEvent, id=workshop_event_id)
        workshop = workshop_event.workshop
    else:
        if workshop_slug is not None:
            workshop = get_object_or_404(Workshop, slug=workshop_slug)
        else:
            workshop = None

    form = registerForm(workshop=workshop, workshop_event_id=workshop_event_id, request=request)

    def notify_on_registration(workshop_event, user_name, phone_number,
            email):
        send_email_to(template='workshop/user_registered_email.txt',
                to=settings.WORKSHOP_REGISTRATION_NOTIFICATION_EMAIL,
                subject="citytree: workshop %s, on the %s: '%s' registered" %
                    (workshop_event.workshop.name,
                     workshop_event.start_date.isoformat(),
                     user_name),
                context_dict = {
                    'user_name': user_name,
                    'workshop_event' : workshop_event,
                    'phone_number' : phone_number,
                    'email' : email,
                    },
                fail_silently = True)

    # we present one form for authenticated users, another for anonymous users:
    if request.user.is_authenticated():
        if request.method == 'GET':
            status = 'authenticated GET'
        elif request.method == 'POST':
            workshop_event.users.add(request.user)
            user = request.user
            phone = ''
            if hasattr(user, 'userprofile'):
                if hasattr(user.userprofile, 'phone'):
                    phone = user.userprofile.phone
            notify_on_registration(workshop_event,
                    user.get_full_name(),
                    phone_number=phone,
                    email=user.email)
            template = registration_complete_template
    else:
        if request.method == 'GET':
            status = 'anonymous GET'
        elif request.method == 'POST':
            if form.is_valid():
                participant = form.save()
                template = registration_complete_template
                notify_on_registration(workshop_event,
                        user_name='(external) %s' % participant.get_full_name(),
                        phone_number = participant.phone,
                        email = participant.email)

    return render_to_response(template,
            {
                'form':form,
                'participant':participant,
                'workshop':workshop,
                'blog':workshop.defining_post.blog, # used for header image in base_short_menu.html
            },
            context_instance=RequestContext(request))

# --------------- Display of existing workshops to users ----------------

def latest(request):
    # get workshops, sort by date, display using template
    raise NotImplemented()

def byday(request, day):
    # get day workshops, sort by hour, display using template (with different title)
    raise NotImplemented()

def display_workshop(request, workshop_slug, preview=False):

    # get workshop, get all workshopevents for it, get all workshopeventparts (ok - delegate)
    # render using template. add registration form at the bottom (reuse top - or just move it here)

    if( not preview ):
        workshop = get_object_or_404(Workshop, slug=workshop_slug, defining_post__draft=0)
    else:
        workshop = get_object_or_404(Workshop, slug=workshop_slug, defining_post__author=request.user.id )
      
    p = workshop.defining_post
    blog    = p.blog
    pImages = p.postimage_set.all().order_by( 'index' )
  
    #------------ Get List of flags in blog ---------
    flags = Flag.objects.filter( post__blog = blog.id ).filter( post__draft = 0 ).distinct()
      
    #------------ Create Objects for Hebrew Calender ----
    calLinkType     = FRONTPAGE_URL_TYPE
    calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
    return generic_object_detail(
        request,
        object_id = workshop.id, #p.id,
        queryset  = Workshop.objects.all(),
        template_name = "workshop/workshop.html",
        #context_processors =[calendar,bgColorProcessor],
        extra_context = { 'post':p, 'workshop':workshop, 'blog':blog,
            'flags':flags, 'galleryImages':pImages },
        template_object_name = 'post'
    )
 
