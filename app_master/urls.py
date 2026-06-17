from django.urls import path
from . import views

urlpatterns = [
    path('barang/', views.barang_list, name='barang_list'),
    path('kategori/', views.kategori_list, name='kategori_list'),
]
