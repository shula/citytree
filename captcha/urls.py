# Copyright (c) 2007 Brandon Low
# Licensed under the GPL v2
from django.conf.urls.defaults import *
from views import captcha_image

urlpatterns = patterns('', (r'^captcha/(?P<id>[0-9]+)/$', captcha_image))
