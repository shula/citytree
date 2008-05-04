# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from cityblog.models import post, blog
from django.views.generic.list_detail import object_list as generic_object_list
from citytree.utils.hebCalView import *

def LatestPosts_get_feed_url(blog):
  return u'%s/%s' % (LatestPosts.link, blog.slug)

class LatestPosts(Feed):
    title = "פוסטים חדשים בעץ בעיר"
    link = "/posts"
    description = "עדכונים מעץ בעיר של כל הכותבים"

    def get_object(self, bits):
        """ this is used to return a slug specific feed when bits is length one, like
        """
        if len(bits) == 1:
            return blog.objects.get(slug=bits[0])
        return None

    def items(self, blog=None):
        if blog is None:
            return post.objects.filter(draft=0).order_by('-post_date')[:10]
        # return only posts from the same blog
        return post.objects.filter(draft=0, blog=blog).order_by('-post_date')[:10]

class DummyList(list):
    def _clone(self):
        return DummyList(self)
    def __unicode__(self):
        return unicode(repr(self))

def main_page(request):
  #------------ Create Objects for Hebrew Calender ----
  calLinkType     = FRONTPAGE_URL_TYPE
  calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
  dateToShow = date.today()
  bgColorProcessor = makeHebBGColorProcessor( dateToShow )
  dayLinks = makeHebCalLinks( '/?date=%s', date.today() )
  calender = makeHebCalRequestContext(dayLinks, engDate=date.today(), urlType=calLinkType, highlightToday=True)
  return generic_object_list( request, queryset=blog.objects.all(),
              template_object_name='blog',
              template_name='feeds_main_page.html',
              context_processors =[calender,bgColorProcessor],
              allow_empty=True)
 
