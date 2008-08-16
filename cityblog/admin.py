from django.contrib import admin

from models import Blog, Flag, Post, PostImage, Subject
from workshop.models import BlogWorkshop

class BlogWorkshopInline(admin.TabularInline):
    model = BlogWorkshop
    extra = 1
    max_num = 1

class BlogAdmin(admin.ModelAdmin):
    fieldsets = (
    (None,
        {'fields': ('name', 'slug', 'header_image', 'header_image_label', 'teaser_photo', 'teaser_photo_label', 
    'teaser_text', 'authors', 'display_in_menu', 'member_blog')}
    ),
   )
    list_display   = ('name', 'is_workshop', 'member_blog' )
    list_filter    = ('member_blog', )
    inlines = [
            BlogWorkshopInline
    ]

class FlagAdmin(admin.ModelAdmin):
    list_display  = ( 'name', 'blog' )

class PostAdmin(admin.ModelAdmin):
    # The real editing is not done here, but in desk. Still, we can reuse
    # stuff I guess, or just have this as a test bed.
    #js = fckeditor_textarea_js_list

    fieldsets = (
    # almost everything is normal
    (None, {'fields': ('blog', 'author', 'title', 'post_style', 'post_date', 'image',
        'image_caption', 'image_label', 'flags', 'draft', 'enable_comments')}),
    # some stuff should be displayed using some rich text editing - we use a class that is later
    # extracted with a javascript hook, and then the wysiwyg editor (see js above) is used.
    (None, {
        'fields':  ('teaser_text', 'text'),
        'classes': ('wysiwyg'),
        })
    )
    list_display   = ('blog', 'title', 'author', 'time_modified', 'draft' )
    list_filter    = ('blog', 'time_modified', 'post_style', )
    ordering       = ('-post_date',)

class PostImageAdmin(admin.ModelAdmin):
  fieldsets = (
    (None, {'fields': ('post', 'image', 'index', 'label', 'caption' )}),
   )
   
  list_display = ('index', 'label', 'image')

class SubjectAdmin(admin.ModelAdmin):
  fieldsets = (
      (None, {'fields': ('name', 'slug', 'image', 'label', 'ordering', 'flags', 'blogs', 'teaser_text' )}),
     )

for model, modeladmin in [
        (Blog, BlogAdmin),
        (Flag, FlagAdmin),
        (Post, PostAdmin),
        (PostImage, PostImageAdmin),
        (Subject, SubjectAdmin),
        ]:
    admin.site.register(model, modeladmin)

