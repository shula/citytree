def media_url(request): 
    from django.conf import settings
    return {
        'media_url': settings.MEDIA_URL,
        'site_hostname': settings.SITE_HOSTNAME
    }

def citytree_context(request):
    from cityblog.models import Blog, Subject
    return {'blogs': Blog.objects.all(), 'subjects' : Subject.objects.all() }
