from django.urls import path
from .views import register, login, logout, activate, dashboard, redirect_to_dashboard

urlpatterns = [
    path('', redirect_to_dashboard, name='dashboard_redirect'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('dashboard/', dashboard, name='dashboard'),
]