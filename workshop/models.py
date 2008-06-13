# -*- coding: utf-8 -*-

""" Basically the model is:
    Workshop
    ^
    |
    WorkshopEvent
    ^
    |-------------------------\
    |                         |
    WorkshopEventPart       ExternalParticipant
"""

from django.db import models
from django.contrib.auth.models import User
from cityblog.models import post

class Workshop(models.Model):
    name        =   models.CharField('workshop name', max_length=200, blank=False)
    slug        =   models.SlugField(verbose_name='workshop url identifier', unique=True)
    description =   models.TextField(blank=True, null=True, help_text='single line description')
    defining_post = models.ForeignKey( post, blank=True, null=True, help_text='Defining post where this workshop is written about. ' )
    owners      =   models.ManyToManyField(User, related_name='owned_workshop_set',
                    help_text='future - allow these people to change workshop details',
                    verbose_name='workshop owners', blank=True,
                    filter_interface=models.HORIZONTAL)

    def __unicode__(self):
        return self.name

    class Admin:
        list_filter    = ('owners',)

class WorkshopEvent(models.Model):
    # question: how do I easily allow structured and unstructured together? I want
    # to have both free text and also site users in the instructors field - how do
    # I do that easily (i.e. without creating two seperate fields I'll have to keep checking?
    # TODO: answer - create my own field!. Not now)
    instructors =   models.CharField('name of instructors', max_length=200, blank=False)
    workshop    =   models.ForeignKey(Workshop, verbose_name='סדנה', blank=False)
    users       =   models.ManyToManyField(User, related_name='registered_workshopevent_set',
                    verbose_name='registered site users', blank=True,
                    filter_interface=models.HORIZONTAL)

class WorkshopEventPart(models.Model):
    workshop_event = models.ForeignKey(WorkshopEvent, verbose_name='מופע הסדנה', blank=False)
    date           = models.DateField()
    start_time     = models.TimeField()
    end_time       = models.TimeField() # TODO: any TimeSpanField ? or maybe TimeAndDateSpan - superb for a calendar..

class ExternalParticipant(models.Model):
    """ A Participant that isn't a registered user of the site. No support for the same
    participant registering to multiple workshops, or actually any history whatsoever. 
    Basically that means we'll have to deal with double (or triple, or more!) registrations
    from people hitting the submit, then going back, then again. Oh fun!
    """
    first_name      =   models.CharField(verbose_name='שם פרטי', max_length=200, blank=False)
    last_name       =   models.CharField(verbose_name='שם משפחה', max_length=200, blank=False)
    email           =   models.EmailField(verbose_name='כתובת דואל', max_length=200, blank=False)
    phone           =   models.PositiveIntegerField(verbose_name='מספר טלפון', blank=True, null=True)
    workshop_event  =   models.ForeignKey(WorkshopEvent, verbose_name='מופע הסדנה', blank=False)

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Admin:
        list_filter    = ('workshop_event',)

