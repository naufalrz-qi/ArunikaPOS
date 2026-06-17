from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Barang, Kategori

from django.db.models import Q

@login_required
def barang_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    kategori_id = request.GET.get('kategori', '')
    sort = request.GET.get('sort', 'kd_barang')
    
    barang_qs = Barang.objects.all()
    
    if q:
        barang_qs = barang_qs.filter(Q(nama__icontains=q) | Q(kd_barang__icontains=q))
        
    if status:
        barang_qs = barang_qs.filter(status=status)
    if kategori_id:
        barang_qs = barang_qs.filter(kd_kategori=kategori_id)
        
    valid_sorts = ['nama', '-nama', 'kd_barang', '-kd_barang']
    if sort in valid_sorts:
        barang_qs = barang_qs.order_by(sort)
    else:
        barang_qs = barang_qs.order_by('kd_barang')
        
    paginator = Paginator(barang_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    kategori_dict = {k.kd_kategori: k.nama for k in Kategori.objects.all()}
    for item in page_obj:
        item.nama_kategori = kategori_dict.get(item.kd_kategori, '-')
        
    context = {
        'page_obj': page_obj,
        'query': q,
        'filter_status': status,
        'filter_kategori': kategori_id,
        'sort': sort,
        'kategori_list': Kategori.objects.all().order_by('nama'),
    }
    return render(request, 'barang_list.html', context)

@login_required
def kategori_list(request):
    kategori_qs = Kategori.objects.all().order_by('kd_kategori')
    paginator = Paginator(kategori_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'kategori_list.html', {'page_obj': page_obj})
