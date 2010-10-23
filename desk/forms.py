# -*- coding:utf-8 -*-

from django import forms

from cityblog.models import Post, Blog
from workshop.models import Workshop, WorkshopEvent

#----------------- Forms --------------------------

class PostForm(forms.ModelForm):
    #post_date = forms.DateField(widget = forms.widgets.SplitDateTimeWidget())
    class Meta:
        model = Post

# TODO: would be nicer to do a UniqueSlugField, but then we need to know
# which class we should 'uniquify' on, and what's the field name - that
# info is in the Meta class of the Form (almost), but we need some metaclass
# magic to get it?
class WorkshopSlugField(forms.SlugField):
    def clean(self, value):
        this_slug_workshops = Workshop.objects.filter(slug=value)
        if this_slug_workshops.count() > 0:
            if this_slug_workshops[0] != self.form.instance.workshop:
                p = Post.objects.get(workshop__slug=value)
                raise forms.ValidationError('The slug field already exists in post <a href="%s">%s</a> (<a href="%s">edit</a>)' % (p.get_absolute_url(), p.title, p.get_absolute_edit_url()))
        return super(forms.SlugField, self).clean(value)

class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'image', 'image_label', 'image_caption', 'text', 'draft', 'enable_comments')

    # post stuff
    title         = forms.CharField(max_length=200)
    
    # Workshop stuff
    name        = forms.CharField()
    slug        = WorkshopSlugField()
    description = forms.CharField()

    # post stuff
    image         = forms.ImageField(required=False)
    image_label   = forms.CharField(widget=forms.widgets.Textarea, required=False)
    image_caption = forms.CharField(max_length=200, required=False)
    
    text          = forms.CharField(widget=forms.widgets.Textarea, required=False)
    
    draft         = forms.BooleanField(initial=1, required=False) #TODO, choices=DRAFT_CHOICES)

    # fields required by the comment system
    enable_comments = forms.BooleanField(initial=1, required=False)
    
    def fill_other_fields_from_instance(s):
        # reality check
        s.instance.make_sure_workshop_exists()
        w = s.instance.workshop_set.get()
        # lucky - workshop uses different field names. maybe I should make all these fields workshop_something?
        fields = w._meta.get_all_field_names()
        for field in fields:
            if s.fields.has_key(field):
                value = getattr(w, field)
                #print "wform: reading %s=%s" % (field, value)
                s.initial[field] = value

    def full_clean(s):
        # TODO - hack. Need to tell the slug field what the form is
        s.fields['slug'].form = s
        super(WorkshopForm, s).full_clean()

    def save(s):
        s.create_or_update_workshop_from_dict(s.cleaned_data)
        return super(WorkshopForm, s).save()

    def create_or_update_workshop_from_dict(s, d):
        # NOTE: should this be in the model? but it depends on the fields I choose for the form. But
        # those are chosen to match the names in the models. I'm almost convinced.
        p = s.instance
        p.make_sure_workshop_exists()
        w = p.workshop_set.get()

        w.post = p
        w.description = d['description']
        w.name = d['name']
        w.slug = d['slug']

        w.save()

class WorkshopEventForm(forms.ModelForm):
    instructors = forms.CharField(label='שם המנחים')
    contact = forms.EmailField(label="איש קשר")
    location = forms.CharField(label="איפה")
    class Meta:
        model = WorkshopEvent
        fields = ('instructors', 'contact', 'location', 'cost', 'duration')

