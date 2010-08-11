# Generic admin views, with admin templates created dynamically at runtime.
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from nesh.translation.models import Message, Translation
from django.http import HttpResponseRedirect, HttpResponseNotFound
#from django.utils.translation import get_language
import sha
from django.conf import settings
from django.utils.translation import gettext as _

# XXX if Message does not exists add it automatically?? What about Registry?
def add(request, digest):
    msg = get_object_or_404(Message, digest__exact=digest)
    return render_to_response('translation/translate.html', context_instance=RequestContext(request, {'message': msg, 'path': request.GET.get('path', '/')} ))
#

def edit(request, digest):
    lang = request.LANGUAGE_CODE
    msg = get_object_or_404(Message, digest__exact=digest)
    
    try:
        tr = msg.translation_set.get(language__exact=lang)
    except Translation.DoesNotExist:
        #return HttpResponseNotFound()
        # add new translation
        return add(request, digest)
    #

    return render_to_response('translation/translate.html', context_instance=RequestContext(request, {'message': msg, 'path': request.GET.get('path', '/'), 'translated': tr,} ))
#

def save(request, digest):
    message = request.POST.get('message', None)
    path = request.POST.get('path', '/')

    if not message:
        return HttpResponseRedirect(path)
    #

    msg = get_object_or_404(Message, digest__exact=digest)
    lang = request.LANGUAGE_CODE #get_language()

    try:
        tr = msg.translation_set.get(language__exact=lang)
    except Translation.DoesNotExist:
        # add
        tr = Translation(translation=message, language=lang)
        msg.translation_set.add(trans)
        return HttpResponseRedirect(path)
    #

    # edit
    tr.translation = message
    tr.save()
    return HttpResponseRedirect(path)
#
