# ./manage.py shell
# then source:
from django.contrib.comments.models import Comment
comments=Comment.objects.all()
#  see code.saymoo.org - SpamSpamSpam page
ch=[c for c in comments if c.comment.find('http')!=-1]

