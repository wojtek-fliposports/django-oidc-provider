from django.contrib import admin
from . import models


@admin.register(models.MicroServicePermissionModel)
class MicroServicePermissionModelAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(models.UserPermissionsModel)
class UserPermissionsModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']
    raw_id_fields = ['user']
