from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers

class JSONResponse(HttpResponse):
    def __init__(self, obj):
        self.original_obj = obj
        #if not obj:
        #    self.original_obj = list(obj)
        #else:
        #    self.original_obj = None
        HttpResponse.__init__(self, self.serialize())
        self["Content-Type"] = "text/javascript; charset=utf-8"

    def serialize(self):
        return('{"%s": %s}' % ('data', simplejson.dumps(self.original_obj, ensure_ascii=False)))

def response_from_filter(filter):
    ret = []
    for obj in filter:
        ret.append({'pk': obj.id, 'str': str(obj)})
    return JSONResponse(ret)

def response_from_tuples(lst):
    ret = []
    for pk, val in lst:
        ret.append({'pk': pk, 'str': val})
    return JSONResponse(ret)
#def json_lookup(request, queryset, field, limit=10, login_required=False):
#    """
#    Method to lookup a model field and return a array. Intended for use 
#    in AJAX widgets.
#    """
#    if login_required and not request.user.is_authenticated():
#        return redirect_to_login(request.path)
#    obj_list = []
#    lookup = {
#        '%s__istartswith' % field: request.GET['q'],
#    }
#    for obj in queryset.filter(**lookup)[:limit]:
#        obj_list.append([getattr(obj, field), obj.id])
#    return JsonResponse(obj_list)
