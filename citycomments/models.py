from django.db import models

from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager

try:
    from utils.collections import muldict
except:
    pass

class CityCommentManager(CommentManager):
    def get_query_set(self):
        return Comment.objects.all()

# Create your models here.

def to_id_dict(col):
    return muldict((x.content_object.id, x) for x in col if x.content_object != None)
    

class CityComment(Comment):
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        get_latest_by = 'submit_date'
    #objects = CityCommentManager()
    #citycomments = models.Manager()

    @classmethod
    def as_id_dict(cls):
        return to_id_dict(cls.objects.all())
