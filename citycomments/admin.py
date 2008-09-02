from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django.contrib.comments.models import Comment

from models import CityComment

# I've made a small change to django.contrib.ModelAdmin to let me
# set the manager for a particular ModelAdmin using the
# manager=
# property

class CityCommentAdmin(admin.ModelAdmin):
    manager = CityComment.citycomments

    def post(self, obj):
        return obj.content_object

    fieldsets = (
        (None,
           {'fields': ('object_pk', 'site')}
        ),
        (_('Content'),
           {'fields': ('user', 'user_name', 'user_email', 'phone', 'user_url', 'comment')}
        ),
        (_('Metadata'),
           {'fields': ('submit_date', 'ip_address', 'is_public', 'is_removed')}
        ),
     )

    list_display = ('name', 'post', 'object_pk', 'ip_address', 'is_public', 'is_removed')
    list_filter = ('submit_date', 'site', 'is_public', 'is_removed')
    date_hierarchy = 'submit_date'
    search_fields = ('comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address', 'phone')

class CommentAdmin(admin.ModelAdmin):
    def post(self, obj):
        return obj.content_object

    fieldsets = (
        (None,
           {'fields': ('object_pk', 'site')}
        ),
        (_('Content'),
           {'fields': ('user', 'user_name', 'user_email', 'user_url', 'comment')}
        ),
        (_('Metadata'),
           {'fields': ('submit_date', 'ip_address', 'is_public', 'is_removed')}
        ),
     )

    list_display = ('name', 'post', 'object_pk', 'ip_address', 'is_public', 'is_removed')
    list_filter = ('submit_date', 'site', 'is_public', 'is_removed')
    date_hierarchy = 'submit_date'
    search_fields = ('comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address')


admin.site.register(CityComment, CityCommentAdmin)
admin.site.register(Comment, CommentAdmin)

