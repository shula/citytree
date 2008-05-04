from django.db import models
from django.utils.translation import gettext_lazy as _

class CounterManager(models.Manager):
    # FIXME: make atomic
    def inc(self, name):
        """ increment counter.
            create new counter if needed.
        """
        try:
            obj = self.get(name=name)
            obj.val += 1
        except Counter.DoesNotExist:
            # create new
            obj = Counter(name=name, val=1)
        # XXX trap duplicate exception?
        obj.save()

    def get_next(self, name):
        """ get next value for the counter and increment it.
            create new counter if needed.
        """
        try:
            obj = self.get(name=name)
            obj.val += 1
        except Counter.DoesNotExist:
            # create new
            obj = Counter(name=name, val=1)
        # XXX trap duplicate exception?
        obj.save()
        return obj.val
    #
    
    def peek_next(self, name):
        """ get and/or create next value for the counter without incrementing it """
        try:
            obj = self.get(name=name)
        except Counter.DoesNotExist:
            obj = Counter(name=name, val=1)
            obj.save()
        return obj.val
    #
    
    # FIXME: make atomic
    def set(self, name, val):
        """ set counter value """
        try:
            obj = self.get(name=name)
            obj.val = val
        except Counter.DoesNotExist:
            # create new
            obj = Counter(name=name, val=val)
        obj.save()
    #
#

class Counter(models.Model):
    """ simple models for storing various counters
        use only manager functions for getting values
    """
    
    objects = CounterManager()
    
    name = models.CharField(_('name'), maxlength=50, unique=True)
    val = models.IntegerField(_('value'))
    
    class Meta:
        ordering = ['name']
        verbose_name = _('counter')
        verbose_name_plural = _('counters')
    #
    class Admin:
        list_display = ('name', 'val',)
    #
    
    def __str__(self):
        return '%s: %d' % (self.name, self.val)
    #
#