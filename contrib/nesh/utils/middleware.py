""" from http://lukeplant.me.uk/blog.php?id=1107301634
    requires Python 2.4
"""

import threading

_THREAD_LOCALS = threading.local()

def get_current_user():
    """ return current logged in user """
    return getattr(_THREAD_LOCALS, 'user', None)
#

#def user_fields(model, options):
#    from django.db.models.options import AdminOptions
#    from django.db.models import Model
#    assert isinstance(model, Model)
#    assert isinstance(options, AdminOptions)
#    
#    del model._meta.admin.fields
#    model._meta.admin.__class__ = options
#    return model
##

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    
    def process_request(self, request):
        """ dodaje user u thread locals """
        _THREAD_LOCALS.user = getattr(request, 'user', None)
    #
#

#class ApplicationAdminOptions(AdminOptions):
#    """Class used to replace AdminOptions for the Application model"""
#    def _fields(self):
#        user = threadlocals.get_current_user()
#        if user is None or user.is_anonymous():
#            # should never get here
#            return ()
#        else:
#            if user.has_perm('officers.change_application'):
#                # Fields for a user with more privileges
#                # to be able to modify existing Applications
#                return (
#                   (None, {'fields':
#                      ('officer', 'full_name', 'address')}
#                   ),
#                 )
#            else:
#                # Fields for a normal officer
#                return (
#                   (None, {'fields':
#                      ('full_name', 'address')}
#                   ),
#                )
#    fields = property(_fields)

from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
class SiteLogin:
    "This middleware requires a login for every view from http://superjared.com/entry/requiring-login-entire-django-powered-site/"
    def process_request(self, request):
        if request.path != '/accounts/login/' and request.user.is_anonymous():
            if request.POST:
                return login(request)
            else:
                return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)