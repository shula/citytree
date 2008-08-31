"""
Template tags designed to work with applications which use comment
moderation.

"""


from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import get_model
from django.contrib.comments.models import Comment
from django.contrib.comments.templatetags import comments
from django.contrib.contenttypes.models import ContentType


class PublicCommentCountNode(comments.CommentCountNode):
    def render(self, context):
        # TODO: Broken (also, subsumed by comments indjango 1.0, somewhat at least.
        from django.conf import settings
        manager = Comment.objects
        if self.context_var_name is not None:
            object_id = self.context_var_name.resolve(context)
        comment_count = manager.filter(object_id__exact=object_id,
                                       content_type__app_label__exact=self.package,
                                       content_type__model__exact=self.module,
                                       site__id__exact=settings.SITE_ID,
                                       is_removed__exact=False).count()
        context[self.var_name] = comment_count
        return ''


#class DoPublicCommentList(comments.CommentListNode):
def get_public_comment_list(parser, token):
    """
    Retrieves comments for a particular object and stores them in a
    context variable.

    The difference between this tag and Django's built-in comment list
    tags is that this tag will only return comments with
    ``is_removed=False``. If your application uses any sort of comment
    moderation which sets ``is_removed=True``, you'll probably want to
    use this tag, as it makes the template logic simpler by only
    returning approved comments.
    
    Syntax::
    
        {% get_public_comment_list for [app_name].[model_name] [object_id] as [varname] %}
    
    When called as ``get_public_comment_list``, this tag retrieves
    instances of ``Comment`` (comments which require
    registration).
    
    To retrieve comments in reverse order (e.g., newest comments
    first), pass 'reversed' as an extra argument after ``varname``.
    
    So, for example, to retrieve registered comments for a flatpage
    with ``id`` 12, use like this::
    
        {% get_public_comment_list for flatpages.flatpage 12 as comment_list %}
    
    To retrieve comments for the same object::
    
        {% get_public_comment_list for flatpages.flatpage 12 as comment_list %}
    
    To retrieve in reverse order (newest comments first)::
    
        {% get_public_comment_list for flatpages.flatpage 12 as comment_list reversed %}
        
    """
    bits = token.contents.split()
    if len(bits) not in (6, 7):
        raise template.TemplateSyntaxError("'%s' tag takes 5 or 6 arguments" % bits[0])
    if bits[1] != 'for':
        raise template.TemplateSyntaxError("first argument to '%s' tag must be 'for'" % bits[0])
    try:
        app_name, model_name = bits[2].split('.')
    except ValueError:
        raise template.TemplateSyntaxError("second argument to '%s' tag must be in the form 'app_name.model_name'" % bits[0])
    model = get_model(app_name, model_name)
    if model is None:
        raise template.TemplateSyntaxError("'%s' tag got invalid model '%s.%s'" % (bits[0], app_name, model_name))
    content_type = ContentType.objects.get_for_model(model)
    var_name, object_id = None, None
    if bits[3].isdigit():
        object_id = bits[3]
        try:
            content_type.get_object_for_this_type(pk=object_id)
        except ObjectDoesNotExist:
            raise template.TemplateSyntaxError("'%s' tag got reference to %s object with id %s, which doesn't exist" % (bits[0], content_type.name, object_id))
    else:
        var_name = bits[3]
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    if len(bits) == 7:
        if bits[6] != 'reversed':
            raise template.TemplateSyntaxError("sixth argument to '%s' tag, if given, must be 'reversed'" % bits[0])
        ordering = '-'
    else:
        ordering = ''
    return comments.CommentListNode(app_name, model_name, var_name, object_id, bits[5], ordering, extra_kwargs={ 'is_removed__exact': False })


#class DoPublicCommentCount(CommentCountNode):
def get_public_comment_count(parser, token):
    """
    Retrieves the number of comments attached to a particular object
    and stores them in a context variable.

    The difference between this tag and Django's built-in comment
    count tags is that this tag will only count comments with
    ``is_removed=False``. If your application uses any sort of comment
    moderation which sets ``is_removed=True``, you'll probably want to
    use this tag, as it gives an accurate count of the comments which
    will be publicly displayed.
    
    Syntax::
    
        {% get_public_comment_count for [app_name].[model_name] [object_id] as [varname] %}
    
    Example::

        {% get_public_comment_count for weblog.entry entry.id as comment_count %}

    When called as ``get_public_comment_list``, this tag counts
    instances of ``Comment`` (comments which require
    registration).

    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("'%s' tag takes five arguments" % bits[0])
    if bits[1] != 'for':
        raise template.TemplateSyntaxError("first argument to '%s' tag must be 'for'" % bits[0])
    try:
        app_name, model_name = bits[2].split('.')
    except ValueError:
        raise template.TemplateSyntaxError("second argument to '%s tag must be in the format app_name.model_name'" % bits[0])
    model = get_model(app_name, model_name)
    if model is None:
        raise template.TemplateSyntaxError("'%s' tag got invalid model '%s.%s'" % (bits[0], app_name, model_name))
    content_type = ContentType.objects.get_for_model(model)
    var_name, object_id = None, None
    if bits[3].isdigit():
        object_id = bits[3]
        try:
            content_type.get_object_for_this_type(pk=object_id)
        except ObjectDoesNotExist:
            raise template.TemplateSyntaxError("'%s' tag got reference to %s object with id %s, which doesn't exist" % (bits[0], content_type.name, object_id))
    else:
        var_name = bits[3]
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    
    return PublicCommentCountNode(app_name, model_name, var_name, object_id, bits[5])

register = template.Library()
register.tag('get_public_comment_list', get_public_comment_list)
register.tag('get_public_comment_count', get_public_comment_count)

