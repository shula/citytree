# Generic admin views, with admin templates created dynamically at runtime.
from django.template import RequestContext as Context
from django.shortcuts import render_to_response, get_object_or_404
from nesh.articles.models import Article, ArticleCategory

def view(request, slug):
    data = get_object_or_404(Article, slug__exact=slug)
    category = data.category
    return render_to_response('articles/show.html', context_instance=Context(request, {'data': data, 'category': category}))

def kview(request, slug):
    data = get_object_or_404(ArticleCategory, slug__exact=slug)
    return render_to_response('articles/show.html', context_instance=Context(request, {'data': data, 'category': data}))