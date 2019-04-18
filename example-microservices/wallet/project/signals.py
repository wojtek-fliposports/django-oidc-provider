from django.dispatch import Signal

missing_user_signal = Signal(providing_args=["username"])
