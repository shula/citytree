from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django.contrib.comments.models import Comment
from batchadmin.admin import BatchModelAdmin, CHECKBOX_NAME, model_ngettext

from models import CityComment

# I've made a small change to django.contrib.ModelAdmin to let me
# set the manager for a particular ModelAdmin using the
# manager=
# property

class CityCommentAdmin(BatchModelAdmin):
    #manager = CityComment.citycomments

    batch_actions=['hide_selected', 'delete_selected']
    def delete_selected(self, request, changelist):
        if self.has_delete_permission(request):
            selected = request.POST.getlist(CHECKBOX_NAME)
            objects = changelist.get_query_set().filter(pk__in=selected)
            n = objects.count()
            if n:
                for obj in objects:
                    obj.delete()
                self.message_user(request, "Successfully deleted %d %s." % (
                    n, model_ngettext(self.opts, n)
                ))
    def hide_selected(self, request, changelist):
        if self.has_delete_permission(request):
            selected = request.POST.getlist(CHECKBOX_NAME)
            objects = changelist.get_query_set().filter(pk__in=selected)
            n = objects.count()
            if n:
                for obj in objects:
                    obj.is_removed = True
                    obj.is_public = False
                    obj.save()
                    # TODO - log this.
                    #object_repr = str(obj)
                    #self.log_deletion(request, obj, object_repr)
                # TODO - update should work. using iteration instead
                #objects.update(is_removed=True, is_public=False)
                self.message_user(request, "Successfully hidden %d %s." % (
                    n, model_ngettext(self.opts, n)
                ))
    hide_selected.short_description = "Hide selected %(verbose_name_plural)s"
    delete_selected.short_description = "Delete selected %(verbose_name_plural)s (Please be careful!)"
 
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

    list_display = ('name', 'post', 'submit_date', 'object_pk', 'ip_address', 'is_public', 'is_removed')
    list_filter = ('submit_date', 'site', 'is_public', 'is_removed')
    date_hierarchy = 'submit_date'
    search_fields = ('comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address', 'phone')
    ordering = ('-submit_date',)

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
# no longer required - just remember to run bin/create_citycomments_from_comments.py
#admin.site.register(Comment, CommentAdmin)

