# -*- coding: utf-8 -*-

import re
import time
import datetime

from django import forms
from django.forms.util import ErrorDict
from django.conf import settings
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.text import get_text_list
from django.utils.translation import ngettext
from django.utils.translation import ugettext_lazy as _

from django.contrib.comments.models import Comment
from django.contrib.comments.forms import CommentForm, COMMENT_MAX_LENGTH

from utils.models import create_from_existing_base

from models import CityComment


class CityCommentForm(CommentForm):
    name          = forms.CharField(label="שם", max_length=50)
    email         = forms.EmailField(label="כתובת דואר אלקטרוני")
    url           = forms.URLField(label="URL", required=False)
    phone         = forms.CharField(label="מספר טלפון", required=False)
    comment       = forms.CharField(label='הערה', widget=forms.Textarea,
                                    max_length=COMMENT_MAX_LENGTH)
    honeypot      = forms.CharField(required=False,
                                    label='אל תמלאו כאן שום דבר, או שהמערכת'\
                                            'תזרוק את ההודעה הזו כספאם!')
    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_pk     = forms.CharField(widget=forms.HiddenInput)
    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None):
        super(CityCommentForm, self).__init__(target_object, data, initial)

    def get_comment_object(self):
        """
        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        new_comment = super(CityCommentForm, self).get_comment_object()

        new = create_from_existing_base(base_class=Comment,
                inheritor_class=CityComment, obj=new_comment)
        new.phone = self.cleaned_data["phone"]

        return new

    def example_clean_phone(self):
        phone = self.cleaned_data['phone']
        if self.cleaned_data['phone'] == '':
            raise forms.ValidationError('בבקשה מלאו מספר טלפון שנוכל לחזור אליכם. המספר לא יופיע באתר')
        return phone
