from django.core.exceptions import ObjectDoesNotExist

def create_from_existing_base(base_class, inheritor_class, obj):
    """ Now that django has model inheritance, a common case of migration
    is to create an instance of the inheritor given an instance of the base
    class. This method does just that.
    """
    inheritor = inheritor_class()
    ptr_field = '%s_ptr' % base_class.__name__.lower()
    setattr(inheritor, ptr_field, obj)
    fields = [x.name for x in obj._meta.fields]
    for f in fields:
        if f == inheritor_class.__name__: continue
        # HACK: check if there is an associated id field. If so, use that instead
        f_id = '%s_id' % f
        try:
            val = getattr(obj, f_id)
            f = f_id
        except:
            pass
        # check if field is actually gettable from obj
        try:
            val = getattr(obj, f)
        except ObjectDoesNotExist:
            continue
        setattr(inheritor, f, val)
    return inheritor # caller should .save()


