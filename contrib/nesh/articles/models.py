# pylint: disable-msg=R0903, W0232, C0111
"""
$Id: models.py 99 2006-06-14 08:17:18Z nesh $

Article storage
"""

__revision__ = '$Rev: 34 $'

from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from nesh.thumbnail.field import ImageWithThumbnailField
from nesh.utils import url
from nesh.utils.markup import MARKUP_FILTERS, MARKUP_TEXTILE, render_content
import os
from django.core.cache import cache

ARTICLES_ROOT_URL = getattr(settings, 'ARTICLES_ROOT_URL', '/article/')
IMG_ROOT = os.path.join('img', 'articles')
C_KEY = 'CATEGORY_LIST_CACHE_%s'
A_KEY = 'ARTICLE_LIST_CACHE_%d_%s'


class ArticleImage(models.Model):
    """ article images """
    
    slug = models.SlugField(_('image name'), unique=True, core=True)
    # FIXME: validate max width|height for images
    image = ImageWithThumbnailField(_("image"), upload_to=os.path.join(IMG_ROOT))

    class Meta:
        verbose_name = _('article image')
        verbose_name_plural = _('article images')
        ordering = ('slug',)

    class Admin:
        list_display = ('slug', 'image')
        search_fields = ('slug',)

    def __str__(self):
        return self.slug

class ArticleCategoryManager(models.Manager):
    def make_list(self, root=None):
        """ create list of list's with appropriate categories and articles (recursive) """

        lst = cache.get(C_KEY % get_language())
        
        if lst is not None:
            return lst
        else:
            lst = []

        if root is None:
            for top in self.filter(parent__isnull=True, language=get_language(), in_menu=True):
                #if top.child.count() or top.article_set.count(): # has childs?
                lst.append((top.menu_tuple(), self.make_list(top)))
        else:
            for top in root.child.filter(language=get_language(), in_menu=True):
                #if top.child.count(): # has childs?
                lst.append((top.menu_tuple(), self.make_list(top)))

        cache.set(C_KEY % get_language(), lst, 60 * 60 * 60 * 24 * 365) # cache 1yr
        return lst

class ArticleCategory(models.Model):
    """ article categories """
    
    objects = ArticleCategoryManager()
    weight = models.IntegerField(_('category weight'), default=0, db_index=True)
    category_name = models.CharField(_('name'), maxlength=200, db_index=True)
    slug = models.SlugField(_('slug'), prepopulate_from=['category_name'])
    parent = models.ForeignKey('self', verbose_name=_('parent'), blank=True, null=True, related_name='child')
    language = models.CharField(_('language'), maxlength=10, choices=settings.LANGUAGES, default=get_language) #IGNORE:E1101
    in_menu = models.BooleanField(_('in menu'), default=True)

    # text
    text_type = models.PositiveSmallIntegerField(_('content type'), choices=MARKUP_FILTERS, default=MARKUP_TEXTILE)
    raw_content = models.TextField(_('content'), help_text=_('Use {{ image image_name }} to insert images'))
    rendered_content = models.TextField(_('rendered content'), editable=False, blank=True)
    images = models.ManyToManyField(ArticleImage, filter_interface=models.HORIZONTAL, blank=True, null=True)
    keywords = models.CharField(_('keywords'), maxlength=200, blank=True)

    class Meta:
        verbose_name = _('article category')
        verbose_name_plural = _('article categories')
        ordering = ('weight', 'category_name',)
        unique_together = (('parent', 'slug'),)

    class Admin:
        list_display = ('category_name', 'in_menu', 'weight', 'parent', 'text_type',)
        search_fields = ('category_name',)
        list_filter = ('in_menu', 'language', 'parent',)
        fields = (
                  (None, {'fields': ('language', ('category_name', 'parent'), ('weight', 'in_menu'),),}),
                  (_('Description'), {'fields': ('keywords', 'text_type', 'raw_content', 'images', )}),
                  (_('Misc'), {'fields': ('slug',), 'classes': 'collapse',}),
             )

    def save(self):
        if not self.id: #IGNORE:E1101
            # I'm using self.images (M2M) so I must have valid ID!
            super(ArticleCategory, self).save()
        self.rendered_content = render_content(self.raw_content, self.text_type, self.images)
        super(ArticleCategory, self).save()
        # refresh cache
        cache.delete(C_KEY % get_language())


    def delete(self):
        super(ArticleCategory, self).delete()
        cache.delete(C_KEY % get_language())

    def content(self):
        return self.rendered_content

    def title(self):
        return self.category_name

    def get_absolute_url(self):
        return url.urljoin(ARTICLES_ROOT_URL, 'show', self.slug)

    def menu_tuple(self):
        return self.get_absolute_url(), self.category_name

    def __str__(self):
        if self.parent:
            return '%s::%s' % (self.parent, self.category_name)
        else:
            return '[%s] %s' % (self.language, self.category_name)

    def get_parents(self):
        """ return list of parent objects """
        
        if not self.parent:
            return []
        return [self.parent] + self.parent.get_parents() #IGNORE:E1101

    def _get_parent_ids(self):
        """ return list of parent objects """
        if self.parent is None:
            return []
        return [self.parent.id] + self.parent._get_parent_ids() #IGNORE:E1101

class ArticleManager(models.Manager): #IGNORE:R0904
    def get_articles(self):
        return self.filter((
                models.Q(is_published=True, in_menu=True)
                & models.Q(pub_date__lte=datetime.now())
                & (models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gt=datetime.now()))
                & models.Q(language=get_language())
                ))

    def make_list(self, category):
        """ create list of articles"""

        lst = cache.get(A_KEY % (category.id, get_language()))
        
        if lst is not None:
            return lst
        else:
            lst = []

        flt = self.filter((
                models.Q(is_published=True, in_menu=True)
                & models.Q(pub_date__lte=datetime.now())
                & (models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gt=datetime.now()))
                & models.Q(language=get_language())
                & models.Q(category=category.id)
                ))
        for art in flt:
            t = art.menu_tuple()
            if len(t):
                lst.append(t)

        cache.set(A_KEY % (category.id, get_language()), lst, 60 * 60 * 60 * 24 * 365) # cache 1yr
        return lst

# TODO: prevent text_type changes!
# FIXME: validate language choice
class Article(models.Model):
    objects = ArticleManager()
    
    category = models.ForeignKey(ArticleCategory)
    language = models.CharField(_('language'), maxlength=10, choices=settings.LANGUAGES, default=get_language) #IGNORE:E1101
    title = models.CharField(_('title'), maxlength=200)
    slug = models.SlugField(_('slug'), prepopulate_from=['title'])
    in_menu = models.BooleanField(_('in menu'), default=True)
    
    # text
    text_type = models.PositiveSmallIntegerField(_('content type'), choices=MARKUP_FILTERS, default=MARKUP_TEXTILE)
    raw_content = models.TextField(_('content'), help_text=_('Use {{ image image_name }} to insert images'))
    rendered_content = models.TextField(_('rendered content'), editable=False, blank=True)
    images = models.ManyToManyField(ArticleImage, filter_interface=models.HORIZONTAL, blank=True, null=True)
    keywords = models.CharField(_('keywords'), maxlength=200, blank=True)
    
    sites = models.ManyToManyField(Site, filter_interface=models.HORIZONTAL)
    is_published = models.BooleanField(_('published'), default=True, db_index=True)
    pub_date = models.DateTimeField(_('publication start'), default=models.LazyDate())
    expiry_date = models.DateTimeField(_('publication end'), blank=True, null=True)
    weight = models.IntegerField(_('article weight'), default=0, db_index=True)

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ('weight', 'title',)
        unique_together = (('category', 'slug'),)
        order_with_respect_to = 'category'

    class Admin:
        date_hierarchy = 'pub_date'
        list_filter = ('is_published', 'in_menu', 'sites', 'language', 'category',)
        search_fields = ('title',)
        list_display = ('title', 'category', 'weight', 'in_menu', 'is_published', 'language', 'text_type', 'pub_date', 'expiry_date')
        fields = (
                  (None, {'fields': (('language', 'category'), ('title', 'is_published', 'in_menu'), 'weight'),}),
                  (_('Text'), {'fields': ('keywords', 'text_type', 'raw_content', 'images',)}),
                  (_('Date/Time'), {'fields': ('pub_date', 'expiry_date'), 'classes': 'collapse',}),
                  (_('Misc'), {'fields': ('slug', 'sites',), 'classes': 'collapse',}),
                  )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return url.urljoin(ARTICLES_ROOT_URL, 'art', 'show', self.slug)

    def menu_tuple(self):
        return self.get_absolute_url(), self.title

    def save(self):
        if not self.id: #IGNORE:E1101
            # I'm using self.images (M2M) so I must have valid ID!
            super(Article, self).save()
        self.rendered_content = render_content(self.raw_content, self.text_type, self.images)
        super(Article, self).save()
        # clear cache
        cache.delete(A_KEY % (self.category.id, get_language()))

    def delete(self):
        super(Article, self).delete()
        cache.delete(A_KEY % (self.category.id, get_language()))

    def content(self):
        return self.rendered_content