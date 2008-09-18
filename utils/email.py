import re

from django.core.mail import send_mail
from django.template import Context, loader

from  settings import DEFAULT_FROM_EMAIL

email_re = re.compile(r"^([\w at .=/_-]+)@([\w-]+)(\.[\w-]+)*$")

def check_email(email):
    """ TODO: replace with django equivalent code (must be)
    """
    return email_re.match(email)


def send_email_to(template, to, subject, context_dict, fail_silently=True):
    recipient_list = [to]
    t = loader.get_template(template)
    c = Context(context_dict)
    message = t.render(c)
    # can't have eol chars in subject
    subject = subject.strip().replace('\n', '. ')
    send_mail(subject, message, DEFAULT_FROM_EMAIL, recipient_list, fail_silently=fail_silently)

