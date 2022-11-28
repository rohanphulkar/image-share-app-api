from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account,SharedFile


class AccountAdmin(UserAdmin):
    list_display = ('email',  'is_admin', 'is_staff', 'is_verified')
    search_fields = ('email',)
    readonly_fields = ('id', )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ("email",)

class SharedFilesAdmin(admin.ModelAdmin):
    list_display = ('owner','file','link','date')
    search_fields = ('owner',)
admin.site.register(Account, AccountAdmin)
admin.site.register(SharedFile, SharedFilesAdmin)