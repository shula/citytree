# pylint: disable-msg=R0913,W0612,W0613
from django.conf import settings
from django.template import RequestContext as Context
from django.db.models.fields import FieldDoesNotExist, NOT_PROVIDED
from django.template import (
                             TemplateSyntaxError, 
                             Library, 
                             Node, 
                             resolve_variable, 
                             TokenParser, 
                             Template,
                             )
from django.template.loader import render_to_string
from django.utils.translation import gettext
import re

register = Library()

#class FormRowNode(Node):
#    def __init__(self, nodelist):
#        super(FormRowNode, self).__init__()
#        self.nodelist = nodelist
#
#    def render(self, context):
#        try:
#            return '<div class="form-row">%s</div>' % self.nodelist.render(context)
#        except Exception:
#            raise
#        return ''
#
#@register.tag
#def formrow(parser, token):
#    """
#    Create form row template.
#
#    Example::
#
#        {% formrow %}
#            ({% formfield  %})*
#        {% endformrow %}
#    """
#
#    nodelist = parser.parse(('endformrow',))
#    parser.delete_first_token()
#    return FormRowNode(nodelist)


# TODO: help
# TODO: edit_inline support
# TODO: inline support
class FormFieldNode(Node):
    def __init__(self, field, label, readonly=False, inline=False, single=False, filter_=None):
        super(FormFieldNode, self).__init__()
        self.label = label
        self.readonly = readonly
        self.wrapper, self.field = field.split('.')
        self.inline = inline
        self.single = single
        self.filter = filter_

    def render(self, context):  #IGNORE:R0912
        form = context['FORM'] = context[self.wrapper] #IGNORE:W0612
        orig_field = self.field #IGNORE:W0612
        label = self.label #IGNORE:W0612
        field = context['FORM_field'] = form[self.field]
        str_field = '%s.%s' % (self.wrapper, self.field)
        context['FORM_readonly'] = self.readonly
        user = context.get('user', None)
        addlink = '' #IGNORE:W0612
        js = None
        try:
            model = resolve_variable(self.wrapper, context).manipulator.model #IGNORE:E1101
            try:
                fld = model._meta.get_field(self.field)
                context['FORM_DBFIELD'] = fld
                template_name = fld.__class__.__name__.lower()
                #context['FORM_db_field'] = fld
                maxlen = getattr(fld, 'maxlength')
                if maxlen:
                    context['FORM_size'] = maxlen < 80 and maxlen or 80
                else:
                    context['FORM_size'] = 30
                context['FORM_maxlength'] = maxlen
                context['FORM_label'] = fld.verbose_name
                context['FORM_help_text'] = fld.help_text
                context['FORM_value'] = form.data.get(self.field, fld.default)
                if context['FORM_value'] is None: context['FORM_value'] = ''
                if context['FORM_value'] == NOT_PROVIDED: context['FORM_value'] = ''
            except FieldDoesNotExist:
                raise TemplateSyntaxError, 'Field "%s" does not exists in model "%s"' % (self.field, model._meta.object_name)
            if not self.readonly:
                if user is not None and not user.is_anonymous():
                    pass
                    # TODO: relatons
                    if fld.rel:
                        to = fld.rel.to._meta
                        if user.has_perm('%s.%s' % (to.app_label, to.get_add_permission())):
                            alt = gettext('Add Another')
                            module = to.module_name
                            app_label = to.app_label
                            context['FORM_add_rel'] = '\n<a href="/admin/%(app_label)s/%(module)s/add/" class="add-another" id="add_{{ %(str_field)s.get_id }}" onclick="return showAddAnotherPopup(this);"> <img src="/admin-media/img/admin/icon_addlink.gif" alt="%(alt)s" height="10" width="10"></a>\n' % locals()
                    else:
                        context['FORM_add_rel'] = ''
                    if self.filter is not None:
                        if self.filter == 'horizontal':
                            dir = 0
                        else:
                            dir = 1
                        context['FORM_JS'] = Template('<script type="text/javascript">addEvent(window, "load", function(e) { SelectFilter.init("{{ %(str_field)s.get_id }}", "{{ %(str_field)s.get_member_name }}", %(dir)d, "/admin-media/"); });</script>' % locals()).render(context)
                #t = Template(FTPL % locals())
            else:
                # XXX escape field data??
                default = gettext('Empty')
                #t = Template(ROFTPL % locals())
            if not self.inline:
                if field.errors():
                    return '<div class="form-row error">%s</div>' % render_to_string('widgets/%s.html' % template_name, context_instance=context)
                else:
                    return '<div class="form-row">%s</div>' % render_to_string('widgets/%s.html' % template_name, context_instance=context)
            else:
                    return render_to_string('widgets/%s.html' % template_name, context_instance=context)

        except TemplateSyntaxError, e:
            if settings.TEMPLATE_DEBUG:
                raise
        return ''

I18NRE = re.compile(r'^_\((?:\'|")(.*?)(?:\'|")\)$')

# TODO: better syntax check
@register.tag
def formfield(parser, token):
    """
    Create form field.

    Example::

        {% formfield <field> <label> [filter horizontal|vertical] [as [readonly] [inline] %}
    """
    class Parser(TokenParser):
        def top(self):
            field = None
            label = None
            readonly = False
            inline = False
            single = False
            filter = None
            ct = 0

            while self.more():
                if ct == 0:
                    field = self.value()
#                elif ct == 1:
#                    val = self.value().strip('"')
#                    val = val.strip("'")
#                    r = I18NRE.match(val)
#                    if r:
#                        label = gettext(r.group(1))
#                    else:
#                        label = val
                else:
                    tag = self.tag()
                    if tag == 'filter':
                        filter = self.value()
                        single = True # force single
                    elif tag == 'as':
                        while self.more():
                            tag = self.tag()
                            if tag == 'readonly':
                                readonly = True
                            elif tag == 'inline':
                                inline = True
                            elif tag == 'single':
                                single = True
                            else:
                                raise TemplateSyntaxError, "'formfield' syntax error (got %r)" % tag
                    else:
                        raise TemplateSyntaxError, "'formfield' syntax error"
                ct += 1
            return field, label, readonly, inline, single, filter
    field, label, readonly, inline, single, filter = Parser(token.contents).top()
    return FormFieldNode(field, label, readonly, inline, single, filter)
