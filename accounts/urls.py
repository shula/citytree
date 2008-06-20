from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^profile/$', 'accounts.views.profile'),
    (r'^login_and_register/$', 'accounts.views.login_and_register'),
#    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
#    (r'^create_account/$', 'accounts.views.create_account'),
    (r'^capcha/image/(?P<hash>.+)/$', 'accounts.views.capcha_image')
)

