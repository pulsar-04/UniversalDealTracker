from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('cars/', views.car_list, name='car_list'),
    path('jobs/', views.job_list, name='job_list'),

    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/delete/<int:pk>/', views.delete_search, name='delete_search'),
]