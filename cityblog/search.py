from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.template import loader, Context
from cityblog.models import post
import operator

class_search_fields = ((post, ['title', 'teaser_text', 'text'], {'draft':0}),)

def search(terms): 
    query = terms.replace("+"," ")       
    search_results = []

    if query:
        for clazz, search_fields, filter_terms in class_search_fields:
            or_query=Q() 
            other_qs = QuerySet(clazz) # your class here
            for bit in query.split(): 
                or_queries = [Q(**{'%s__icontains' % field_name: bit}) for field_name in search_fields] 
                other_qs = other_qs.filter(reduce(operator.or_, or_queries)) 
            search_results.append((clazz, other_qs.filter(**filter_terms)))
    return search_results
