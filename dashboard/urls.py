from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('create/', views.create_poll, name='create_poll'),
    path('manage/', views.manage_polls, name='manage_polls'),
    path('poll/<int:poll_id>/edit/', views.edit_poll, name='edit_poll'),
    path('poll/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
    path('poll/<int:poll_id>/toggle/', views.toggle_poll, name='toggle_poll'),
    path('poll/<int:poll_id>/monitor/', views.poll_monitor, name='poll_monitor'),
]