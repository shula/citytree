#!/usr/bin/python2.4
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE']='citytree.settings'
sys.path.append('/home/tamizori')
sys.path.append('/home/tamizori/citytree')
from accounts.models import UserProfile

if __name__=='__main__':
    UserProfile.create_userprofiles_for_all_users()

