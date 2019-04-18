from rest_framework import generics
from . import serializers
from project import authentication, permissions


class WalletGenericMixing(object):
    authentication_classes = (authentication.OpenIdAuthentication, )
    permission_classes = (permissions.IdTokenHasPermission, )

    def get_object(self):
        # noinspection PyUnresolvedReferences
        return self.request.user.wallet


class WalletModelRetrieveAPIView(WalletGenericMixing, generics.RetrieveAPIView):
    required_permissions = ['wallet:read']
    serializer_class = serializers.WalletModelSerializer


class CurrentBalanceRetrieveAPIView(WalletGenericMixing, generics.RetrieveAPIView):
    required_permissions = ['wallet:current_balance:read']
    serializer_class = serializers.WalletCurrentBalanceModelSerializer


class WalletTopUpCreateAPIView(WalletGenericMixing, generics.CreateAPIView):
    required_permissions = ['wallet:top_up:write']
    serializer_class = serializers.WalletTopUpSerializer


class WalletChargeCreateAPIView(WalletGenericMixing, generics.CreateAPIView):
    required_permissions = ['wallet:charge:write']
    serializer_class = serializers.WalletChargeSerializer


class WalletTopUpForUserCreateAPIView(WalletGenericMixing, generics.CreateAPIView):
    required_permissions = ['wallet:top_up_for_user:write']
    serializer_class = serializers.WalletTopUpForUserSerializer

