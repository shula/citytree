from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^profile/$', 'accounts.views.profile'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^create_account/$', 'accounts.views.create_account'),
    (r'^registration_success/$', 'accounts.views.registration_success'),
    (r'^capcha/image/(?P<hash>.+)/$', 'accounts.views.capcha_image')
)

