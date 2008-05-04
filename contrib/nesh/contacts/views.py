from django.shortcuts import get_object_or_404
from models import *
from nesh.utils.json import JSONResponse, response_from_filter
from nesh.utils.log import db_log, ADDITION
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import create_update, list_detail
from django.template import RequestContext as Context
from django.db import transaction
from django.forms import FormWrapper

def json_countries(request):
    """ return all countries in format [[PK, __str___],...] """
    return response_from_filter(Country.objects.all()) #IGNORE:E1101

def json_cities(request, country=None):
    """ return all cities for given country in format [[PK, __str___],...] """
    if country is None:
        filter = City.objects.all() #IGNORE:E1101
    else:
        filter = City.objects.filter(country=country) #IGNORE:E1101
    return response_from_filter(filter)

def json_contacts(request, country=None, city=None):
    """ return all contacts for given country and city in format [[PK, __str___],...] """
    exclude = request.GET.get('exclude_by', None)
    contacts = Contact.objects.all() #IGNORE:E1101
    if country is not None and int(country):
        contacts = contacts.filter(country=country)
    if city is not None and int(city):
        contacts = contacts.filter(city=city)
    if exclude is not None and int(exclude):
        contacts = contacts.exclude(id=exclude)
    return response_from_filter(contacts)