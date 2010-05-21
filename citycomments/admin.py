from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django.contrib.comments.models import Comment

from models import CityComment

def delete_selected(modeladmin, request, queryset):
    if modeladmin.has_delete_permission(request):
        for obj in queryset:
            obj.delete()
        modeladmin.message_user(request,
            "Successfully deleted %d." % (len(queryset))
        )

def hide_selected(modeladmin, request, queryset):
    if modeladmin.has_delete_permission(request):
        for obj in queryset:
            obj.is_removed = True
            obj.is_public = False
            obj.save()
            # TODO - log this.
            #object_repr = str(obj)
            #modeladmin.log_deletion(request, obj, object_repr)
        # TODO - update should work. using iteration instead
        #objects.update(is_removed=True, is_public=False)
        modeladmin.message_user(request,
            "Successfully hidden %d." % (len(queryset)))

hide_selected.short_description = "Hide selected %(verbose_name_plural)s"
delete_selected.short_description = "Delete selected %(verbose_name_plural)s (Please be careful!)"

class CommentAdmin(admin.ModelAdmin):
    def post(self, obj):
        return obj.content_object

    actions = [hide_selected, delete_selected]

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


admin.site.register(CityComment, CommentAdmin)

