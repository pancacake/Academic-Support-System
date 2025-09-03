from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('api/login/', views.user_login, name='user_login'),
    path('api/register/', views.user_register, name='user_register'),
    path('api/logout/', views.user_logout, name='user_logout'),
    path('api/current-user/', views.get_current_user, name='get_current_user'),
    path('api/guest-mode/', views.set_guest_mode, name='set_guest_mode'),
]
