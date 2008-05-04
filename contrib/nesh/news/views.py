from django.http import HttpResponse
from django.core import serializers 
from nesh.news.models import Entry

def json_news_list(request, mod):
    return HttpResponse(serializers.serialize('json', Entry.objects.get_news(int(mod)), ensure_ascii=False),
                        mimetype='text/javascript; charset=utf-8')

def json_get_news(request, number, mod):
    number = int(number)
    mod = int(mod)
    news = Entry.objects.get_news(mod)
    if len(news):
        if len(news) < mod:
            mod = len(news)
        return HttpResponse(serializers.serialize('json', [news[int(number) % mod]], ensure_ascii=False),
                            mimetype='text/javascript; charset=utf-8')
    else:
        return HttpResponse(serializers.serialize('json', [], ensure_ascii=False),
                            mimetype='text/javascript; charset=utf-8')

