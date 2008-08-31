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

class UserProfile(User):
    """
    Additional data for all people who could login to the site. Exists in a seperate
    model since we can't actually change User, and don't want to, since it's implemented
    in a contrib module.
    """

    phone = models.CharField(max_length=200) # core=True
    address = models.CharField(max_length=400, default='not set') # core=True
    admin_notes = models.TextField(blank=True, null=True, help_text="Admin only (not for user) notes about the user")
    in_citytree_list = models.BooleanField(blank=True, default=True, null=True)

    def is_gardener(self):
        """ after talking to tami we agreed on the following definition:
        users without any blogs or only with the designated MEMBERS_BLOG (tbd in settings.py)
        are regular members. Anyone with a blog that isn't MEMBERS_BLOG is a GARDENER
        """
        return self.user.blog_set.filter(member_blog=False).count() > 0

    def is_member(self):
        return not self.is_gardener()

    def get_member(self):
        members_matching = Member.objects.filter(username=self.username)
        if members_matching.count() == 0: return None
        return members_matching[0]

    @staticmethod
    def create_from_existing_user(user):
        return create_from_existing_base(User, UserProfile, user)

    @staticmethod
    def create_userprofiles_for_all_users(read_litrom_too=False
            , overwrite_existing = False):
        if read_litrom_too:
            from utils.litrom import get_donors, get_csv_html
            txt = get_csv_html()
            donors = get_donors(txt)
            donors = dict([(x['email'], x) for x in donors])
        for u in User.objects.all():
            userprofiles_matching = UserProfile.objects.filter(username=u.username)
            if  userprofiles_matching.count() > 0:
                up = userprofiles_matching[0]
            else:
                up = UserProfile.create_from_existing_user(u)
                up.save()
                tmp_u = u
                up = UserProfile.objects.get(username=u.username)
                if not up.username == u.username:
                    print "bad bad bad"
                    import pdb
                    pdb.set_trace()
            if not read_litrom_too: continue
            m = up.get_member()
            if m is None and not overwrite_existing: continue
            if not donors.has_key(u.username): continue
            data = donors[u.username]
            del donors[u.username]
            up.create_member_from_litrom(data)
    
    def create_member_from_litrom(self, data):
        """ give it the dictionary from litrom.get_donors
        """
        mem = self.get_member()
        if mem is None:
            mem = Member.create_from_existing_user_profile(self)
            mem.save()
        mem.payment_amount = data['amount']
        mem.payment_method = 'litrom'
        mem.payment_number_of_payments = 0
        mem.address = data['address'][0] # bug in address parsing?
        mem.save()
        self.save()
        print "As Member: ", mem
        print "As UP: ", self
        #fields = ['handled', 'campaign', 'amount', 'date', 'first', 'last', 'address', 'city', 'mikud', 'email', 'comment']

    def __unicode__(self):
        return 'UserProfile %s %s' % (self.first_name, self.last_name)

def create_from_existing_base(base_class, inheritor_class, obj):
    inheritor = inheritor_class()
    ptr_field = '%s_ptr' % base_class.__name__
    setattr(inheritor, ptr_field, obj)
    fields = [x.name for x in obj._meta.fields]
    for f in fields:
        if f == inheritor_class.__name__: continue
        setattr(inheritor, f, getattr(obj, f))
    return inheritor # caller should .save()

class Member(UserProfile):
    """
    Members are users who contribute money to citytree. Since they are users
    they are implemented straightforwardly as inheriting from UserProfile

    They have dedicated blogs, which they access through the same interface, the desk, so
    in that sense they are just normal users, but they also have more information available
    since the main feature is that they pay 
    """

    payment_amount = models.FloatField(default=0.0)
    payment_method = models.CharField(max_length=200) # choice field?
    payment_number_of_payments = models.IntegerField(default=1)
    payment_reciet_sent = models.BooleanField(default=False)
    arrived_following = models.CharField(max_length=500)

    def __unicode__(self):
        return u'Member %s %s: %s' % (self.first_name, self.last_name, self.payment_method)

    @staticmethod
    def create_from_existing_user_profile(up):
        return create_from_existing_base(UserProfile, Member, up)

