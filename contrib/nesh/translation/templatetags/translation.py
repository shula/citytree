# stdlib
from difflib import Differ
import urllib
# django
from django.conf import settings
from django.template import Node
from django.template import TOKEN_BLOCK, TOKEN_TEXT, TOKEN_VAR
from django.template import TemplateSyntaxError, Library, Node, resolve_variable, TokenParser
from django.utils.translation import get_language, gettext
# nesh
from nesh.translation.models import Message, message_digest

register = Library()

# ========================================================================
# translate
# ========================================================================
TRANS_LINK = """<div class="translate_block">
    %(translation)s
    <a href="%(translate_root)s/edit/%(digest)s/%(path)s" class="translation" rel="nofollow" title="%(edit_trans)s">
        <image src="%(icon)s" height="16" width="16" alt="%(edit_trans)s" />
    </a>
</div>
"""

class TranslateNode(Node):
    def __init__(self, message, noop):
        self.message = message
        self.noop = noop

    def render(self, context, message=None):
        if message is None:
            message = resolve_variable(self.message, context)
        icon = getattr(settings, 'TRANSLATION_ICON', '%s/img/icons/edit.png' % settings.MEDIA_URL.rstrip('/'))
        translate_root = getattr(settings, 'TRANSLATE_ROOT', '/translate').rstrip('/')
        lang = get_language()
        if lang == settings.LANGUAGE_CODE:
            return message

        translation = Message.objects.gettext(message)

        if self.noop or not translation:
            return translation % context

        user = context.get('user', None)
        request = context.get('request', None)
        
        if (request is None) or (user is None):
            if settings.DEBUG:
                print 'TRANSLATE: user or request not found!'
            return translation % context

        if user.is_anonymous() or not user.has_perm('change_translation'):
            return translation % context

        try:
            message_obj = Message.objects.get(digest=message_digest(translation))
        except Message.DoesNotExist: #IGNORE:E1101
            # this can never happen
            return translation % context

        path = '?' + urllib.urlencode({'path': request.path})        
        edit_trans = gettext('edit translation')
        translation = translation % context
        digest = message_obj.digest
        
        return TRANS_LINK % locals()

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

        {% translate "this is a test" noop %}

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
            noop = False
            value = self.value()
            
            if self.more():
                if self.tag() == 'noop':
                    noop = True
                else:
                    raise TemplateSyntaxError, "'translate' has no options"
            return value, noop

    value, noop = TranslateParser(token.contents).top()
    return TranslateNode(value, noop)

class BlockTranslateNode(TranslateNode):
    """ used i18n BlockTranslateNode as a starting point for this """
    
    def __init__(self, extra_context, message, noop):
        super(BlockTranslateNode, self).__init__(message, noop)
        self.extra_context = extra_context

    def render_token_list(self, tokens):
        result = []
        for token in tokens:
            if token.token_type == TOKEN_TEXT:
                result.append(token.contents)
            elif token.token_type == TOKEN_VAR:
                result.append('%%(%s)s' % token.contents)
        return ''.join(result)

    def render(self, context):
        context.push()
        
        for var, val in self.extra_context.items():
            context[var] = val.resolve(context)

        message = self.render_token_list(self.message).strip()
        
        if get_language() == settings.LANGUAGE_CODE:
            result = message % context
        else:
            result = super(BlockTranslateNode, self).render(context, message=message)

        context.pop()
        
        return result

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
            noop = False
            while self.more():
                tag = self.tag()
                if tag == 'with' or tag == 'and':
                    value = self.value()
                    if self.tag() != 'as':
                        raise TemplateSyntaxError, "variable bindings in 'blocktrans' must be 'with value as variable'"
                    extra_context[self.tag()] = parser.compile_filter(value)
                elif tag == 'noop':
                    noop = True
                else:
                    raise TemplateSyntaxError, "unknown subtag %s for 'blocktrans' found" % tag
            return extra_context, noop

    extra_context, noop = BlockTranslateParser(token.contents).top()
    
    message = []
    
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            message.append(token)
        else:
            break

    if token.contents.strip() != 'endblocktranslate':
        raise TemplateSyntaxError, "'blocktranslate' doesn't allow other block tags (seen %r) inside it" % token.contents

    return BlockTranslateNode(extra_context, message, noop)

# ========================================================================
# language name
# ========================================================================

def get_language_name(lang):
    for cd, name in settings.LANGUAGES:
        if cd == lang:
            return str(name)
    return None

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
    # this can never happen
    raise TemplateSyntaxError, "'language_name' BUG: unknown language encountered (%r)" % lang

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

    ret.append('</div>')
    return '\n'.join(ret)

# ========================================================================
# similar
# ========================================================================

class GetSimilarNode(Node):
    def __init__(self, message, variable):
        self.variable = variable
        self.message = message

    def render(self, context):
        message = resolve_variable(self.message, context)
        if message:
            context[self.variable] = Message.objects.similar(message)
        return ''

@register.tag
def similar(parser, token):
    """ return all similar messages
    
    Usage::
    
        {% similar <message> as <var> %}
    """

    args = token.contents.split()
    
    if len(args) != 4 or args[2] != 'as':
        raise TemplateSyntaxError, "'similar' syntax error (got %r)" % args

    return GetSimilarNode(args[1], args[3])

# ========================================================================
# get_untranslated_for
# ========================================================================

class GetUntranslatedForNode(Node):
    def __init__(self, message):
        self.message = message

    def render(self, context):
        message = resolve_variable(self.message, context)

        if not message:
            return ''

        user = context.get('user', None)
        request = context.get('request', None)
        
        if (request is None) or (user is None):
            if settings.DEBUG:
                print 'TRANSLATE: user or request not found!'
            return ''

        untrans = Message.objects.get_untranslated_for(message)
        
        path = '?' + urllib.urlencode({'next': request.path})        
        translate = gettext('translate to')
        digest = message_digest(self.message)
        MR = settings.MEDIA_URL.rstrip('/')
        translate_root = getattr(settings, 'TRANSLATE_ROOT', '/translate').rstrip('/')

        if len(untrans):
            ret = ['<ul class="untranslated">']
            for un in untrans:
                name = gettext(get_language_name(un))
                flag = '<img src="%(MR)s/img/flags/%(un)s.png" alt="%(name)s" title="%(translate)s %(name)s" style="vertical-align: middle;" />' % locals()
                lnk = '<a href="%(translate_root)s/translate/%(digest)s/%(un)s/%(path)s" class="translation" rel="nofollow"">%(flag)s</a>' % locals()
                ret.append('<li>%s</li>' % lnk)
            ret.append('</ul>')
            return ''.join(ret)
        else:
            return ''

@register.tag
def get_untranslated_for(parser, token):
    """ return <ul class="untranslated"> of all languages for which this message is untranslated
        with links for translation.
    
    Usage::
    
        {% get_untranslated_for <message> %}
    """

    args = token.contents.split()
    
    if len(args) != 2:
        raise TemplateSyntaxError, "%s: syntax error (got %r)" % (args[0], args[1:])
    return GetUntranslatedForNode(args[1])

@register.filter
def translate_from_db(text):
    """Translates a text from the database"""
    # create a node without text
    translation_node = TranslateNode(None, noop=False)
    # now really render the text.
    # the context is empty, as it is not needed, just a dummy.
    translation = translation_node.render({}, text)
    # render gave back a string we can which we can return now
    return translation