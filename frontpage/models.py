# -*- coding:utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.db import models
from nesh.thumbnail.field import ImageWithThumbnailField
from django.conf import settings 

DRAFT_CHOICES = (
  ( 1, '×××××'),
  ( 0, '××××©×¨') )
  
class Teaser( models.Model ):
    image          = ImageWithThumbnailField('Teaser Image', blank=True,upload_to='frontpage_images/%Y/%m/%d',width_field='image_width', height_field='image_height')
    image_width    = models.PositiveIntegerField(blank=True,null=True)
    image_height   = models.PositiveIntegerField(blank=True,null=True)
    url            = models.CharField('URL To Link To', max_length=255,blank=True)
    label          = models.CharField('Teaser Label', max_length=255,blank=True)
    title          = models.CharField('Teaser Title', max_length=255,blank=True)
    teaserText     = models.TextField('Teaser Text', blank=True)
    
    def __unicode__( self ):
        return self.title
    
    class Admin:
       fields = (
            (None, {'fields': ('image',
            'url',
            'label',
            'title',
            'teaserText'
            )}),
           )
    
class FrontpageHeaderImage( models.Model ):
    image          = ImageWithThumbnailField(blank=True,upload_to='frontpage_images/%Y/%m/%d',
                                width_field='image_width', height_field='image_height',
                                mask_file=settings.HEADER_MASK, logo_file=settings.SITE_LOGO, 
                                help_text='<b>MUST BE</b>: 808x160!')
    image_width    = models.PositiveIntegerField(blank=True,null=True)
    image_height   = models.PositiveIntegerField(blank=True,null=True)
    image_label    = models.CharField(max_length=255,blank=True,null=True)
    
    def __unicode__( self ):
        return self.image_label
    
    class Admin:
         fields = (
                (None, {'fields': ('image',
                'image_label'
                )}),
               )
    

class FrontPage(models.Model):
      
    title                 = models.CharField(max_length=255,blank=False, help_text='Title text at top of page - Required' )
    main_text             = models.TextField( blank=True, null=True, help_text='No wiki formatting - just use plain HTML' )
    
    date                  = models.DateTimeField( blank=False, help_text='Required' )
    
    draft                 = models.BooleanField(blank=False,help_text='Uncheck to make this live on site', default=1, choices=DRAFT_CHOICES)
    
    headerImage           = models.ForeignKey(FrontpageHeaderImage, blank=False, help_text='Required')
    
    teaser1               = models.ForeignKey(Teaser, blank=True, null=True, related_name='teaser1_set')
    teaser2               = models.ForeignKey(Teaser, blank=True, null=True, related_name='teaser2_set')
    teaser3               = models.ForeignKey(Teaser, blank=True, null=True, related_name='teaser3_set')
    teaser4               = models.ForeignKey(Teaser, blank=True, null=True, related_name='teaser4_set')
    teaser5               = models.ForeignKey(Teaser, blank=True, null=True, related_name='teaser5_set')
    
    def get_absolute_url(self):
      return '/frontpage/preview/%s/' % self.id
    
    def __unicode__(self):
      return self.title
    
    class Admin:
      fields = (
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
    
    class Meta:
        get_latest_by = 'date'
        
# Create your models here.
