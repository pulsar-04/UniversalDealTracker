from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as user_views
from . import views
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_done.html'), name='password_reset_complete'),
]