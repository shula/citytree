# pylint: disable-msg=C0103
""" urlconf """
from django.conf.urls.defaults import patterns

from models import Entry

info_dict = {
    'queryset': Entry.objects.published(),
    'date_field': 'pub_date',
    #'extra_context': {
    #    'years': Entry.objects.get_pub_date_list('year'),
    #    'months': Entry.objects.get_pub_date_list('month'),
    #},
}

info_dict_month = info_dict.copy()
info_dict_month['month_format'] = '%m'

urlpatterns = patterns('nesh.news.views',
                       # JSON
                       (r'^json/list/(\d+)/?$', 'json_news_list'),
                       (r'^json/get/(\d+)/(\d+)/?$', 'json_get_news'),
)

urlpatterns += patterns('django.views.generic.date_based',
   (r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\w{1,2})/(?P<slug>[\w\-]+)/$', 'object_detail', dict(info_dict_month, slug_field='slug')),
   (r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\w{1,2})/$', 'archive_day', info_dict_month),
   (r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'archive_month', info_dict_month),
   (r'^(?P<year>\d{4})/$', 'archive_year', info_dict),
   (r'^/?$', 'archive_index', info_dict),
)
