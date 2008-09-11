#!/usr/bin/python2.4
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE']='citytree.settings'
home = os.environ['HOME']
sys.path.append(home)
sys.path.append(os.path.join(home, 'citytree'))

from utils.models import create_from_existing_base
from django.contrib.comments.models import Comment
from citycomments.models import CityComment

def main():
    call = Comment.objects.all()
    count = 0
    for c in call:
        if CityComment.objects.filter(comment_ptr__pk=c.id).count() == 0:
            count += 1
            cc=create_from_existing_base(Comment,CityComment,c)
            cc.save()

    print "created %s CityComments with empty phones" % count

if __name__ == '__main__':
    main()
