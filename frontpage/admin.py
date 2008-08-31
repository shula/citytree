from django.contrib import admin

from django.contrib.admin.models import User

from models import Teaser, FrontpageHeaderImage, FrontPage

class TeaserAdmin(admin.ModelAdmin):
    fieldssets = (
            (None, {'fields': ('image',
            'url',
            'label',
            'title',
            'teaserText'
            )}),
           )
 
class FrontpageHeaderImageAdmin(admin.ModelAdmin):
     fieldsets = (
                (None, {'fields': ('image',
                'image_label'
                )}),
               )

class FrontpageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('draft', 'title', 'main_text', 'date', 
        'headerImage', 
        'teaser1',
        'teaser2',
        'teaser3',
        'teaser4',
        'teaser5', 
        )}),
       )
    list_display   = ('title', 'date', 'draft' )
    ordering       = ('-date',)
    search_fields  = ('title',)

admin.site.register(Teaser, TeaserAdmin)
admin.site.register(FrontpageHeaderImage, FrontpageHeaderImageAdmin)
admin.site.register(FrontPage, FrontpageAdmin)

