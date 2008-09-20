from django.contrib import admin

from models import BannedIp, AllowedBanRequests

class BannedIpAdmin(admin.ModelAdmin):
    pass

class AllowedBanRequestsAdmin(admin.ModelAdmin):
    pass

admin.site.register(AllowedBanRequests, AllowedBanRequestsAdmin)
admin.site.register(BannedIp, BannedIpAdmin)

