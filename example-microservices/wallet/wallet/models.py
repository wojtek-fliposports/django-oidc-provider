from django.db import models, transaction
from django.core.exceptions import ValidationError
import uuid
from django.conf import settings


class AbstractCommonModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.id)


class WalletHistoryModel(AbstractCommonModel):
    wallet = models.ForeignKey('WalletModel', on_delete=models.CASCADE, related_name='wallet_history_set')
    amount = models.PositiveIntegerField(editable=False)
    before_amount = models.PositiveIntegerField(editable=False)
    after_amount = models.PositiveIntegerField(editable=False)

    class Meta:
        index_together = (
            ('wallet', 'amount'),
            ('wallet', 'created_at'),
        )


class WalletModel(AbstractCommonModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    current_balance = models.PositiveIntegerField(editable=False, default=0)

    @classmethod
    def cls_top_up(cls, wallet_id, amount):
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0')

        with transaction.atomic():
            wallet = cls.objects.filter(id=wallet_id).select_for_update().first()
            WalletHistoryModel.objects.create(
                wallet=wallet,
                amount=amount,
                before_amount=wallet.current_balance,
                after_amount=wallet.current_balance + amount
            )
            wallet.current_balance += amount
            wallet.save(
                force_update=True,
                update_fields=['current_balance']
            )
            return wallet

    @classmethod
    def cls_charge(cls, wallet_id, amount):
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0')

        with transaction.atomic():
            wallet = cls.objects.filter(id=wallet_id, current_balance__gte=amount).select_for_update().first()
            if wallet is None:
                raise ValidationError('Insufficient funds!')
            WalletHistoryModel.objects.create(
                wallet=wallet,
                amount=amount,
                before_amount=wallet.current_balance,
                after_amount=wallet.current_balance - amount
            )
            wallet.current_balance -= amount
            wallet.save(
                force_update=True,
                update_fields=['current_balance']
            )
            return wallet




