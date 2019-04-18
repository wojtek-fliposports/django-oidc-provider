from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views


app_name = 'pytech'

urlpatterns = [
    path('', TemplateView.as_view(template_name='pytech/home.html'), name='home'),
    path('accounts/login', auth_views.LoginView.as_view(template_name='pytech/login.html'), name='login'),
    path('accounts/logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
