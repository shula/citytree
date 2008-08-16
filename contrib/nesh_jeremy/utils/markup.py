from django import template
from django.contrib.markup.templatetags import markup
from django.utils import html
from django.utils.translation import gettext_lazy as _
import re

MARKUP_PLAIN_TEXT, MARKUP_HTML, MARKUP_TEXTILE, MARKUP_MARKDOWN, MARKUP_REST = range(1, 6)
MARKUP_FILTERS = (
           (MARKUP_PLAIN_TEXT, _('Plain Text'),),
           (MARKUP_HTML, _('HTML'),),
           (MARKUP_TEXTILE, _('Textile'),),
           (MARKUP_MARKDOWN, _('Markdown'),),
           (MARKUP_REST, _('Restructured Text'),),
           )

_IMG_TAG_RE = re.compile(r'\{\{\s*image\s*([\w\-]+)\s*\}\}')
_IMG_REPLACE = r'\{\{\s*image\s*%s\s*\}\}'

def render_content(content, text_type, images=None):
    try:
        if not content:
            return ''

        text_type = int(text_type)
        
        # the big bad switch ;)
        if text_type == MARKUP_PLAIN_TEXT:
            ret = html.linebreaks(html.escape(content))
        elif text_type == MARKUP_HTML:
            ret = html.clean_html(content)
        elif text_type == MARKUP_TEXTILE:
            ret = markup.textile(content)
        elif text_type == MARKUP_MARKDOWN:
            ret = markup.markdown(content)
        elif text_type == MARKUP_REST:
            ret = markup.restructuredtext(content)
        else:
            # this can never happen
            return 'UNKNOWN CONTENT %d' % text_type

    except template.TemplateSyntaxError, err:
        return 'ERROR: %s' % err

    new = ret[:] # XXX why?
    
    if isinstance(new, unicode):
        new = new.encode('utf-8')
    
    for tag in _IMG_TAG_RE.findall(ret):
        if images is not None:
            try:
                img = images.get(slug=tag) #IGNORE:E1101
                new = re.sub(_IMG_REPLACE % tag, '<img src="%s" />' % img.image.url, new)
            # XXX what if images don't have .model?
            except images.model.DoesNotExist: #IGNORE:E1101
                new = re.sub(_IMG_REPLACE % tag, '<div class="error">NO IMAGE %s</div>' % tag, new)
        else:
            new = re.sub(_IMG_REPLACE % tag, '<div class="error">NO IMAGE %s</div>' % tag, new)
    return new
