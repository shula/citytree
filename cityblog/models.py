# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import datetime
import random

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 
from django.template import RequestContext, Context, loader
from django.contrib.sites.models import Site

from nesh.thumbnail.field import ImageWithThumbnailField

from citytree.utils.textUtils import wikiSub
from utils.randomUtils import make_random_hash
from utils.email import send_email_to
import settings

# Javascript stuff - to be moved somewhere more appropriate

# use Dojo - seems to have much more then just an editor, but the editor itself is much less fleshed out.
dojo_textarea_js_list = ['js/admin/DojoTextArea.js']

# TinyMCE is very nice, has tables, right to left support, raw html editing support.
tinymce_textarea_js_list = ['tinymce/tiny_mce.js'
,'js/admin/TinyMCETextArea.js']

fckeditor_textarea_js_list = ['fckeditor/fckeditor.js']

#Object representing a blog, a Blog can have many authors.
class Blog(models.Model):
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

    # I could have used the same solution as for the workshop question - 
    # is_workshop is the other solution.
    member_blog           = models.BooleanField( "Is this blog open for members?", default=False)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
      return u'/branches/%s/' % self.slug
      
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

    def is_workshop(self):
        return self.blogworkshop_set.count() > 0
    is_workshop.boolean = True # prettier display in Admin
       

#Categories a blog post can be placed under
class Flag(models.Model):
    name         = models.CharField(max_length=50)
    
    #blog in which this flag is viewable (null = all blogs)
    blog         = models.ForeignKey( Blog, blank=True, null=True )
    
    def __unicode__(self):
        return self.name
    
class Post(models.Model):
    DRAFT_CHOICES = (
      ( 1, 'טיוטה'),
      ( 0, 'מאושר') )
    
    POST_STYLE_SMALL_LEAF = 1
    POST_STYLE_ARTICLE = 2
    POST_STYLE_GALLERY = 3
    POST_STYLE_WORKSHOP = 4
    
    POST_STYLE_TYPES = (
        ( POST_STYLE_SMALL_LEAF, 'עלה קטן' ),
        ( POST_STYLE_ARTICLE, 'מאמר' ),
        ( POST_STYLE_GALLERY, 'גלריה' ),
        ( POST_STYLE_WORKSHOP, 'סדנה' ),
    )

    blog          = models.ForeignKey(Blog)
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
    
    teaser_text          = models.TextField(blank=True, null=True, help_text='הבקיצור יופיע בעמוד הראשי של הבלוג, ויכול גם להוות את העלה כולו (במקרב של "עלה קטן")')
    teaser_rendered_text = models.TextField(blank=True, null=True)
    
    text          = models.TextField(help_text="If left blank then Text is copied here", blank=True, null=True)
    rendered_text = models.TextField('Entry body as HTML', blank=True, null=True)
    
    flags         = models.ManyToManyField( Flag, blank=True, null=True )
    draft         = models.BooleanField(help_text='Set to post to make post live on site', default=1, choices=DRAFT_CHOICES, blank=True)
    post_style    = models.PositiveIntegerField('Post Style', help_text='Style in which post is displayed' , blank=False, default=1, choices=POST_STYLE_TYPES )

    # fields required by the comment system
    enable_comments = models.BooleanField(default=1, blank=True, help_text='Set to enable comments on post')
    
    class Meta:
        get_latest_by = 'post_date'
        ordering = ['-post_date']
    
    def get_workshop(self):
        return self.workshop_set.get()
    workshop = property(get_workshop)

    def make_sure_workshop_exists(self):
        # basically a gradual update measure - posts that are on a blog that is a workshop
        # should always have a Workshop instance pointing at them, but it didn't use to be that way.
        if self.blog.is_workshop() and self.workshop_set.count() == 0:
            from workshop.models import Workshop
            self.workshop_set.add(Workshop.create_workshop_by_post(self))
            self.save()

    # TODO - is there a simpler way to do this is_X stuff? some magic of meta classes? my
    # oppurtunity?? nah.
    def is_workshop(self):
        return self.post_style == self.POST_STYLE_WORKSHOP

    def is_gallery(self):
        return self.post_style == self.POST_STYLE_GALLERY

    def is_article(self):
        return self.post_style == self.POST_STYLE_ARTICLE

    def get_absolute_url(self):
      d = self.post_date
      return u'/branches/posts/%d/' % ( self.id )
      
    def get_absolute_edit_url(self):
      # TODO: is there a better way to keep this in sync? maybe just have the editBlog
      # a constant in the desk.views model?
      d = self.post_date
      return u'/desk/editPost/%d/' % ( self.id )
      
    def get_absolute_preview_url( self ):
      d = self.post_date
      return u'/branches/preview_post/%d/' % ( self.id )
    
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
        
        import datetime
        self.time_modified        = datetime.date.today()
        self.rendered_text        = wikiSub(self.text)
        self.teaser_rendered_text = wikiSub(self.teaser_text)
        super(Post, self).save() # Call the "real" save() method.

class PostImage(models.Model):
    post          = models.ForeignKey(Post)
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
            # new PostImage
            if self.caption is None: self.caption= ''
            if self.label is None: self.label=''
            if( len(self.caption) == 0 ):
                self.caption = self.label[0:25]
                
        super( PostImage, self ).save()
   
class Subject(models.Model):
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
  
  flags         = models.ManyToManyField(Flag,verbose_name='flags to include', blank=True, null=True)
  blogs         = models.ManyToManyField(Blog, help_text="currently not in use", verbose_name='blogs to include', blank=True, null=True)
   
  def get_absolute_url( self ):
      return u'/subjects/%s/' % self.slug
    
  def __unicode__(self):
        return self.name
  
  class Meta:
    ordering = ['ordering']

# This model doesn't need to be here. It is meant to be a general way to do the following flow:
# site does something -> sends email -> user does something
# the user something should be connected to the original. So we use a hash - it is not easy to guess,
# and allows us to determine the 'thread' of thought. should actually add something deterministic too
# to prevent conflicts, but as long as the hash is long enough it won't happen ;)
class HashPoint(models.Model):
  """
  Allows continueing from a point in the process through user interaction by email (or anything)
  you use with the new method:
  new(data)
  you make sure you give the user by email the correct url, you do the parsing and get back your data
  from the hash.
  The data can be whatever you want - use cPickle or json or whatever.
  """
  hash          = models.CharField(max_length=256, blank=False)
  data          = models.TextField(blank=False)
  comment       = models.TextField(blank=True) # helps, not required
  @classmethod
  def new(clazz, data, comment = ''):
        hash = make_random_hash()
        hp = HashPoint(hash=hash, data=data, comment=comment)
        hp.save()
        return hash

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
        hide_hash = HashPoint.new(data=str(comment.id), comment='hide_comment')
        post = content_object # same thing
        if self.really_send_email_to_this_person is None:
            recipient_list = [post.author.email]
        else:
            recipient_list = [self.really_send_email_to_this_person]
        site = Site.objects.get_current().name
        from spamdetector.models import AllowedBanRequests
        AllowedBanRequests(ip_address = comment.ip_address, hash=self._hash).save()
        c = Context({ 'comment': comment,
                      'content_object': content_object,
                      'site': site,
                      'ban_hash': self._hash,
                      'hide_hash': hide_hash})
        subject = u'[%s] New comment posted on "%s"' % (site, content_object)
        send_email_to(template='cityblog/post_comment_notification_email.txt',
                to=recipient_list, subject=subject, context_dict=c,
                fail_silently=True)
        
# This is annoying - but for some reason this file gets loaded
# more then once - so I'm forced to catch the AlreadyModerated
# exception, lest django present the dreaded error page.
try:
    i = 0
    moderator.register(Post, PostModerator)
except AlreadyModerated:
    i += 1
    print "already moderated: %s" % i

