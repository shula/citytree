from django.contrib import admin

from models import Workshop, BlogWorkshop, WorkshopEvent, WorkshopEventPart, ExternalParticipant

class WorkshopAdmin(admin.ModelAdmin):
    list_filter    = ('owners',)
    list_display = ('name', 'slug', 'description')

class BlogWorkshopAdmin(admin.ModelAdmin):
    pass

class WorkshopEventAdmin(admin.ModelAdmin):
    pass

class WorkshopEventPartAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_time'

class ExternalParticipantAdmin(admin.ModelAdmin):
    list_filter    = ('workshop_event',)

for model, modeladmin in [
        (Workshop, WorkshopAdmin),
        (BlogWorkshop, BlogWorkshopAdmin),
        (WorkshopEvent, WorkshopEventAdmin),
        (WorkshopEventPart, WorkshopEventPartAdmin),
        (ExternalParticipant, ExternalParticipantAdmin),
        ]:
    admin.site.register(model, modeladmin)

