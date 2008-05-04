from django.conf import settings
from django import template
from django.conf import settings
from django.db.models.fields import FieldDoesNotExist
from django.template import (
                             TemplateSyntaxError, 
                             Library, 
                             Node, 
                             resolve_variable, 
                             TokenParser, 
                             Template
                             )
from django.utils.translation import gettext
from nesh.utils.middleware import get_current_user
import re

register = Library()

#=========================================================================================
# number formatting
#=========================================================================================
def _group(s, grouping=(3, 0), thousands_sep=','):
    if not grouping:return (s, 0)
    result=""
    seps = 0
    spaces = ""
    if s[-1] == ' ':
        sp = s.find(' ')
        spaces = s[sp:]
        s = s[:sp]
    while s and grouping:
        # if grouping is -1, we are done
        if grouping[0]== -1:
            break
        # 0: re-use last group ad infinitum
        elif grouping[0]!=0:
            #process last group
            group=grouping[0]
            grouping=grouping[1:]
        if result:
            result = s[-group:] + thousands_sep +result
            seps += 1
        else:
            result=s[-group:]
        s=s[:-group]
        if s and s[-1] not in "0123456789":
            # the leading string is only spaces and signs
            return s + result + spaces, seps
    if not result:
        return s+spaces,seps
    if s:
        result=s + thousands_sep + result
        seps += 1
    return result + spaces, seps
#

def format(f, val, decimal_point='.', grouping=True):
    """Formats a value in the same way that the % formatting would use,
    but takes the current locale into account.
    Grouping is applied if the grouping parameter is true."""
    if decimal_point == '.':
        thousands_sep = ','
    else:
        thousands_sep = '.'
    result = f % val
    fields = result.split(".")
    seps = 0
    if grouping:
        fields[0], seps = _group(fields[0], thousands_sep=thousands_sep)
    if len(fields) == 2:
        result = fields[0] + decimal_point + fields[1]
    elif len(fields) == 1:
        result = fields[0]
    else:
        raise ValueError, "Too many decimal points in result string"

    while seps:
        # If the number was formatted for a specific width, then it
        # might have been filled with spaces to the left or right. If
        # so, kill as much spaces as there where separators.
        # Leading zeroes as fillers are not yet dealt with, as it is
        # not clear how they should interact with grouping.
        sp = result.find(" ")
        if sp==-1:break
        result = result[:sp] + result[sp + 1:]
        seps -= 1

    return result
#
@register.simple_tag
def formatmoney(fmt, val, decimal_point='.'):
    return format(fmt, val, decimal_point=decimal_point)

@register.simple_tag
def module_name(module):
    """ returns module name """
    return module._meta.module_name

@register.simple_tag
def MEDIA_URL():
    """ return MEDIA_URL """
    return settings.MEDIA_URL.rstrip('/')

@register.simple_tag
def ADMIN_MEDIA_URL():
    """ return ADMIN_MEDIA_PREFIX """
    return settings.ADMIN_MEDIA_PREFIX.rstrip('/')

#class GetSettings(Node):
#    def __init__(self, variable):
#        super(GetSettings, self).__init__()
#        self.variable = variable
#
#    def render(self, context):
#        return getattr(settings, self.variable)
#
#@register.tag(name="get_settings")
#def get_settings(parser, token):
#    """ return value from django settings """
#
#    args = token.contents.split()
#    
#    if len(args) != 2 :
#        raise TemplateSyntaxError, "'get_settings' requires only variable name (got %r)" % args
#    if not hasattr(settings, args[1]):
#        raise TemplateSyntaxError, "'get_settings' invalid variable name for %s" % args[1]
#    return GetSettings(args[1])

#=========================================================================================
# lifted from RLP
#=========================================================================================
def if_has_perm(parser, token):
    """

    TODO: Update document
    
    Checks permission on the given user.
    
    Note: Perm name should be in the format of [app_label].[perm codename]
        
    """    
    tokens = token.split_contents()
    if len(tokens)<2:
        raise template.TemplateSyntaxError, "%r tag requires at least 1 arguments" % tokens[0]
    if len(tokens)>4:
        raise template.TemplateSyntaxError, "%r tag should have no more then 3 arguments" % tokens[0]
    
    nodelist_true = parser.parse(('else', 'end_'+tokens[0],))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('end_'+tokens[0],))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    
    object_var = None
    not_flag = False
    if tokens[1] is "not":
        not_flag = True
        permission=tokens[2]
        if len(tokens)>3:
            object_var = parser.compile_filter(tokens[3])
    else:
        permission=tokens[1]
        if len(tokens)>2:
            object_var = parser.compile_filter(tokens[2])

    if not (permission[0] == permission[-1] and permission[0] in ('"', "'")):            
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tokens[0]
    
    return HasPermNode(permission[1:-1], not_flag, object_var, nodelist_true, nodelist_false)
    
class HasPermNode(template.Node):
    def __init__(self, permission, not_flag, object_var, nodelist_true, nodelist_false):
        self.permission = permission
        self.not_flag = not_flag
        self.object_var = object_var
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<HasPerm node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):   
        if self.object_var:
            try:
                object = self.object_var.resolve(context)
            except template.VariableDoesNotExist:
                object = None
        else:
            object=None
        
        try:
            user = template.resolve_variable("user", context)
        except template.VariableDoesNotExist:
            return settings.TEMPLATE_STRING_IF_INVALID
        
        bool_perm = user.has_perm(self.permission)
        if (self.not_flag and not bool_perm) or (not self.not_flag and bool_perm):
            return self.nodelist_true.render(context)
        if (self.not_flag and bool_perm) or (not self.not_flag and not bool_perm):
            return self.nodelist_false.render(context)
        return ''
        
register.tag('nesh_if_has_perm', if_has_perm)

#=========================================================================================
# FORM UTILS
#=========================================================================================
FTPL = """
    {%% if %(field)s.errors %%}
        <ul class="errorlist">{%% for err in %(field)s.errors %%}<li>{{ err }}</li>{%% endfor %%}</ul>
    {%% endif %%}
    <label for="{{ %(field)s.get_id }}" class="%(inline)s{%% if %(field)s.formfield.is_required %%} required{%% endif %%}">%(label)s:</label>
    {{ %(field)s }}
    %(addlink)s
"""

ROFTPL = """
    <!-- READONLY -->
    <label for="{{ %(field)s.get_id }}" class="%(inline)s{%% if %(field)s.formfield.is_required %%} required{%% endif %%}">%(label)s:</label>
    <input disabled class="vTextField" id="{{ %(field)s.get_id }}" value="{{ %(wrapper)s.data.%(orig_field)s|default:"%(default)s" }}" />
    %(addlink)s
"""

# TODO: help
class FormFieldNode(Node):
    def __init__(self, field, label, readonly=False, inline=False, single=False, filter_=None):
        super(FormFieldNode, self).__init__()
        self.label = label
        self.readonly = readonly
        self.wrapper, self.field = field.split('.')
        self.inline = inline
        self.single = single
        self.filter = filter_
    #

    def render(self, context):  #IGNORE:R0912
        wrapper = self.wrapper #IGNORE:W0612
        orig_field = self.field #IGNORE:W0612
        label = self.label #IGNORE:W0612
        field = '%s.%s' % (self.wrapper, self.field) #IGNORE:W0612
        user = get_current_user()
        addlink = '' #IGNORE:W0612
        js = None
        if self.inline:
            inline = 'inline' #IGNORE:W0612
        else:
            inline = ''
        #
        try:
            if not self.readonly:
                if user is not None and not user.is_anonymous():
                    model = resolve_variable(self.wrapper, context).manipulator.model #IGNORE:E1101
                    try:
                        fld = model._meta.get_field(self.field)
                    except FieldDoesNotExist:
                        raise TemplateSyntaxError, 'Field "%s" does not exists in model "%s"' % (self.field, model._meta.object_name)
                    #
                    if fld.rel:
                        to = fld.rel.to._meta
                        if user.has_perm('%s.%s' % (to.app_label, to.get_add_permission())):
                            alt = gettext('Add Another')
                            module = to.module_name
                            app_label = to.app_label
                            addlink = '\n<a href="/admin/%(app_label)s/%(module)s/add/" class="add-another" id="add_{{ %(field)s.get_id }}" onclick="return showAddAnotherPopup(this);"> <img src="/admin-media/img/admin/icon_addlink.gif" alt="%(alt)s" height="10" width="10"></a>\n' % locals()
                     #
                    if self.filter is not None:
                        if self.filter == 'horizontal':
                            dir = 0
                        else:
                            dir = 1
                        #js = Template('<script type="text/javascript">addEvent(window, "load", function(e) { SelectFilter.init("{{ %(field)s.get_id }}", "{{ %(field)s.get_member_name }}", %(dir)d, "/admin-media/"); });</script>' % locals())

                #
                t = Template(FTPL % locals())
            else:
                # XXX escape field data??
                default = gettext('Empty')
                t = Template(ROFTPL % locals())
            #
            if not self.single:
                return t.render(context)
            else:
                if js is None:
                    return '<div class="form-row">%s</div>' % t.render(context)
                else:
                    return '<div class="form-row">%s</div>%s' % (t.render(context), js.render(context))
                    
        except TemplateSyntaxError, e:
            if settings.TEMPLATE_DEBUG:
                raise
        return ''
    #
#

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
                elif ct == 1:
                    val = self.value().strip('"')
                    val = val.strip("'")
                    r = I18NRE.match(val)
                    if r:
                        label = gettext(r.group(1))
                    else:
                        label = val
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
                        #
                    else:
                        raise TemplateSyntaxError, "'formfield' syntax error"
                    #
                #
                ct += 1
            # while
            return field, label, readonly, inline, single, filter
        #
    field, label, readonly, inline, single, filter = Parser(token.contents).top()
    return FormFieldNode(field, label, readonly, inline, single, filter)
#

class FormRowNode(Node):
    def __init__(self, nodelist):
        super(FormRowNode, self).__init__()
        self.nodelist = nodelist
    #

    def render(self, context):
        try:
            return '<div class="form-row">%s</div>' % self.nodelist.render(context)
        except Exception:
            raise
        return ''
    #
#

@register.tag
def formrow(parser, token):
    """
    Create form row template.

    Example::

        {% formrow %}
            {% formfield <field> with <label> [as readonly] %}
        {% endformrow %}
    """

    nodelist = parser.parse(('endformrow',))
    parser.delete_first_token()
    return FormRowNode(nodelist)
#