from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.request import Request

from . import models


class WalletHistoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WalletHistoryModel
        exclude = ['wallet']


class WalletModelSerializer(serializers.ModelSerializer):
    wallet_history = serializers.ListSerializer(
        child=WalletHistoryModelSerializer(),
        source='wallet_history_set'
    )
    user = serializers.CharField(source='user.username')

    class Meta:
        model = models.WalletModel
        fields = '__all__'


class WalletCurrentBalanceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WalletModel
        fields = ['current_balance']


class WalletOperationSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0, write_only=True)
    current_balance = serializers.IntegerField(read_only=True)

    operation_name = None

    def update(self, instance, validated_data):
        raise NotImplemented()

    def create(self, validated_data):
        request = self.context.get('request')
        wallet = self.get_wallet(request, validated_data)
        amount = validated_data.get('amount')
        return self.perform_operation(wallet=wallet, amount=amount)

    def get_wallet(self, request, validated_data):
        return request.user.wallet

    def perform_operation(self, wallet, *args, **kwargs):
        if self.operation_name is None:
            raise NotImplemented
        return getattr(wallet, self.operation_name)(wallet_id=wallet.id, *args, **kwargs)


class WalletTopUpSerializer(WalletOperationSerializer):
    operation_name = 'cls_top_up'


class WalletChargeSerializer(WalletOperationSerializer):
    operation_name = 'cls_charge'


class WalletTopUpForUserSerializer(WalletOperationSerializer):
    for_user = serializers.CharField(write_only=True)
    operation_name = 'cls_top_up'

    def validate_for_user(self, attr):
        for_user = get_user_model().objects.filter(username=attr).first()
        if for_user is None:
            raise serializers.ValidationError('Wrong user')
        return for_user

    def get_wallet(self, request, validated_data):
        for_user = validated_data.get('for_user')
        return get_user_model().objects.get(id=for_user.id).wallet
