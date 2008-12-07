from django.contrib import admin

from models import SentEmail

class SentEmailAdmin(admin.ModelAdmin):
    #list_filter    = ('owners',)
    list_display = ('mail_from', 'mail_to', 'mail_subject')

admin.site.register(SentEmail, SentEmailAdmin)

