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

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from cityblog.models import post, blog

class Workshop(models.Model):
    name        =   models.CharField('workshop name', max_length=200, blank=False)
    slug        =   models.SlugField(verbose_name='workshop url identifier', unique=True)
    description =   models.TextField(blank=True, null=True, help_text='single line description')
    defining_post = models.ForeignKey( post, blank=True, null=True, help_text='Defining post where this workshop is written about. ' )
    owners      =   models.ManyToManyField(User, related_name='owned_workshop_set',
                    help_text='future - allow these people to change workshop details',
                    verbose_name='workshop owners', blank=True,
                    filter_interface=models.HORIZONTAL)

    def get_events(self):
        return self.workshopevent_set.order_by('workshopeventpart__start_time')
    events = property(get_events)
    
    def get_next_event(self):
        try:
            return self.workshopevent_set.order_by('workshopeventpart__start_time')[0]
        except:
            return None
    next_event = property(get_next_event)

    def next_event_date(self):
        try:
            return self.events[0].parts[0].start_time.date()
        except:
            return None

    @staticmethod
    def create_workshop_by_post(post):
        if Workshop.objects.count() == 0:
            maxid = 0
        else:
            maxid = Workshop.objects.order_by('-id')[0].id
        workshop = Workshop.objects.create(slug='unnamed_%s' % (maxid+1))
        return workshop

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return u'/workshop/%s/' % self.slug

    def get_add_event_absolute_url(self):
        return u'/desk/workshop/%s/addEvent' % self.slug

    def get_header_image_absolute_url(self):
        return self.defining_post.blog.get_header_image_url()

    class Admin:
        list_filter    = ('owners',)

class BlogWorkshop(models.Model):
    
    """ The dillema is wether to use the existing blog table or not. Decided
    to keep the workshop application seperate table wise too. So this table
    will contain any information that is blog instance specific but workshop related.

    Currently that is just: is this blog a workshop blog - a blog were all posts
    are actually workshops. The implementation is basically to keep the post
    mechanism but to find have a related workshop instance. The allows the "gallery"
    part of the workshop to be implemented in the post logic, which already knows how to
    do that. Not sure if that makes sense or not yet. comments are another thing - this way
    comments are still related to the post, which is just also related to a workshop.
    """

    blog              = models.ForeignKey(blog, edit_inline=models.STACKED,
            core=True, unique=True, num_in_admin=1,min_num_in_admin=1, max_num_in_admin=1,num_extra_on_change=0)
    is_workshops_blog = models.BooleanField("Is this a workshop blog")

    def save(self):
        super(BlogWorkshop, self).save()

    class Admin:
        pass

class WorkshopEvent(models.Model):
    # question: how do I easily allow structured and unstructured together? I want
    # to have both free text and also site users in the instructors field - how do
    # I do that easily (i.e. without creating two seperate fields I'll have to keep checking?
    # TODO: answer - create my own field!. Not now)
    instructors =   models.CharField('name of instructors', max_length=200, blank=False)
    contact     =   models.EmailField('email of point of contact for questions', blank=False)
    location    =   models.CharField('location of workshop', max_length=200, blank=False)
    workshop    =   models.ForeignKey(Workshop, verbose_name='סדנה', blank=False)
    users       =   models.ManyToManyField(User, related_name='registered_workshopevent_set',
                    verbose_name='registered site users', blank=True,
                    filter_interface=models.HORIZONTAL)

    class Admin:
        pass

    def __unicode__(self):
        return u'%s %s' % (unicode(self.workshop), self.get_start_date() or self.id)

    def get_start_date(self):
        if self.workshopeventpart_set.count() == 0:
            return None
        return self.workshopeventpart_set.order_by('start_time')[0].start_time.date()
    start_date = property(get_start_date)

    def get_end_date(self):
        if self.workshopeventpart_set.count() == 0:
            return None
        return self.workshopeventpart_set.order_by('-start_time')[0].start_time.date()
    end_date = property(get_end_date)

    def get_eventparts(self):
        return self.workshopeventpart_set.order_by('start_time')
    parts = property(get_eventparts)

    def get_new_event_dict(self):
        """ Return a dictionary with fields suitable to fill a new WorkshopEvent form,
        based on the values in this instance
        """
        return dict([(f, getattr(self, f)) for f in ['instructors', 'location', 'contact']])

    def get_edit_absolute_url(self):
        return u"/desk/workshop/%s/editEvent/%s/" % (self.workshop.slug, self.id)

    def get_registration_absolute_url(self):
        return u"/workshop/register/%s/%s/" % (self.workshop.slug, self.id)

    def save(self):
        # no WorkshopEvent can exist without at least one WorkshopEventPart.
        # rationalization: it makes my coding easier, and it actually makes sense - what's the
        # point of a non-event event?
        if self.id is None:
            super(WorkshopEvent, self).save()
        if self.workshopeventpart_set.count() == 0:
            wsep = WorkshopEventPart()
            wsep.workshop_event = self
            wsep.start_time = datetime.now()
            wsep.end_time = datetime.now()
            wsep.save()
        super(WorkshopEvent, self).save() # really needed?
        print "saving WorkshopEvent id=%s" % self.id

class WorkshopEventPart(models.Model):
    workshop_event = models.ForeignKey(WorkshopEvent, verbose_name='מופע הסדנה', blank=False)
    start_time     = models.DateTimeField()
    end_time       = models.DateTimeField() # TODO: any TimeSpanField ? or maybe TimeAndDateSpan - superb for a calendar..

    def __unicode__(self):
        return u'%s %s' % (self.workshop_event.workshop, self.start_time)

    class Admin:
        pass

    class Meta:
        ordering = ['-start_time']

class ExternalParticipant(models.Model):
    """ A Participant that isn't a registered user of the site. No support for the same
    participant registering to multiple workshops, or actually any history whatsoever. 
    Basically that means we'll have to deal with double (or triple, or more!) registrations
    from people hitting the submit, then going back, then again. Oh fun!
    """
    first_name      =   models.CharField(verbose_name='שם פרטי', max_length=200, blank=False)
    last_name       =   models.CharField(verbose_name='שם משפחה', max_length=200, blank=False)
    email           =   models.EmailField(verbose_name='כתובת דואל', max_length=200, blank=True)
    phone           =   models.CharField(verbose_name='מספר טלפון', max_length=200, blank=True)
    workshop_event  =   models.ForeignKey(WorkshopEvent, verbose_name='מופע הסדנה', blank=False)

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Admin:
        list_filter    = ('workshop_event',)

