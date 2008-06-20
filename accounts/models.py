# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from cityblog.models import post

class CapchaRequest(models.Model):
    hash       = models.CharField(max_length=256, blank=False)
    letters    = models.CharField(max_length=100)

    def __unicode__(self):
        return self.hash

    def get_image_url(self):
        return '/accounts/capcha/image/%s/' % self.hash

    class Admin:
        pass

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone = models.CharField(max_length=200)
    in_citytree_list = models.BooleanField(blank=True, default=True, null=True)
    # TODO whenever needed

