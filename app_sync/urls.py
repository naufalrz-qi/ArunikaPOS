from django.urls import path
from . import views

urlpatterns = [
    path('sync/', views.sync_control, name='sync_control'),
    path('sync/trigger/', views.trigger_sync, name='trigger_sync'),
    path('sync/cancel/', views.cancel_sync, name='cancel_sync'),
    path('sync/log/', views.sync_log, name='sync_log'),
    path('sync/toggle_auto/', views.toggle_auto_sync, name='toggle_auto_sync'),
    path('harga/', views.sync_harga, name='sync_harga'),
    path('api/task-status/<str:task_id>/', views.task_status_view, name='task_status'),
    path('sync/empty_database/', views.empty_database, name='empty_database'),
    path('sync/server_tables/', views.get_server_tables, name='server_tables'),
    path('sync/clear_queue/', views.clear_queue, name='clear_queue'),
]
