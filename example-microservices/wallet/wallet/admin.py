from django.contrib import admin
from . import models


class WalletHistoryModelInline(admin.TabularInline):
    model = models.WalletHistoryModel
    readonly_fields = ['amount', 'before_amount', 'after_amount', 'created_at']
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.WalletModel)
class WalletModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_balance']
    readonly_fields = list_display
    raw_id_fields = ['user']
    inlines = [WalletHistoryModelInline]

