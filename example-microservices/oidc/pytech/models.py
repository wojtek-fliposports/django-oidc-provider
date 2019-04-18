from django.db import models
from django.core import validators
from django.conf import settings
import uuid


class AbstractCommonModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.id)


class MicroServicePermissionModel(AbstractCommonModel):
    name = models.CharField(max_length=200, unique=True, validators=[validators.RegexValidator(r'^[a-z:_]+$')])

    def __str__(self):
        return self.name


class UserPermissionsModel(AbstractCommonModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_permissions_model')
    permissions = models.ManyToManyField('MicroServicePermissionModel', related_name='+')

