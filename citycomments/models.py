from django.db import models

from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager

class CityCommentManager(CommentManager):
    def get_query_set(self):
        return Comment.objects.all()

# Create your models here.

class CityComment(Comment):
    phone = models.CharField(max_length=30)

    objects = CityCommentManager()
    citycomments = models.Manager()

