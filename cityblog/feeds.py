# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from cityblog.models import post, blog

class LatestPosts(Feed):
    title = "פוסטים חדשים בעץ בעיר"
    link = "/posts/"
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

