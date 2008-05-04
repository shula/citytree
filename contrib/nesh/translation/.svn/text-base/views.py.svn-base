# stdlib
import sha
# django
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext as Context
from django.utils.translation import check_for_language
from django.utils.translation import gettext as _
# nesh
from nesh.translation.models import Message, Translation

def set_language(request, lang_code=settings.LANGUAGE_CODE):
    """
    Redirect to a given url while setting the chosen language in the
    session or cookie. The next url can be
    specified in the GET paramter.
    
    Use url like /i18n/set-language/<language code>/[?next=...].
    
    If next is not given it will try to return to HTTP_REFERER.
    """

    next = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))

    response = HttpResponseRedirect(next)
    
    if check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie('django_language', lang_code)
    return response

#=========================================================================================
# In progress... it will be changed
#=========================================================================================

# XXX if Message does not exists add it automatically?? What about Registry?
def add(request, digest):
    msg = get_object_or_404(Message, digest__exact=digest)
    return render_to_response('translation/translate.html', context_instance=Context(request, {'message': msg, 'path': request.GET.get('path', '/')} ))

def edit(request, digest):
    lang = request.LANGUAGE_CODE
    msg = get_object_or_404(Message, digest__exact=digest)
    
    try:
        tr = msg.translation_set.get(language__exact=lang)
    except Translation.DoesNotExist:
        # add new translation
        return add(request, digest)

    return render_to_response('translation/translate.html', context_instance=Context(request, {'message': msg, 'path': request.GET.get('path', '/'), 'translated': tr,} ))

def save(request, digest):
    message = request.POST.get('message', None)
    path = request.POST.get('path', '/')

    if not message:
        return HttpResponseRedirect(path)

    msg = get_object_or_404(Message, digest__exact=digest)
    lang = request.LANGUAGE_CODE #get_language()

    try:
        tr = msg.translation_set.get(language__exact=lang)
    except Translation.DoesNotExist:
        # add
        tr = Translation(translation=message, language=lang)
        msg.translation_set.add(trans)
        return HttpResponseRedirect(path)

    # edit
    tr.translation = message
    tr.save()
    return HttpResponseRedirect(path)