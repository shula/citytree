import re

from django.core.mail import send_mail
from django.template import Context, loader

from citymail.models import SentEmail
from settings import DEFAULT_FROM_EMAIL

email_re = re.compile(r"^([\w at .=/_-]+)@([\w-]+)(\.[\w-]+)*$")

def check_email(email):
    """ TODO: replace with django equivalent code (must be)
    """
    return email_re.match(email)

def send_email_to(template, to, subject, context_dict, fail_silently=True):
    if isinstance(to, str):
        recipient_list = [to]
    else:
        recipient_list = to
    del to
    t = loader.get_template(template)
    c = Context(context_dict)
    message = unicode(t.render(c))
    # can't have eol chars in subject
    subject = unicode(subject.strip().replace('\n', '. '))
    mail_from = DEFAULT_FROM_EMAIL
    for to in recipient_list:
        # TODO - store emails seperately from to, to make this more consise
        # for cases with multiple to's?
        sent_email_log = SentEmail(mail_to=to, mail_from=mail_from,
            mail_subject=subject, mail_contents=message)
    sent_email_log.save()
    send_mail(subject, message, mail_from, recipient_list, fail_silently=fail_silently)

