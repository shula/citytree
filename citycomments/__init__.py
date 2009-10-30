# we patched django a bit, so now the already existing
# get_comment_app points here, 

from django.core import urlresolvers

def get_model():
    import models
    return models.CityComment

def get_form():
    import forms
    return forms.CityCommentForm

def get_form_target():
    #import django.contrib.comments as comments
    #return comments.get_form_target()
    return urlresolvers.reverse("django.contrib.comments.views.comments.post_comment")

