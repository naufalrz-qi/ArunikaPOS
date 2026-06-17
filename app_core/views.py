from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import ServerConfig
from .forms import ServerConfigForm, UserForm
from app_sync.connectors import test_server_connection

@login_required
def dashboard(request):
    from app_master.models import Barang, Customer
    from app_core.models import SyncLog
    
    context = {
        'servers': ServerConfig.objects.all(),
        'total_barang': Barang.objects.count(),
        'total_customer': Customer.objects.count(),
        'recent_logs': SyncLog.objects.order_by('-mulai_pada')[:5]
    }
    return render(request, 'dashboard.html', context)

@login_required
def server_list(request):
    servers = ServerConfig.objects.all()
    return render(request, 'server_list.html', {'servers': servers})

@login_required
def server_add(request):
    if request.method == 'POST':
        form = ServerConfigForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Server berhasil ditambahkan.')
            return redirect('server_list')
    else:
        form = ServerConfigForm()
    return render(request, 'server_form.html', {'form': form, 'title': 'Tambah Server'})

@login_required
def server_edit(request, server_id):
    server = get_object_or_404(ServerConfig, id=server_id)
    if request.method == 'POST':
        form = ServerConfigForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            messages.success(request, 'Server berhasil diubah.')
            return redirect('server_list')
    else:
        form = ServerConfigForm(instance=server)
    return render(request, 'server_form.html', {'form': form, 'title': 'Edit Server'})

@login_required
def server_delete(request, server_id):
    server = get_object_or_404(ServerConfig, id=server_id)
    if request.method == 'POST':
        server.delete()
        messages.success(request, 'Server berhasil dihapus.')
        return redirect('server_list')
    return render(request, 'server_confirm_delete.html', {'server': server})

@login_required
def test_server(request, server_id):
    server = get_object_or_404(ServerConfig, id=server_id)
    result = test_server_connection(server)
    return JsonResponse(result)

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengguna berhasil ditambahkan.')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'user_form.html', {'form': form, 'title': 'Tambah Pengguna'})

@login_required
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengguna berhasil diubah.')
            return redirect('user_list')
    else:
        form = UserForm(instance=user_obj)
    return render(request, 'user_form.html', {'form': form, 'title': 'Edit Pengguna'})

@login_required
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if request.user.id == user_obj.id:
            messages.error(request, 'Anda tidak bisa menghapus diri sendiri.')
        else:
            user_obj.delete()
            messages.success(request, 'Pengguna berhasil dihapus.')
        return redirect('user_list')
    return render(request, 'user_confirm_delete.html', {'user_obj': user_obj})
