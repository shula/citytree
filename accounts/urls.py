from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$', 'workshop.views.register'),
    (r'^register/(?P<workshop_slug>.+)/$', 'workshop.views.register'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'workshop/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^create_account/$', 'workshop.views.create_account'),
    (r'^capcha/image/(?P<seed>.+)/$', 'workshop.views.capcha_image')
)


