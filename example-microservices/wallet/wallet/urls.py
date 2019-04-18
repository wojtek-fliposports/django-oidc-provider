from django.urls import path
from . import views


app_name = 'wallet'

urlpatterns = [
    path('current_balance', views.CurrentBalanceRetrieveAPIView.as_view(), name='current_balance'),
    path('top_up_for_user', views.WalletTopUpForUserCreateAPIView.as_view(), name='top_up_for_user'),
    path('top_up', views.WalletTopUpCreateAPIView.as_view(), name='top_up'),
    path('charge', views.WalletChargeCreateAPIView.as_view(), name='charge'),
    path('', views.WalletModelRetrieveAPIView.as_view(), name='wallet'),
]
