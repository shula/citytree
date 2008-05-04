import base

FLD_LEN = len('Field')

def widget_factory(form_field):
    try:
        name = form_field.__class__.__name__[:-FLD_LEN]
        cls = getattr(base, '%sWidget' % name)
        ret = cls(form_field)
        print 'ret %r (%r)' % (ret, ret.__class__.__name__)
        return ret
    except AttributeError:
        return form_field
