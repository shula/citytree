def create_from_existing_base(base_class, inheritor_class, obj):
    """ Now that django has model inheritance, a common case of migration
    is to create an instance of the inheritor given an instance of the base
    class. This method does just that.
    """
    inheritor = inheritor_class()
    ptr_field = '%s_ptr' % base_class.__name__
    setattr(inheritor, ptr_field, obj)
    fields = [x.name for x in obj._meta.fields]
    for f in fields:
        if f == inheritor_class.__name__: continue
        setattr(inheritor, f, getattr(obj, f))
    return inheritor # caller should .save()


