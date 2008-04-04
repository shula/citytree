# ./manage.py shell
# then source:
from django.contrib.comments.models import FreeComment
comments=FreeComment.objects.all()
ch=[c for c in comments if c.comment.find('http')!=-1]

