from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from bitforex.models import *


class AccountResource(resources.ModelResource):
    class Meta:
        model = Account
        fields = ['id', 'email', 'email_password', 'bitforex_password']


class BaseAdmin(ImportExportModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        return admin.ModelAdmin.change_view(self, request, object_id, form_url, extra_context=extra_context)


class AccountAdmin(admin.ModelAdmin):
    resource_class = AccountResource
    list_display = ['email', 'email_password', 'bitforex_password', 'access_key', 'secret_key']
    exclude = ['email_password', 'bitforex_password']
    readonly_fields = ['email', 'e_password', 'b_password']


admin.site.register(Account, AccountAdmin)
