from django.contrib.auth import get_user_model

from . import models


def create_wallet(**kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    raw = kwargs.get('raw')
    if raw is True or not created:
        return
    models.WalletModel.objects.create(
        user=instance
    )


def create_missing_user(**kwargs):
    username = kwargs.get('username')
    if username is None:
        return
    get_user_model().objects.create_user(username=username)





