# -*- coding: utf-8 -*-
# pylint: disable-msg=R0903, W0232, E1101

from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from nesh.thumbnail.field import ImageWithThumbnailField
from nesh.utils.markup import MARKUP_FILTERS, MARKUP_TEXTILE, render_content
import os

IMG_ROOT = os.path.join('img', 'news')

class NewsImage(models.Model):
    """ news images """
    
    slug = models.SlugField(_('image name'), unique=True, core=True)
    # FIXME: validate max width|height for images
    image = ImageWithThumbnailField(_("image"), upload_to=os.path.join(IMG_ROOT))

    class Meta:
        verbose_name = _('news image')
        verbose_name_plural = _('news images')
        ordering = ('slug',)
    #
    
    class Admin:
        list_display = ('slug', 'image')
        search_fields = ('slug',)
    #
    
    def __str__(self):
        return self.slug

class EntryManager(models.Manager):
    def get_news(self, max_entries=10):
        lang = get_language()
        ret = cache.get('NEWS_%d_%s' % (max_entries, lang), None)
        if ret is None:
            ret = list(self.filter((
                    Q(is_published__exact=True)
                    & Q(pub_date__lte=datetime.now())
                    & (Q(expiry_date__isnull=True) | Q(expiry_date__gt=datetime.now()))
                    & Q(language__exact=lang)
                    ))[:max_entries])
            cache.set('NEWS_%d_%s' % (max_entries, lang), ret, 60) # 60s
        return ret
    
    def published(self):
        return self.filter(Q(is_published__exact=True) & Q(language__exact=get_language()))

class Entry(models.Model):
    """ make compound index on:
    
        * is_published, pub_date, expiry_date, language
        * pub_date, slug
    """
    
    site = models.ForeignKey(Site,
                             default=settings.SITE_ID)
    language = models.CharField(_('language'),
                                maxlength=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    is_published = models.BooleanField(_('published'),
                                       default=True,
                                       db_index=True)
    pub_date = models.DateTimeField(_('publication start'),
                                    help_text=_('News will start to show after this date.'),
                                    default=models.LazyDate())
    expiry_date = models.DateTimeField(_('publication end'),
                                       help_text=_('News will stop showing after this date.'),
                                       blank=True, null=True)
    slug = models.SlugField(_('slug'),
                            unique_for_date='pub_date',
                            prepopulate_from=['headline'])

    headline = models.CharField(_('headline'), maxlength=255)
    
    # TEXT
    text_type = models.PositiveSmallIntegerField(_('content type'),
                                                 choices=MARKUP_FILTERS,
                                                 default=MARKUP_TEXTILE)
    raw_summary = models.TextField(_('summary'),
                                   help_text=_('News summary'))
    rendered_summary = models.TextField(_('rendered symmary content'),
                                        editable=False,
                                        blank=True)
    raw_body = models.TextField(_('body'),
                                blank=True,
                                help_text=_('Full version of the news. If not given summary will be used. Use {{ image image_name }} to insert images')
                                )
    rendered_body = models.TextField(_('rendered body content'),
                                     editable=False,
                                     blank=True)

    images = models.ManyToManyField(NewsImage, filter_interface=models.HORIZONTAL, blank=True, null=True)
    keywords = models.CharField(_('keywords'),
                                maxlength=200,
                                blank=True,
                                help_text=_('Keywords for search engines')
                                )

    objects = EntryManager()

    class Meta:
        verbose_name = _('news entry')
        verbose_name_plural = _('news entries')

        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    class Admin:
        search_fields = ('headline', 'raw_summary', 'raw_body')
        save_as = True
        date_hierarchy = 'pub_date'
        fields = (
                    (None, {'fields': (('site', 'is_published',), 'language', 'headline', 'slug',)}),
                    (_('Date/Time'), {'fields': ('pub_date', 'expiry_date'), 'classes': 'collapse',}),
                    (_('Text'), {'fields': ('keywords', 'text_type', 'raw_summary', 'raw_body', 'images')}),
                 )
        list_filter = ('site', 'is_published', 'language',)
        list_display = ('headline', 'site', 'is_published', 'language', 'pub_date', 'expiry_date')

    def save(self):
        if not self.id:
            # I'm using self.images (M2M) so I must have valid ID!
            super(Entry, self).save()

        self.rendered_body = render_content(self.raw_body, self.text_type, self.images)
        # summary can't have images
        self.rendered_summary = render_content(self.raw_summary, self.text_type)

        super(Entry, self).save()

    def body(self):
        return self.rendered_body

    def summary(self):
        return self.rendered_summary

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        return "/news/%s/%s/" % (self.pub_date.strftime("%Y/%m/%d").lower(), self.slug)