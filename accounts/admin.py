from django.contrib import admin

from django.contrib.admin.models import User

from models import CapchaRequest, UserProfile, Member

class CapchaRequestAdmin(admin.ModelAdmin):
    list_display   = ('hash', 'letters')

class MemberAdmin(admin.ModelAdmin):
#    fields = ['payment_amount', 'payment_method', 'payment_number_of_payments', 'payment_reciet_sent',  'arrived_following']
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password',
                'phone', 'address', 'in_citytree_list',
                'arrived_following', 'admin_notes')
        }),
        ('Payment Details', {
            'fields': ('payment_amount', 'payment_method', 'payment_number_of_payments',
            'payment_reciet_sent'),
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields' : ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        })
    )
    list_display = ('first_name', 'last_name', 'arrived_following', 'payment_amount')

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password',
                'phone', 'address', 'in_citytree_list',
                'admin_notes')
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields' : ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        })
    )

admin.site.register(CapchaRequest, CapchaRequestAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

