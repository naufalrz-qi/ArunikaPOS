from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app_core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('server/', views.server_list, name='server_list'),
    path('server/add/', views.server_add, name='server_add'),
    path('server/<int:server_id>/edit/', views.server_edit, name='server_edit'),
    path('server/<int:server_id>/delete/', views.server_delete, name='server_delete'),
    path('server/<int:server_id>/test/', views.test_server, name='test_server'),
    
    path('user/', views.user_list, name='user_list'),
    path('user/add/', views.user_add, name='user_add'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('user/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    path('master/', include('app_master.urls')),
    path('', include('app_sync.urls')),
]
