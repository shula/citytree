# -*- coding: utf-8 -*-

"""
Models for people who just want to be added to the mailing list
"""

from django.db import models

class MailingListSubscriber(models.Model):
    """ Someone who is not a User (so not a Member), but wants to be on the mailing list - 
    we record this when he goes through the add to mailing list form on the front page.
    """
    email        =   models.EmailField('subscriber email', max_length=200, blank=False)
    confirmed    =   models.BooleanField(blank=False, default=False)
    confirm_code =   models.TextField('confirmation code', max_length=50, blank=False)

    def __unicode__(self):
        return u'<subscriber %s>' % (self.email)

    class Admin:
        list_filter    = ('email',)

