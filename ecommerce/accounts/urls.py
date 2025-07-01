from django.urls import path
from .views import (register, login, logout, activate, dashboard, reset_password,
                    redirect_to_dashboard, forgot_password, reset_password_validate)

urlpatterns = [
    path('', redirect_to_dashboard, name='dashboard_redirect'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('reset-password-validate/<uidb64>/<token>/', reset_password_validate, name='reset_password_validate'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('dashboard/', dashboard, name='dashboard'),
]