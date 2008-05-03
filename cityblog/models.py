# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 
from django.core.mail import send_mail
from django.template import Context, loader
from django.contrib.sites.models import Site
from nesh.thumbnail.field import ImageWithThumbnailField
from citytree.utils.textUtils import wikiSub


#Object representing a blog, a blog can have many authors.
class blog(models.Model):
    name          = models.CharField(max_length=200,blank=False)
    slug          = models.SlugField('blog url identifier', unique=True)
    authors       = models.ManyToManyField(User,verbose_name='list of blog authors')
    header_image  = ImageWithThumbnailField(blank=True,upload_to='blog_header_images/%Y/%m/%d',
                                                    width_field='header_image_width', 
                                                    height_field='header_image_height',
                                                    mask_file=settings.HEADER_MASK, 
                                                    logo_file=settings.SITE_LOGO, 
                                                    help_text='<b>MUST BE</b>: 808x160 image!')
    header_image_width    = models.PositiveIntegerField(blank=True,null=True)
    header_image_height   = models.PositiveIntegerField(blank=True,null=True)
    header_image_label    = models.CharField(max_length=255,blank=True)
    
    teaser_photo          = ImageWithThumbnailField('Image to display along with teaser', 
                                                     upload_to='blog_teaser_images/%Y/%m/%d',
                                                     width_field='teaser_image_width', 
                                                     height_field='teaser_image_height', 
                                                     blank=True, null=True)
    teaser_image_width    = models.PositiveIntegerField(blank=True,null=True)
    teaser_image_height   = models.PositiveIntegerField(blank=True,null=True)
    teaser_photo_label    = models.TextField(blank=True, null=True) 
    teaser_text           = models.TextField(blank=True, null=True)
    teaser_photo_caption  = models.CharField("Label for teaser photo", max_length=200,blank=True, null=True)
    
    hits                  = models.PositiveIntegerField(blank=True,null=True)
    display_in_menu       = models.BooleanField( "Display in Menu", default=1 )

    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
      return '/blogs/%s/' % self.slug
      
    def get_edit_absolute_url(self):
      return "/desk/mybranches/%s/" % (self.slug)
    
    def get_last_post(self):
      return self.post_set.latest('post_date')

    def get_last_post_as_list(self):
      return [self.post_set.latest('post_date')]

    class Admin:
      fields = (
        (None, {'fields': ('name', 'slug', 'header_image', 'header_image_label', 'teaser_photo', 'teaser_photo_label', 
        'teaser_text', 'authors', 'display_in_menu')}),
       )
        

#Categories a blog post can be placed under
class flag(models.Model):
    name         = models.CharField(max_length=50)
    
    #blog in which this flag is viewable (null = all blogs)
    blog         = models.ForeignKey( blog, blank=True, null=True )
    
    def __str__(self):
        return self.name
    
    class Admin:
        list_display  = ( 'name', 'blog' )
        pass
    
class post(models.Model):
    DRAFT_CHOICES = (
      ( 1, 'טיוטה'),
      ( 0, 'מאושר') )
    
    POST_STYLE_SMALL_LEAF = 1
    POST_STYLE_ARTICLE = 2
    POST_STYLE_GALLERY = 3
    
    POST_STYLE_TYPES = (
        ( POST_STYLE_SMALL_LEAF, 'עלה קטן' ),
        ( POST_STYLE_ARTICLE, 'מאמר' ),
        ( POST_STYLE_GALLERY, 'גלריה' ),
    )

    blog          = models.ForeignKey(blog)
    author        = models.ForeignKey(User, blank=False)
    
    #slug          = models.SlugField('blog url identifier', unique=True)
    
    #User editable date for when the post should be shown as being modified
    post_date     = models.DateTimeField(blank=False)
    
    #Hidden field so that you can see when the post was really last changed
    time_modified = models.DateTimeField('Time Of Last Edit', auto_now=True)
    
    title         = models.CharField('Post Title', max_length=200,blank=False)
    
    image         = ImageWithThumbnailField(upload_to='blog_images/%Y/%m/%d',width_field='image_width', height_field='image_height', blank=True)
    image_label   = models.TextField('Text Displayed as you hover over the image',
                                                blank=True, null=True)
    image_caption = models.CharField('post image Caption -', 
                                     help_text='If left blank then contents of image label are copied here', max_length=200,blank=True, null=True)
    image_height  = models.PositiveIntegerField(blank=True,null=True)
    image_width   = models.PositiveIntegerField(blank=True,null=True)
    
    teaser_text          = models.TextField(blank=False, null=True)
    teaser_rendered_text = models.TextField(blank=True, null=True)
    
    text          = models.TextField(help_text="If left blank then Text is copied here", blank=True, null=True)
    rendered_text = models.TextField('Entry body as HTML', blank=True, null=True)
    
    flags         = models.ManyToManyField( flag, blank=True, null=True )
    draft         = models.BooleanField(help_text='Set to post to make post live on site', default=1, choices=DRAFT_CHOICES, blank=False)
    post_style    = models.PositiveIntegerField('Post Style', help_text='Style in which post is displayed' , blank=False, default=1, choices=POST_STYLE_TYPES )

    # fields required by the comment system
    enable_comments = models.BooleanField(default=1,blank=False,help_text='Set to enable comments on post')
    
    class Admin:
       fields = (
        (None, {'fields': ('blog', 'author', 'title', 'post_style', 'post_date', 'image', 'image_caption', 'image_label', 'teaser_text',
            'text', 'flags', 'draft')}),
       )
       list_display   = ('blog', 'title', 'author', 'time_modified', 'draft' )
       list_filter    = ('blog', 'time_modified')
       ordering       = ('-post_date',)
       
    class Meta:
        ordering = ['-post_date']
    
    def is_gallery(self):
        return self.post_style == self.POST_STYLE_GALLERY

    def is_article(self):
        return self.post_style == self.POST_STYLE_ARTICLE

    def get_absolute_url(self):
      d = self.post_date
      return '/blogs/posts/%d/' % ( self.id )
      
    def get_absolute_edit_url(self):
      # TODO: is there a better way to keep this in sync? maybe just have the editBlog
      # a constant in the desk.views model?
      d = self.post_date
      return '/desk/editPost/%d/' % ( self.id )
      
    def get_absolute_preview_url( self ):
      d = self.post_date
      return '/blogs/preview_post/%d/' % ( self.id )
    
    def __str__(self):
        return self.title
    
    def save(self):
        if not self.id:
          if( len(self.image_caption) == 0 ):
              self.image_caption = self.image_label[0:25] #take first 25 letters only
              
          #if( len(self.text) == 0 ):
          #    self.text = self.teaser_text
          
        self.time_modified        = datetime.date.today()
        self.rendered_text        = wikiSub(self.text)
        self.teaser_rendered_text = wikiSub(self.teaser_text)
        super(post, self).save() # Call the "real" save() method.

class postImage(models.Model):
    post          = models.ForeignKey(post)
    image         = ImageWithThumbnailField(upload_to='blog_images/%Y/%m/%d',width_field='image_width', height_field='image_height')
    image_height  = models.PositiveIntegerField(blank=True,null=True)
    image_width   = models.PositiveIntegerField(blank=True,null=True)
    index         = models.PositiveIntegerField("For Image Ordering", blank=True,null=True)
    label         = models.TextField(help_text="Displayed when the image is hovered over", blank=True, null=True)
    caption       = models.CharField(help_text="Title of image, displayed in html", max_length=200,blank=True, null=True)
    
    def __str__(self):
      return self.label
      
    def save(self):
        if not self.id:
            if( len(self.caption) == 0 ):
                self.caption = self.label[0:25]
                
        super( postImage, self ).save()
        
    class Admin:
      fields = (
        (None, {'fields': ('post', 'image', 'index', 'label', 'caption' )}),
       )
       
      list_display = ('index', 'label', 'image')
    
class subject(models.Model):
  """
  Reshiymat Nos'iym
  """
  name          = models.CharField(max_length=200,blank=False)
  slug          = models.SlugField('subject url identifier', unique=True)
  teaser_text   = models.TextField( blank=True, null=True )
  
  image         = ImageWithThumbnailField('Header Image',
                                upload_to='subject_header_images/%Y/%m/%d',
                                width_field='image_width', height_field='image_height',
                                mask_file=settings.HEADER_MASK )
  image_height  = models.PositiveIntegerField(blank=True,null=True)
  image_width   = models.PositiveIntegerField(blank=True,null=True)
  label         = models.TextField(help_text="Displayed when the image is hovered over", blank=True, null=True)
  
  ordering      = models.PositiveIntegerField('Ordering:', blank=True,null=True, help_text='For custom ordering of Subjects')
  
  flags         = models.ManyToManyField(flag,verbose_name='flags to include', blank=True, null=True)
  blogs         = models.ManyToManyField(blog, help_text="currently not in use", verbose_name='blogs to include', blank=True, null=True)
  
  class Admin:
      fields = (
          (None, {'fields': ('name', 'slug', 'image', 'label', 'ordering', 'flags', 'blogs', 'teaser_text' )}),
         )
    
  def get_absolute_url( self ):
      return '/subjects/%s/' % self.slug
    
  def __str__(self):
        return self.name
  
  class Meta:
    ordering = ['ordering']

# Coments moderation using comment_util
from comment_utils.moderation import CommentModerator, moderator, AlreadyModerated

class PostModerator(CommentModerator):
    #akismet = True # need an akismet account for this - and this is not private use.
    email_notification = True
    enable_field = 'enable_comments'
    def email(self, comment, content_object):
        post = content_object # same thing
        recipient_list = [post.author.email]
        t = loader.get_template('cityblog/post_comment_notification_email.txt')
        site = Site.objects.get_current().name
        c = Context({ 'comment': comment,
                      'content_object': content_object,
                      'site': site})
        subject = '[%s] New comment posted on "%s"' % (site, content_object)
        message = t.render(c)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
        

try:
    i = 0
    moderator.register(post, PostModerator)
except AlreadyModerated:
    i += 1
    print "already moderated: %s" % i

