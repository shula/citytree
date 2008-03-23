from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^$', 'citytree.frontpage.views.show_front_page' ),
    (r'^frontpage/preview/(?P<page_id>\d+)/$', 'citytree.frontpage.views.preview_front_page' ),
)
