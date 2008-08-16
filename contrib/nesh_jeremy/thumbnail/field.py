from django.db.models.fields.files import ImageField
from utils import make_thumbnail, _remove_thumbnails, remove_model_thumbnails, rename_by_field
from django.dispatch import dispatcher, Signal
from django.db.models import signals

def _delete(instance=None, **kw):
    if instance:
        print '[thumbnail] DELETE', instance
        remove_model_thumbnails(instance)
#

class ImageWithThumbnailField(ImageField):
    """ ImageField with thumbnail support
    
        auto_rename: if it is set perform auto rename to
        <class name>-<field name>-<object pk>.<ext>
        on pre_save.
    """

    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, auto_rename=True, mask_file='', logo_file='',**kwargs):
        self.width_field, self.height_field = width_field, height_field
        super(ImageWithThumbnailField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)
        self.auto_rename = auto_rename
        self.mask_file   = mask_file
        self.logo_file   = logo_file
    #
    
    def _pre_save(self, instance=None, **kw):
        # since this is called by the pre_save signal, the pk can be unset.
        self.needs_renaming= False
        if not self.auto_rename: return
        if instance == None: return
        image = getattr(instance, self.attname)
        if instance._get_pk_val() is None:
            if image == '':
                return
            else:
                # TODO: should have primary key at this point.
                return
        # XXX this needs testing, maybe it can generate too long image names (max is 100)
        image = rename_by_field(image, '%s-%s-%s' \
                                     % (instance.__class__.__name__,
                                         self.name,
                                         instance._get_pk_val()
                                        ), mask_image=self.mask_file, logo_image=self.logo_file
                                   )
        setattr(instance, self.attname, image)
    #
    
    def contribute_to_class(self, cls, name):
        super(ImageWithThumbnailField, self).contribute_to_class(cls, name)
        signals.post_delete.connect(_delete, sender=cls)
        signals.pre_save.connect(self._pre_save, sender=cls)
    #

    def get_internal_type(self):
        return 'ImageField'
    #
#
