# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django.contrib.sites.models import Site

from mailinglist.models import MailingListSubscriber
from utils.randomUtils import make_random_hash
from utils.email import check_email, send_email_to

def join(request):
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

