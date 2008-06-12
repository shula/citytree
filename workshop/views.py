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

def latest(request):
    raise NotImplemented()

def byday(request, day):
    raise NotImplemented()

def workshop(request, slug):
    raise NotImplemented()


