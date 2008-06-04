from datetime import datetime, date
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list as generic_object_list
from django.views.generic.list_detail import object_detail as generic_object_detail
from cityblog.models import blog, post, flag, subject
from frontpage.models import FrontPage
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from spamdetector.models import banned_ip, allowed_ban_requests

def ban_request( request, hash ):
  b = get_object_or_404(allowed_ban_requests, hash=hash)
  ip_address = b.ip_address
  banned_ip(ip_address=ip_address).save()
  b.delete()
  return render_to_response('spamdetector/ban_request_successful.html', {'ip_address': ip_address})
 
