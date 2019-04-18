from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from signals import missing_user_signal


class WalletConfig(AppConfig):
    name = 'wallet'

    def ready(self):
        from . import signal_handlers
        post_save.connect(signal_handlers.create_wallet, sender=get_user_model())
        missing_user_signal.connect(signal_handlers.create_missing_user)

