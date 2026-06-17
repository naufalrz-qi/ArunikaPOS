from django.http import JsonResponse
from django_q.tasks import async_task
from django_q.models import Schedule
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from app_core.models import ServerConfig, SyncLog
from .tasks import task_full_sync, task_auto_sync, task_sequential_auto_sync

@login_required
def sync_control(request):
    servers = ServerConfig.objects.filter(is_active=True)
    auto_sync_active = Schedule.objects.filter(func='app_sync.tasks.task_sequential_auto_sync').exists()
    return render(request, 'sync_control.html', {'servers': servers, 'auto_sync_active': auto_sync_active})

@login_required
def trigger_sync(request):
    if request.method == 'POST':
        server_id = request.POST.get('server_id')
        sync_type = request.POST.get('sync_type')
        
        servers_to_sync = []
        if server_id == 'all':
            servers_to_sync = ServerConfig.objects.filter(is_active=True)
            if not servers_to_sync.exists():
                return JsonResponse({'success': False, 'message': 'Tidak ada server aktif.'})
        else:
            server = get_object_or_404(ServerConfig, pk=server_id)
            servers_to_sync = [server]
            
        task_ids = []
        for server in servers_to_sync:
            log = SyncLog.objects.create(
                server=server, 
                jenis=sync_type + '_sync', 
                status='running'
            )
            
            if sync_type == 'full':
                task_id = async_task('app_sync.tasks.task_full_sync', log.id, server.id)
            elif sync_type == 'auto':
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                task_id = async_task('app_sync.tasks.task_auto_sync', log.id, server.id, start_date, end_date)
                
            log.celery_task_id = task_id
            log.save()
            task_ids.append(task_id)
            
        return JsonResponse({
            'success': True, 
            'task_ids': task_ids,
            'is_multi': len(task_ids) > 1
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def toggle_auto_sync(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enable':
            Schedule.objects.update_or_create(
                func='app_sync.tasks.task_sequential_auto_sync',
                defaults={
                    'schedule_type': Schedule.MINUTES,
                    'minutes': 15,
                    'repeats': -1
                }
            )
        elif action == 'disable':
            Schedule.objects.filter(func='app_sync.tasks.task_sequential_auto_sync').delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def cancel_sync(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            if task_ids:
                SyncLog.objects.filter(celery_task_id__in=task_ids).update(status='cancelled')
                return JsonResponse({'success': True})
        except Exception as e:
            pass
    return JsonResponse({'success': False, 'message': 'Gagal membatalkan sync'})

@login_required
def task_status_view(request, task_id):
    log = SyncLog.objects.filter(celery_task_id=task_id).first()
    if not log:
        return JsonResponse({'pct': 0, 'status': 'error', 'message': 'Task not found'})
        
    if log.status == 'success':
        data = {'pct': 100, 'status': 'done', 'details': log.details}
    elif log.status == 'failed':
        data = {'pct': log.progress_pct, 'status': 'error', 'message': log.pesan_error, 'details': log.details}
    elif log.status == 'running':
        data = {'pct': log.progress_pct, 'status': 'PROGRESS', 'current': log.data_baru, 'total': log.total_data, 'details': log.details}
    else:
        data = {'pct': 0, 'status': log.status, 'details': log.details}
    return JsonResponse(data)

@login_required
def sync_log(request):
    from app_core.models import SyncLog
    logs = SyncLog.objects.all().order_by('-mulai_pada')[:100]
    return render(request, 'sync_log.html', {'logs': logs})

@login_required
def sync_harga(request):
    from app_master.models import BarangSatuan
    # Placeholder for harga manual sync
    return render(request, 'sync_harga.html')

@login_required
def empty_database(request):
    import json
    from django.conf import settings
    from django.apps import apps
    from django.db import connection

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data.get('db_password', '')
            
            db_pass = settings.DATABASES['default'].get('PASSWORD', '')
            if password != db_pass:
                return JsonResponse({'success': False, 'message': 'Password database salah!'})
                
            tables = []
            for app_label in ['app_master', 'app_transaksi']:
                app_config = apps.get_app_config(app_label)
                for model in app_config.get_models():
                    tables.append(model._meta.db_table)
            
            from app_core.models import SyncLog
            tables.append(SyncLog._meta.db_table)

            if tables:
                table_list = ', '.join(tables)
                with connection.cursor() as cursor:
                    cursor.execute(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE;")
                    
            return JsonResponse({'success': True, 'message': 'Database berhasil dikosongkan!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def get_server_tables(request):
    from django.apps import apps
    
    server_id = request.GET.get('server_id')
    if not server_id or server_id == 'all':
        return JsonResponse({'success': False, 'message': 'Pilih satu server tertentu.'})
        
    try:
        tables_info = []
        for app_label in ['app_master', 'app_transaksi']:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                table_name = model._meta.db_table
                if hasattr(model, 'server'):
                    count = model.objects.filter(server_id=server_id).count()
                    if count > 0:
                        tables_info.append({
                            'name': table_name,
                            'count': count
                        })
                    else:
                        tables_info.append({
                            'name': table_name,
                            'count': 0
                        })
        
        tables_info.sort(key=lambda x: x['name'])
        
        return JsonResponse({'success': True, 'tables': tables_info})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
