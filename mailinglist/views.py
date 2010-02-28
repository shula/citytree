# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django.contrib.sites.models import Site

from mailinglist.models import MailingListSubscriber
from utils.randomUtils import make_random_hash
from utils.email import check_email, send_email_to

# TODO - move this somewhere, make sure frontpage uses it too. (and
# anywhere else a calendar is shown. In fact, this should be middleware).
def create_calendar_context_params():
  from citytree.utils.hebCalView import (FRONTPAGE_URL_TYPE,
    CALENDAR_URL_TYPE_REGISTRY, makeHebBGColorProcessor,
        makeHebCalRequestContext, makeHebCalLinks)
  import workshop.util as workshop_util
  #------------ Create Objects for Hebrew Calender ----
  calLinkType     = FRONTPAGE_URL_TYPE
  calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
  dateToShow = date.today()

  bgColorProcessor = makeHebBGColorProcessor( dateToShow )
  dayLinks = makeHebCalLinks( calLinkTemplate, engDate=dateToShow )
  workshopLinks = workshop_util.makeHebCalLinks(dateToShow)
  dayLinks.update(workshopLinks)
  calender = makeHebCalRequestContext(dayLinks, engDate=dateToShow, 
                   urlType=calLinkType,highlightToday=True)
  #def debugme(*args, **kw):
  #  import pdb; pdb.set_trace()
  #  return calendar(*args, **kw)
  return [calender, bgColorProcessor]
  
def join(request):
    """ render the join to mailing list page """
#map={'1':'fn','2':'ln','8':'ly','10':'lw','9':'lc','11':'com','21':'vol','16':'tel','19':'cel','17':'add','18':'job','23':'note'};
    d =  {'site': Site.objects.get_current().name,
          'email':request.GET.get('email',request.GET.get('q',request.GET.get('eMail',''))),
          'fn':unicode(request.GET.get('fn',request.GET.get('1',''))),
          'ln':unicode(request.GET.get('ln',request.GET.get('2',''))),
          'tel':request.GET.get('tel',request.GET.get('16','')),
          'cel':request.GET.get('cel',request.GET.get('19','')),
          'job':request.GET.get('job',request.GET.get('18','')),
          'note':request.GET.get('note',request.GET.get('23','')),
          'addr':request.GET.get('addr',request.GET.get('17','')),
          'ly':request.GET.get('ly',request.GET.get('8','1')),
          'lw':request.GET.get('lw',request.GET.get('10','1')),
          'lc':request.GET.get('lc',request.GET.get('9','')),
          'com':request.GET.get('com',request.GET.get('11','')),
          'vol':request.GET.get('vol',request.GET.get('21','')),
    }
    chk = 'checked selected'
    if (d['ly']=='1'):
        d['ly1']=chk
    if (d['ly']=='0'):
        d['ly0']=chk
    if (d['lw']=='1'):
        d['lw1']=chk
    if (d['lw']=='0'):
        d['lw0']=chk
    if (d['lc']=='1'):
        d['lc1']=chk
    if (d['lc']=='0'):
        d['lc0']=chk
    if (d['com']=='1'):
        d['com1']=chk
    if (d['com']=='0'):
        d['com0']=chk
    if (d['vol']=='1'):
        d['vol1']=chk
    if (d['vol']=='0'):
        d['vol0']=chk

    return render_to_response('mailinglist/join.html',d
        ,context_instance=RequestContext(
            request, {}, create_calendar_context_params()))

def joinerror(request):
    """ render the join to mailing list page """
    return render_to_response('mailinglist/join_error.html'
        ,{'site': Site.objects.get_current().name}
        ,context_instance=RequestContext(
            request, {}, create_calendar_context_params()))

def joindone(request):
    d =  {'site': Site.objects.get_current().name,
          'email':request.GET.get('email',request.GET.get('q',request.GET.get('eMail',''))),
          'fn':request.GET.get('fn',request.GET.get('1','')),
          'ln':request.GET.get('ln',request.GET.get('2','')),
          'tel':request.GET.get('tel',request.GET.get('16','')),
          'cel':request.GET.get('cel',request.GET.get('19','')),
          'job':request.GET.get('job',request.GET.get('18','')),
          'note':request.GET.get('note',request.GET.get('23','')),
          'addr':request.GET.get('addr',request.GET.get('17','')),
          'ly':request.GET.get('ly',request.GET.get('8','1')),
          'lw':request.GET.get('lw',request.GET.get('10','1')),
          'lc':request.GET.get('lc',request.GET.get('9','')),
          'com':request.GET.get('com',request.GET.get('11','')),
          'vol':request.GET.get('vol',request.GET.get('21','')),
    }
    return render_to_response('mailinglist/join_done.html'
        ,d
        ,context_instance=RequestContext(
            request, {}, create_calendar_context_params()))
def unjoin(request):
    d =  {'site': Site.objects.get_current().name,
          'email':request.GET.get('email',request.GET.get('q',request.GET.get('eMail',''))),
          'fn':request.GET.get('fn',request.GET.get('1','')),
          'ln':request.GET.get('ln',request.GET.get('2','')),
          'tel':request.GET.get('tel',request.GET.get('16','')),
          'cel':request.GET.get('cel',request.GET.get('19','')),
          'job':request.GET.get('job',request.GET.get('18','')),
          'note':request.GET.get('note',request.GET.get('23','')),
          'addr':request.GET.get('addr',request.GET.get('17','')),
          'ly':request.GET.get('ly',request.GET.get('8','1')),
          'lw':request.GET.get('lw',request.GET.get('10','1')),
          'lc':request.GET.get('lc',request.GET.get('9','')),
          'com':request.GET.get('com',request.GET.get('11','')),
          'vol':request.GET.get('vol',request.GET.get('21','')),
    }
    return render_to_response('mailinglist/remove.html'
        ,d
        ,context_instance=RequestContext(
            request, {}, create_calendar_context_params()))

def unjoinok(request):
    return render_to_response('mailinglist/removeok.html'
        ,{'site': Site.objects.get_current().name}
        ,context_instance=RequestContext(
            request, {}, create_calendar_context_params()))

def old_join(request):
    email = request.GET['q']
    site = Site.objects.get_current().name
    d = {'site': site, 'email':email}
    if not check_email(email):
        return render_to_response('mailinglist/join_error.html', d
            , context_instance = RequestContext(request))

    if MailingListSubscriber.objects.filter(email=email).count() == 0:
        mls = MailingListSubscriber(email=email, confirmed=False, confirm_code=make_random_hash())
        mls.save()
        d['confirm_code'] = mls.confirm_code
        send_email_to('mailinglist/request_confirmation.txt', email,
                loader.get_template('mailinglist/request_confirmation__subject.txt').render(Context({})), d, fail_silently=False)
        
    return render_to_response('mailinglist/join_confirm.html', d
        , context_instance=RequestContext(request))


def confirm(request, confirm_code):
    matches = MailingListSubscriber.objects.filter(confirm_code=confirm_code)
    email = 'person@example.com'
    site = Site.objects.get_current().name
    if len(matches) > 0:
        for match in matches:
            match.confirmed = True
            match.save()
            email = match.email
    # return success anyway - avoid letting people "sniff" hashes?
    return render_to_response('mailinglist/join_success.html', {
        'email':email,
        'site':site
    }, context_instance = RequestContext(request))

