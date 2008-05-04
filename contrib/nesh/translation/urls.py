from django.conf.urls.defaults import *

urlpatterns = patterns('nesh.translation.views',
    (r'^set-language/(\w+)?/?$', 'set_language'),
    # admin
    (r'^add/(?P<digest>\w+)/?$', 'add'),
    (r'^edit/(?P<digest>\w+)/?$', 'edit'),
    (r'^pledit/(?P<digest>\w+)/?$', 'pledit'),
    (r'^save/(?P<digest>\w+)/?$', 'save'),
    (r'^add/(?P<digest>\w+)/?$', 'add'),
)

