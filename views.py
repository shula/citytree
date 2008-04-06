"""
Django doesn't suggest putting views in a site level directory, but
rather in an application container, and supports this through the manage.py
tool.

So here are only things which don't logically belong to any app.

Currently only one thing: the uptime service from http://uptime.openacs.org/
requires that we have a single url that returns a document consisting of a
single word "success". The function uptime_openacs with another line in urls.py
take care of this.
"""

from datetime import datetime, date
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.template import RequestContext
from frontpage.views import show_front_page

def uptime_openacs(request):
    # we want to do this work - if it works then the site should
    # be generally ok.
    try:
        garbage = show_front_page(request)
    except e:
        return HttpResponse(str(e))
    return HttpResponse("success")

