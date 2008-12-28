from django.contrib import admin

from models import SentEmail

class SentEmailAdmin(admin.ModelAdmin):
    list_filter    = ('mail_sent_date', 'mail_to')
    list_display = ('mail_from', 'mail_to', 'mail_sent_date', 'mail_subject')

admin.site.register(SentEmail, SentEmailAdmin)

