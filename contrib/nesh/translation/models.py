""" models for translation """
# pylint: disable-msg=W0232, R0903, R0904

# stdlib
import sha
# django
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import signals
from django.dispatch import dispatcher
from django.utils.translation import get_language, gettext
from django.utils.translation import gettext_lazy as _

# ========================================================================
# INIT
# ========================================================================

try:
    # requires python Levenshtein module
    # <http://trific.ath.cx/resources/python/levenshtein/>
    from Levenshtein import ratio
except ImportError:
    # use difflib std instead
    from difflib import SequenceMatcher
    def ratio(string1, string2):
        """ simulate Levenshtein function """
        return SequenceMatcher(lambda x: x == " ", string1, string2).ratio()

CHOICES = []
def _setup():
    """ tmp """
    for code, name in settings.LANGUAGES:
        if settings.LANGUAGE_CODE != code:
            CHOICES.append((code, name))

_setup()
del _setup
if not len(CHOICES):
    # this is a error -- why using translations with only default language?
    CHOICES.append((settings.LANGUAGE_CODE, _('default')))

def message_digest(message):
    """ calculate message digest """
    return sha.new(message.strip()).hexdigest()

# ========================================================================
# MODELS
# ========================================================================

# TODO: cache database access

class MessageManager(models.Manager):
    """ additional message model functionality """
    
    def get_or_create_message(self, message):
        """ return message object for message, create if nessesary """
        
        digest = message_digest(message)
        try:
            return self.get(digest=digest)
        except self.model.DoesNotExist:
            # create message
            msg = self.model(message=message)
            msg.save()
            return msg

    def get_untranslated_for(self, message):
        """ return a list of all languages for which this message is not translated """
        languages = [x[0] for x in settings.LANGUAGES if x[0] != settings.LANGUAGE_CODE]

        message_obj = self.get_or_create_message(message)
        langs = [trans.language for trans in message_obj.translation_set.all()]

        ret = []
        for l in languages:
            if l not in langs:
                ret.append(l)
        return ret
    
    def gettext(self, message):
        """ get translation for the message  """
        
        # empty message
        if not message:
            return message
        
        lang = get_language()
        # messages for the default language are in original object
        if lang == settings.LANGUAGE_CODE:
            return message

        digest = message_digest(message)
        
        # get message
        try:
            message_obj = self.get(digest=digest)
        except self.model.DoesNotExist:
            # register message
            message_obj = self.model(digest=digest, message=message)
            message_obj.save()

        # get translation
        try:
            message = message_obj.translation_set.get(language=lang).translation
        except Translation.DoesNotExist: #IGNORE:E1101 -- django generated
            msg = gettext(message)
            # gettext has translation, use it and save into db
            if msg != message:
                tr = Translation(message=message_obj, language=lang, translation=msg)
                message_obj.translation_set.add(tr)
                message_obj.save() # XXX do I have to save here?
            return msg
        return message

    def similar(self, message, min_ratio=50):
        """ find similar messages """
        
        fuzzy = []
        digest = message_digest(message)
        
        for msg in self.exclude(digest=digest):
            rat = ratio(message, msg.message) * 100
            if rat > min_ratio:
                fuzzy.append((rat, msg))

        fuzzy.sort()
        return fuzzy

class Message(models.Model):
    """ main message catalog """

    digest = models.CharField(_('message digest'), maxlength=40, unique=True, 
                              editable=False, # generated on SAVE
                              blank=True
                              )
    message = models.TextField(_('original message'))
    objects = MessageManager()

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    class Admin:
        ordering = ('message',)
        list_display = ('message', 'digest')
        search_fields = ('message',)

    def __str__(self):
        if len(self.message) > 30:
            return self.message[:30] + '[...]'
        else:
            return self.message

    def save(self):
        """ cleanup message, calc digest """
        self.message = self.message.strip()
        self.digest = message_digest(self.message)
        super(Message, self).save()

class Translation(models.Model):
    """ translation catalog """

    message = models.ForeignKey(Message, edit_inline=models.TABULAR)
    language = models.CharField(_('language'), maxlength=10, choices=CHOICES)
    translation = models.TextField(_('translation'), core=True)

    class Meta:
        verbose_name = _('message translation')
        verbose_name_plural = _('message translations')
        unique_together = (('message', 'language',),)

    class Admin:
        ordering = ('language',)
        list_display = ('message', 'language', 'translation')
        list_filter = ('language', 'message',)
        search_fields = ('translation',), 

    def __str__(self):
        if len(self.translation) > 30:
            return '[%s] %s [...]' % (self.get_language_display(), #IGNORE:E1101 -- django generated
                                      self.translation[:30])
        else:
            return '[%s] %s' % (self.get_language_display(), self.translation) #IGNORE:E1101 -- django generated

    def save(self):
        self.translation = self.translation.strip()
        super(Translation, self).save()

class RegistryManager(models.Manager):
    @staticmethod
    def _get_for_model(model):
        """ like ContentTypeManager method, but do not create new ContentType """
        opts = model._meta
        return ContentType._default_manager.get(app_label=opts.app_label, model=opts.object_name.lower()) #IGNORE:E1101 -- django generated

    def unregister(self, obj, field):
        pk = str(obj._get_pk_val())
        try:
            ct = self.__class__._get_for_model(obj)
            reg = self.get(content=ct.id, object_id=pk, field=field)
            reg.delete()
        except self.model.DoesNotExist, err:
            if settings.DEBUG:
                import warnings
                warnings.warn('unregister, unknown object unregistered (%s)' % err, stacklevel=2)
        except ContentType.DoesNotExist, err: #IGNORE:E1101 -- django generated
            if settings.DEBUG:
                import warnings
                warnings.warn('unregister, unknown content type unregistered (%s)' % err, stacklevel=2)

    def register(self, obj, field):
        """ register message into registry, create message if nessesary """
        data = getattr(obj, field)
        pk = str(obj._get_pk_val())
        
        if not data: return # don't register empty data
        
        # this can raise exception because if no ContentType is found there is BUG somewhere
        ct = self.__class__._get_for_model(obj)
        
        try:
            reg = self.get(content=ct.id, object_id=pk, field=field)
            if reg.message.digest != message_digest(data):
                # message is changed!
                msg = Message.objects.get_or_create_message(data)
                reg.delete() # delete old
                reg = Registry(content=ct, object_id=pk, field=field)
                msg.registry_set.add(reg) # add new
        except self.model.DoesNotExist:
            msg = Message.objects.get_or_create_message(data)
            reg = Registry(content=ct, object_id=pk, field=field)
            msg.registry_set.add(reg)

class Registry(models.Model):
    """ register who uses what message """
    
    objects = RegistryManager()
    
    message = models.ForeignKey(Message, edit_inline=True)
    content = models.ForeignKey(ContentType, core=True)
    # NOTE: I GUESS that no model have primary key longer than 255 characters
    #       and I can't use IntegerField, because models can have other
    #       types for the primary key
    # XXX: store object_id in TextField?? Probably backward incompatible.
    object_id = models.CharField(_('object'), maxlength=255)
    field = models.CharField(_('field'), maxlength=50)
    
    class Meta:
        verbose_name = _('registry')
        verbose_name_plural = _('registries')
        unique_together = (('message', 'content', 'object_id', 'field'),)

    class Admin:
        pass
    
    def object(self):
        """ get coresponding object """
        
        return self.content.get_object_for_this_type(pk=self.object_id) #IGNORE:E1101 -- django generated

    def field_value(self):
        """ get coresponding field value """
        
        return getattr(self.object(), self.field)

    def __str__(self):
        return '%s.%s: %s' % (self.object(), self.field, self.message)

# ========================================================================
# Fields
# ========================================================================

class I18NCharField(models.CharField):
    """ same as CharField, just update Message catalog on save/delete """
    
    def get_internal_type(self):
        return 'CharField'

    def _i18n_delete(self, instance=None):
        if instance == None: return # this can never happen
        Registry.objects.unregister(instance, self.name)

    def _i18n_save(self, instance=None):
        if instance == None: return # this can never happen
        Registry.objects.register(instance, self.name)

    def contribute_to_class(self, cls, name):
        super(self.__class__, self).contribute_to_class(cls, name)
        dispatcher.connect(self._i18n_delete, signals.pre_delete, sender=cls)
        dispatcher.connect(self._i18n_save, signals.post_save, sender=cls)

class I18NTextField(models.TextField):
    """ same as TextField, just update Message catalog on save/delete """
    
    def get_internal_type(self):
        return 'TextField'

    def _i18n_delete(self, instance=None):
        if instance == None: return # this can never happen
        Registry.objects.unregister(instance, self.name)

    def _i18n_save(self, instance=None):
        if instance == None: return # this can never happen
        Registry.objects.register(instance, self.name)

    def contribute_to_class(self, cls, name):
        super(self.__class__, self).contribute_to_class(cls, name)
        dispatcher.connect(self._i18n_delete, signals.pre_delete, sender=cls)
        dispatcher.connect(self._i18n_save, signals.post_save, sender=cls)