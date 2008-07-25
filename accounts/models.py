# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class CapchaRequest(models.Model):
    hash       = models.CharField(max_length=256, blank=False)
    letters    = models.CharField(max_length=100)

    def __unicode__(self):
        return self.hash

    def get_image_url(self):
        return '/accounts/capcha/image/%s/' % self.hash

    class Admin:
        pass

class MemberManager(models.Manager):
    def get_query_set(self):
        """ Returns User's that match the member definition as given
        by UserProfile.is_gardener (is_gardener is suitable for a single
        instance, here we generate a more efficient query)
        """
        return User.objects.filter(blog__member_blog=True).exclude(blog__member_blog=False).distinct()
        # this also works since new members have their name initially as the
        # email address
        # User.objects.filter(username__contains='@')

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True,
        edit_inline=models.TABULAR, num_in_admin=1,min_num_in_admin=1, max_num_in_admin=1,num_extra_on_change=0)
    phone = models.CharField(max_length=200, core=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Admin only (not for user) notes about the user")
    in_citytree_list = models.BooleanField(blank=True, default=True, null=True)

    objects = models.Manager()
    members = MemberManager()

    def is_gardener(self):
        """ after talking to tami we agreed on the following definition:
        users without any blogs or only with the designated MEMBERS_BLOG (tbd in settings.py)
        are regular members. Anyone with a blog that isn't MEMBERS_BLOG is a GARDENER
        """
        return self.user.blog_set.filter(member_blog=False).count() > 0

    def is_member(self):
        return not self.is_gardener()

    @staticmethod
    def create_userprofiles_for_all_users():
        for u in User.objects.all():
            if u.userprofile_set.count() > 0: continue
            up = UserProfile()
            up.user = u
            up.save()

