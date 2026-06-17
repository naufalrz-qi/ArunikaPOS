# Rencana Implementasi: Arsitektur Sync 1-ke-1 & Penjadwalan Waktu

Sesuai arahan terbaru, konsep penggabungan "pintar" (*insert-only*) untuk Grosir dibatalkan. Web ini berfungsi sebagai wadah konsolidasi di mana data master akan disedot seluruhnya (timpa jika perlu) tanpa peduli sumbernya. Fokus baru kita adalah pada **Manajemen Periode Transaksi** dan **Penjadwalan**.

## 1. Perubahan Konsep "Full Sync" (Master Data)
- **Logika Standar**: *Full Sync* akan murni menarik seluruh data master (Kategori, Barang, Customer, dll) dari server yang dipilih. Tidak ada pengecualian "Grosir" atau "Gudang". Jika `kd_barang` sama, data terbaru yang masuk akan menimpa yang lama. Ini sesuai dengan konsep "1 server 1 database" untuk saat ini.

## 2. Fitur "Manual Sync" (Data Transaksi)
Data Transaksi (Penjualan & Pembelian) jumlahnya sangat besar, sehingga butuh filter rentang waktu.
- **Pilihan Periode**: Menambahkan formulir di UI (Pusat Kontrol) untuk memilih mode:
  - **Tahunan**: Misal memilih "Tahun 2023".
  - **Bulanan**: Misal memilih "Maret 2024".
  - **Mingguan**: Misal memilih "Minggu ke-12 Tahun 2024".
- **Backend Filter**: Fungsi `sync_incremental` di `etl.py` akan dimodifikasi agar bisa menerima rentang `start_date` dan `end_date`, sehingga query SQL Server-nya menjadi `WHERE tanggal_server BETWEEN ? AND ?`.

## 3. Fitur "Auto Sync" (Terjadwal & Berantai)
"Auto Sync" yang sesungguhnya adalah proses otomatis yang berjalan di belakang layar tanpa perlu dipencet tombolnya.
- **Cron Job**: Mendaftarkan jadwal otomatis (Cron) di Django-Q2.
- **Rentang 3 Hari**: Saat berjalan, sistem selalu mengambil data H-3 sampai hari ini.
- **Sekuensial / Bergantian**: Mengubah eksekusi Auto Sync agar berjalan secara antre (Server A selesai -> lanjut Server B -> lanjut Server C) untuk menghindari beban berlebih pada jaringan saat otomatisasi berjalan.

## 4. Fitur "Mass Sync" (Paralel Semua Server)
Ini adalah tombol "Nuklir" di UI.
- Memungkinkan pengguna memilih jenis sinkronisasi (Master atau Transaksi), dan menembakkannya ke **semua server aktif** secara bersamaan.
- Berjalan paralel (Multi-threading seperti yang sudah kita buat sebelumnya).

## User Review Required
> [!IMPORTANT]  
> 1. Untuk **Manual Sync (Transaksi)**, filter waktu ini apakah didasarkan pada tanggal terjadinya transaksi (misal `tanggal_nota`), atau berdasarkan waktu data diinput ke komputer (`tanggal_server`)? 
> 2. Untuk **Auto Sync (3 Hari)**, apakah Anda ingin saya mendaftarkan jadwalnya berjalan **setiap jam 12 malam otomatis**, atau Anda butuh tombol di Web untuk memicu proses "Auto Sync 3 Hari Berantai" ini secara manual kapanpun Anda mau?

## Proposed Changes
1. **[MODIFY] `templates/sync_control.html`**: Menambahkan *dropdown* Periode Waktu (Tahun/Bulan/Minggu) untuk Manual Sync.
2. **[MODIFY] `app_sync/etl.py`**: Mengubah `sync_incremental` agar menerima filter waktu (bukan lagi otomatis menggunakan log terakhir).
3. **[MODIFY] `app_sync/tasks.py`**: Menambahkan logika `task_sequential_auto_sync` yang looping server secara berurutan.
