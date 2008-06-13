# vim: set fileencoding=utf-8 :
import datetime
import random

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 
from django.core.mail import send_mail
from django.template import Context, loader
from django.contrib.sites.models import Site
from nesh.thumbnail.field import ImageWithThumbnailField
from citytree.utils.textUtils import wikiSub
import settings

from utils.randomUtils import make_random_hash

# Javascript stuff - to be moved somewhere more appropriate

# use Dojo - seems to have much more then just an editor, but the editor itself is much less fleshed out.
dojo_textarea_js_list = ['js/admin/DojoTextArea.js']

# TinyMCE is very nice, has tables, right to left support, raw html editing support.
tinymce_textarea_js_list = ['tinymce/tiny_mce.js'
,'js/admin/TinyMCETextArea.js']

fckeditor_textarea_js_list = ['fckeditor/fckeditor.js']

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

    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
      return u'/blogs/%s/' % self.slug
      
    def get_edit_absolute_url(self):
      return u"/desk/mybranches/%s/" % (self.slug)
    
    def get_last_post(self):
      return self.post_set.latest('post_date')

    def get_last_post_as_list(self):
      return [self.post_set.latest('post_date')]

    def get_feed_url(self):
      # import here to avoid a loop, since feeds imports us
      from citytree.cityblog.feeds import LatestPosts_get_feed_url
      return LatestPosts_get_feed_url(self)

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
    
    def __unicode__(self):
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
    draft         = models.BooleanField(help_text='Set to post to make post live on site', default=1, choices=DRAFT_CHOICES, blank=True)
    post_style    = models.PositiveIntegerField('Post Style', help_text='Style in which post is displayed' , blank=False, default=1, choices=POST_STYLE_TYPES )

    # fields required by the comment system
    enable_comments = models.BooleanField(default=1, blank=True, help_text='Set to enable comments on post')
    
    class Admin:
        # The real editing is not done here, but in desk. Still, we can reuse
        # stuff I guess, or just have this as a test bed.
        #js = fckeditor_textarea_js_list

        fields = (
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
      return u'/blogs/posts/%d/' % ( self.id )
      
    def get_absolute_edit_url(self):
      # TODO: is there a better way to keep this in sync? maybe just have the editBlog
      # a constant in the desk.views model?
      d = self.post_date
      return u'/desk/editPost/%d/' % ( self.id )
      
    def get_absolute_preview_url( self ):
      d = self.post_date
      return u'/blogs/preview_post/%d/' % ( self.id )
    
    def __unicode__(self):
        return self.title
    
    def save(self):
        if not self.id:
            # new post
            if self.image_caption is None: self.image_caption= u''
            if( len(self.image_caption) == 0 ):
                if self.image_label is None: self.image_label = u''
                self.image_caption = self.image_label[0:25] #take first 25 letters only
            if self.text is None: self.text = u''
            if self.teaser_text is None: self.teaser_text = u''
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
    
    def __unicode__(self):
      return self.label
      
    def save(self):
        if not self.id:
            # new postImage
            if self.caption is None: self.caption= ''
            if self.label is None: self.label=''
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
      return u'/subjects/%s/' % self.slug
    
  def __unicode__(self):
        return self.name
  
  class Meta:
    ordering = ['ordering']

# Coments moderation using comment_util
from comment_utils.moderation import CommentModerator, moderator, AlreadyModerated

class PostModerator(CommentModerator):

    #akismet = True # need an akismet account for this - and this is not private use.
    email_notification = True
    enable_field = 'enable_comments'
    really_send_email_to_this_person=settings.SEND_EMAIL_ON_COMMENT

    def moderate(self, comment, content_object):
        """
        Determines whether a given comment on a given object should be
        allowed to show up immediately, or should be marked non-public
        and await approval.

        Returns ``True`` if the comment should be moderated (marked
        non-public), ``False`` otherwise.
        
        """
        # import done here to avoid loop.
        from citytree.spamdetector.myspamdetector import spamDetector
        return spamDetector.moderate(comment, content_object)

    def email(self, comment, content_object):
        self._hash = make_random_hash()
        post = content_object # same thing
        if self.really_send_email_to_this_person is None:
            recipient_list = [post.author.email]
        else:
            recipient_list = [self.really_send_email_to_this_person]
        t = loader.get_template('cityblog/post_comment_notification_email.txt')
        site = Site.objects.get_current().name
        from spamdetector.models import allowed_ban_requests
        allowed_ban_requests(ip_address = comment.ip_address, hash=self._hash).save()
        c = Context({ 'comment': comment,
                      'content_object': content_object,
                      'site': site,
                      'hash': self._hash})
        subject = u'[%s] New comment posted on "%s"' % (site, content_object)
        message = t.render(c)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
        
# This is annoying - but for some reason this file gets loaded
# more then once - so I'm forced to catch the AlreadyModerated
# exception, lest django present the dreaded error page.
try:
    i = 0
    moderator.register(post, PostModerator)
except AlreadyModerated:
    i += 1
    print "already moderated: %s" % i

