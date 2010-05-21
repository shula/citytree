import re

from django.db import models

from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager

from utils.collections import muldict

class CityCommentManager(CommentManager):
    def get_query_set(self):
        return Comment.objects.all()

def to_id_dict(col):
    return muldict((x.content_object.id, x) for x in col if x.content_object != None)
    
re_href = re.compile('href.*=\s*"?([^"]*)"?\s*>')

class CityComment(Comment):
    phone = models.CharField(max_length=30, blank=True)

    def short_comment(self):
        s = re.search(re_href, self.comment)
        if s:
            return s.groups()[0][:50]
        return self.comment[:50]

    class Meta:
        get_latest_by = 'submit_date'
    #objects = CityCommentManager()
    #citycomments = models.Manager()

    @classmethod
    def as_id_dict(cls):
        return to_id_dict(cls.objects.all())
