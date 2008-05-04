"""
$Id: urls.py 96 2006-06-13 22:48:42Z nesh $

URLconf for articles
"""

from django.conf.urls.defaults import patterns

__revision__ = '$Rev: 7 $'

urlpatterns = patterns('nesh.articles.views', #IGNORE:C0103
                       (r'^add/?$', 'add'),
                       (r'^edit/(?P<slug>[\w\-]+)/?$', 'edit'),
                       (r'^delete/(?P<slug>[\w\-]+)/?$', 'delete'),
                       (r'^show/(?P<slug>[\w\-]+)/?$', 'kview'),
                       (r'^art/show/(?P<slug>[\w\-]+)/?$', 'view'),
                       )
