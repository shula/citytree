# vim: set fileencoding=utf-8 :
from django.db import models
from citytree.cityblog.models import post

class banned_ip(models.Model):
    ip_address    = models.IPAddressField('ip address')
    posts         = models.ManyToManyField(post,verbose_name='specific posts to ban from', blank=True, null=True)
    
    def __unicode__(self):
      return self.ip_address

    class Admin:
        list_display = ('ip_address',)

class allowed_ban_requests(models.Model):
    hash          = models.CharField(max_length=256, blank=False)
    ip_address    = models.IPAddressField('ip address')

    class Admin:
        list_display = ('hash', 'ip_address')
