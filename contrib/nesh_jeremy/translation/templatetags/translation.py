from difflib import Differ
from django.conf import settings
from django.template import Node
from django.template import TOKEN_BLOCK, TOKEN_TEXT, TOKEN_VAR
from django.template import TemplateSyntaxError, Library, Node, resolve_variable, TokenParser
from django.utils.translation import get_language, gettext
from nesh.translation.models import Message, message_digest
import urllib

register = Library()

# TODO: make link to switch translate mode on and off and store this in the session

# ========================================================================
# translate
# ========================================================================

TRANS_LINK = """<div class="translate_block">
    %(translation)s
    <a href="/translate/edit/%(digest)s/%(path)s" class="translation" rel="nofollow" title="%(edit_trans)s">
        <image src="%(icon)s" height="16" width="16" alt="%(edit_trans)s" />
    </a>
</div>
"""

class TranslateNode(Node):
    def __init__(self, message, no_action):
        self.message = message
        self.no_action = no_action
    #

    def render(self, context):
        message = resolve_variable(self.message, context)
        icon = getattr(settings, 'TRANSLATION_ICON', '/media/img/icons/edit.png')
        lang = get_language()
        if lang == settings.LANGUAGE_CODE:
            return message
        #
        
        translation = Message.objects.gettext(message)

        if self.no_action or not translation:
            return translation % context
        #

        user = context.get('user', None)
        request = context.get('request', None)
        
        if (request is None) or (user is None):
            if settings.DEBUG:
                # warn
                print 'TRANSLATE: user or request not found! - request:', request, 'user:', user
            return translation % context
        #
        
        if user.is_anonymous() or not user.has_perm('change_translation'):
            return translation % context
        #
        
        try:
            message_obj = Message.objects.get(digest=message_digest(translation))
        except Message.DoesNotExist:
            # this can never happen
            return translation % context
        #
        
        path = '?' + urllib.urlencode({'path': request.path})        
        edit_trans = gettext('edit translation')
        translation = translation % context
        digest = message_obj.digest
        
        return TRANS_LINK % locals()
    # render
# TranslateNode

# ========================================================================
# blocktranslate
# ========================================================================

@register.tag
def translate(parser, token):
    """
    This will translate the string for the current language
    using database based dictionary.
    
    Based on i18n trans tag.

    Usage::

        {% translate "this is a test" %}

    This will run the string through the translation engine.
    
    There is a second form::

        {% translate "this is a test" no_action %}

    This will run the string through the translation engine
    without showing translation links for unkown messages
    regardles of current user rights.
    
    You can use variables instead of constant strings
    to translate stuff you marked somewhere else::

        {% translate variable %}

    This will just try to translate the contents of
    the variable ``variable``.
    """
    
    class TranslateParser(TokenParser):
        def top(self):
            no_action = False
            value = self.value()
            
            if self.more():
                if self.tag() == 'no_action':
                    no_action = True
                else:
                    raise TemplateSyntaxError, "'translate' has no options"
            #
            return value, no_action
        #
    # TranslateParser
    
    value, no_action = TranslateParser(token.contents).top()
    return TranslateNode(value, no_action)
# translate

class BlockTranslateNode(TranslateNode):
    """ used i18n BlockTranslateNode as a starting point for this """
    
    def __init__(self, extra_context, message, no_action):
        super(BlockTranslateNode, self).__init__(message, no_action)
        self.extra_context = extra_context
    #

    def render_token_list(self, tokens):
        result = []
        for token in tokens:
            if token.token_type == TOKEN_TEXT:
                result.append(token.contents)
            elif token.token_type == TOKEN_VAR:
                result.append('%%(%s)s' % token.contents)
        return ''.join(result)
    #

    def render(self, context):
        context.push()
        
        for var, val in self.extra_context.items():
            context[var] = val.resolve(context)
        #
        
        message = self.render_token_list(self.message).strip()
        
        result = super(BlockTranslateNode, self).render(context)
        context.pop()
        
        return result
    #
# BlockTranslateNode

@register.tag
def blocktranslate(parser, token):
    """
    This will translate a block of text with parameters.

    Usage::

        {% blocktranslate with foo|filter as bar and baz|filter as boo %}
        This is {{ bar }} and {{ boo }}.
        {% endblocktranslate %}
        
    Based on i18n blocktrans tag.
    """
    
    class BlockTranslateParser(TokenParser):

        def top(self):
            extra_context = {}
            no_action = False
            while self.more():
                tag = self.tag()
                if tag == 'with' or tag == 'and':
                    value = self.value()
                    if self.tag() != 'as':
                        raise TemplateSyntaxError, "variable bindings in 'blocktrans' must be 'with value as variable'"
                    extra_context[self.tag()] = parser.compile_filter(value)
                elif tag == 'no_action':
                    no_action = True
                else:
                    raise TemplateSyntaxError, "unknown subtag %s for 'blocktrans' found" % tag
            return extra_context, no_action
        #
    #
    extra_context, no_action = BlockTranslateParser(token.contents).top()
    
    message = []
    
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            message.append(token)
        else:
            break
    #
    
    if token.contents.strip() != 'endblocktranslate':
        raise TemplateSyntaxError, "'blocktranslate' doesn't allow other block tags (seen %r) inside it" % token.contents

    return BlockTranslateNode(extra_context, message, no_action)
# blocktranslate

# ========================================================================
# language name
# ========================================================================

@register.simple_tag
def language_name():
    """ return current language name translated to current locale
    
    Usage::
    
        {% language_name %}
    """

    lang = get_language()
    for cd, name in settings.LANGUAGES:
        if cd == lang:
            return str(name)
    #
    
    # this can never happen
    raise TemplateSyntaxError, "'language_name' BUG: unknown language encountered (%r)" % lang
# language_name

CODES = {
    '- ': 'unique_1', 
    '+ ': 'unique_2', 
    ' ': 'common', 
    '? ': 'not_present', 
}

# ========================================================================
# diff
# ========================================================================

@register.simple_tag
def diff(string1, string2):
    """ create table with diff
    
    Usage::
    
        {% diff str1 str2 %}
    """
    
    d = Differ()
    lst = list(d.compare(string1.splitlines(1), string2.splitlines(1)))
    ret = ['<div class="diff">']
    for ln in lst:
        code = ln[:2]
        ret.append('<div class="%s"><span class="mark">%s</span>%s</div>' \
                    % (CODES[code], code, ln[2:]))
    #
    ret.append('</div>')
    return '\n'.join(ret)
# diff

# ========================================================================
# simmilar
# ========================================================================

class GetSimmilarNode(Node):
    def __init__(self, message, variable):
        self.variable = variable
        self.message = message
    #

    def render(self, context):
        message = resolve_variable(self.message, context)
        if message:
            context[self.variable] = Message.objects.simmilar(message)
        return ''
    #
# GetSimmilarNode

@register.tag
def simmilar(parser, token):
    """ return all simmilar messages
    
    Usage::
    
        {% simmilar <message> as <var> %}
    """

    args = token.contents.split()
    
    if len(args) != 4 or args[2] != 'as':
        raise TemplateSyntaxError, "'simmilar' syntax error (got %r)" % args
    #
    return GetSimmilarNode(args[1], args[3])
# simmilar
