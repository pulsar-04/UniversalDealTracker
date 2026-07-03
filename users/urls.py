from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as user_views
from . import views

urlpatterns = [

    path('register/', user_views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    path('settings/', views.profile_settings, name='profile_settings'),
    path('settings/delete/', views.delete_account, name='delete_account'),

    path('settings/password/', auth_views.PasswordChangeView.as_view(
        template_name='users/change_password.html',
        success_url='/settings/'
    ), name='change_password'),

]