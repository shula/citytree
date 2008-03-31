# vim: set fileencoding=utf-8 :
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings 
from nesh.thumbnail.field import ImageWithThumbnailField
import datetime
from citytree.utils.textUtils import wikiSub


#Object representing a blog, a blog can have many authors.
class blog(models.Model):
    name          = models.CharField(maxlength=200,blank=False)
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
    header_image_label    = models.CharField(maxlength=255,blank=True)
    
    teaser_photo          = ImageWithThumbnailField('Image to display along with teaser', 
                                                     upload_to='blog_teaser_images/%Y/%m/%d',
                                                     width_field='teaser_image_width', 
                                                     height_field='teaser_image_height', 
                                                     blank=True, null=True)
    teaser_image_width    = models.PositiveIntegerField(blank=True,null=True)
    teaser_image_height   = models.PositiveIntegerField(blank=True,null=True)
    teaser_photo_label    = models.TextField(blank=True, null=True) 
    teaser_text           = models.TextField(blank=True, null=True)
    teaser_photo_caption  = models.CharField("Label for teaser photo", maxlength=200,blank=True, null=True)
    
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
    name         = models.CharField(maxlength=50)
    
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
      
    POST_STYLE_TYPES = (
        ( 1, 'עלה קטן' ),
        ( 2, 'מאמר' ),
        ( 3, 'גלריה' ),
    )
    

    blog          = models.ForeignKey(blog)
    author        = models.ForeignKey(User, blank=False)
    
    #slug          = models.SlugField('blog url identifier', unique=True)
    
    #User editable date for when the post should be shown as being modified
    post_date     = models.DateTimeField(blank=False)
    
    #Hidden field so that you can see when the post was really last changed
    time_modified = models.DateTimeField('Time Of Last Edit', auto_now=True)
    
    title         = models.CharField('Post Title', maxlength=200,blank=False)
    
    image         = ImageWithThumbnailField(upload_to='blog_images/%Y/%m/%d',width_field='image_width', height_field='image_height', blank=True)
    image_label   = models.TextField('Text Displayed as you hover over the image',
                                                blank=True, null=True)
    image_caption = models.CharField('post image Caption -', 
                                     help_text='If left blank then contents of image label are copied here', maxlength=200,blank=True, null=True)
    image_height  = models.PositiveIntegerField(blank=True,null=True)
    image_width   = models.PositiveIntegerField(blank=True,null=True)
    
    teaser_text          = models.TextField(blank=False, null=True)
    teaser_rendered_text = models.TextField(blank=True, null=True)
    
    text          = models.TextField(help_text="If left blank then Text is copied here", blank=True, null=True)
    rendered_text = models.TextField('Entry body as HTML', blank=True, null=True)
    
    flags         = models.ManyToManyField( flag, blank=True, null=True )
    draft         = models.BooleanField(help_text='Set to post to make post live on site', default=1, choices=DRAFT_CHOICES, blank=False)
    post_style    = models.PositiveIntegerField('Post Style', help_text='Style in which post is displayed' , blank=False, default=1, choices=POST_STYLE_TYPES )
    
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
        return self.post_style == 3 # TODO - how to make this a constant automatically, djangoly?

    def get_absolute_url(self):
      d = self.post_date
      return '/blogs/posts/%d/' % ( self.id )
      
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
    caption       = models.CharField(help_text="Title of image, displayed in html", maxlength=200,blank=True, null=True)
    
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
  name          = models.CharField(maxlength=200,blank=False)
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
