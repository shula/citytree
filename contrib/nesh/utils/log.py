from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

ACTION_MAP = {
              ADDITION: _('The %(name)s "%(obj)s" was added successfully.'),
              CHANGE: _('The %(name)s "%(obj)s" was changed successfully.'),
              DELETION: _('The %(name)s "%(obj)s" was deleted successfully.'),
              }

def db_log(request, obj, action, add_msg=True):
    """ log into django log """
    opts = obj._meta
    LogEntry.objects.log_action(request.user.id,
                                ContentType.objects.get_for_model(obj).id,
                                obj._get_pk_val(), str(obj),
                                action)
    if add_msg:
        msg = ACTION_MAP[action] % {'name': opts.verbose_name, 'obj': obj}
        request.user.message_set.create(message=msg)
