from django.db import models
import os
from django.core import validators

class Category(models.Model):
    category_name = models.CharField(_('name'), maxlength=50)
    parent = models.ForeignKey('self', verbose_name=_('parent'), blank=True, null=True, related_name='child')

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    #
    class Admin:
        list_display = ('category_name', '__str__')
        search_fields = ['category_name']
    #

    def __str__(self):
        if self.parent:
            return '%s :: %s' % (self.parent, self.category_name)
        else:
            return self.category_name
    #
    
    def get_parents(self):
        """ return list of parent objects """
        if not self.parent: return []
        return [self.parent] + self.parent.get_parents()
    #

    def _get_parent_ids(self):
        """ return list of parent objects """
        if self.parent is None: return []
        return [self.parent.id] + self.parent.get_parent_ids()
    #

    def validate(self):
        errdict = super(Category, self).validate()
        lst = self._get_parent_ids()
        if self.id in lst:
            if 'parent' in errdict:
                errdict['parent'].append(_("You must not save a category in itself!"))
            else:
                errdict['parent']= [_("You must not save a category in itself!")]
        #
        return errdict
    #
#

class Country(models.Model):
    """ Country info """
    code = models.CharField(_('country code'), maxlength=5, unique=True)
    name = models.CharField(_('name'), maxlength=255, unique=True)
    phone = models.CharField(_('phone prefix'), maxlength=10, blank=True, null=True)
    flag = models.ImageField(_('flag'), upload_to=os.path.join('img', 'flags'), blank=True)
    
    def __str__(self):
        return self.name
    #
    
    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
    #

    class Admin:
        list_display = ('code', 'name', 'phone')
    #
#

class City(models.Model):
    """ City info """
    name = models.CharField(maxlength=250, core=True)
    call_prefix = models.CharField(_('call prefix'), maxlength=10, blank=True)
    post_prefix = models.CharField(_('post prefix'), maxlength=20, blank=True)
    country = models.ForeignKey(Country, edit_inline=models.TABULAR)

    def __str__(self):
        return '%s -- %s' % (self.name, self.country.code)
    #
    
    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        ordering = ['name']
        unique_together = (('country', 'name'),)
    #
    
    class Admin:
       list_display = ('name', 'country', 'call_prefix', 'post_prefix')
       list_filter = ('country',)
       fields = (
                 (None, {'fields': ('country', 'name')}), 
                 (_('PTT'), {'fields': ('call_prefix', 'post_prefix')}), 
       )
    #
#

class Contact(models.Model):
    """ Contact info """
    contact_name = models.CharField(_('name'), maxlength=255, blank=True,
                           validator_list=[validators.RequiredIfOtherFieldNotGiven('company')])
    company = models.CharField(_('company'), maxlength=255, blank=True,
                              validator_list=[validators.RequiredIfOtherFieldNotGiven('contact_name')])
    # TODO: validate country against city
    country = models.ForeignKey(Country)
    # TODO: validate city against country
    city = models.ForeignKey(City)
    address = models.TextField(_('address'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    category = models.ForeignKey(Category, blank=True, null=True)

    def _get_name(self):
        if self.contact_name:
            return self.contact_name
        else:
            return self.company
    #
    name = property(fget=_get_name)

    def __str__(self):
        if self.company and self.contact_name:
            return '%s -- %s' % (self.company, self.name)
        else:
            return self.name
    #
    
    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
    #

    class Admin:
        list_display = ('name', 'category', 'city', 'address')
        list_filter = ('category','country', 'city')
        fields = (
           (None, {'fields': ('contact_name', 'company', 'category')}),
           (_('Address'), {'fields': (('country', 'city'), 'address',)}),
           (None, {'fields': ('notes',),}),
        )
    #
#

class ContactType(models.Model):
    name = models.CharField(_('name'), maxlength=255)
    
    class Meta:
        verbose_name = _('contact type')
        verbose_name_plural = _('contact types')
    #

    class Admin:
        list_display=('name',)
    #
    
    def __str__(self):
        return self.name
    #
#

class ContactDetail(models.Model):
    contact = models.ForeignKey(Contact, edit_inline=models.TABULAR)
    contact_type = models.ForeignKey(ContactType, core=True, blank=True, null=True)
    data = models.CharField(_('data'), maxlength=255)
    note = models.CharField(_('note'), maxlength=255)
#
