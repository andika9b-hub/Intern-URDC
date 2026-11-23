# Buoy Detection System

Desktop application untuk mendeteksi **Red Buoy** dan **Green Buoy** secara real-time menggunakan model custom YOLOv8 (`best.pt`), OpenCV, dan GUI PySide6.

> **Penting:** file model `best.pt` tidak disertakan. Masukkan file hasil training Roboflow Anda sendiri ke `weights/best.pt`. Aplikasi tetap dapat dibuka dan menampilkan preview kamera walaupun model belum tersedia; deteksi AI baru aktif setelah model berhasil dimuat.

## 1. Fitur

- Live preview dari kamera laptop, webcam USB, atau kamera lain yang dikenali OpenCV.
- Scan indeks kamera 0 sampai 5 melalui tombol **Refresh Camera**.
- Beralih kamera tanpa menutup aplikasi.
- Inferensi menggunakan model lokal `weights/best.pt`, bukan model pretrained bawaan.
- Bounding box berwarna merah/hijau, nama kelas, dan confidence.
- Counter Red Buoy, Green Buoy, total objek, dan FPS.
- Pengaturan confidence threshold dan ukuran input model.
- Informasi kelas model, lokasi model, serta perangkat CPU/GPU.
- Capture frame beranotasi ke folder `captures/`.
- Log ringkas perubahan hasil deteksi.

## 2. Struktur folder

```text
Buoy_Detection_System/
├── main.py              # Entry point aplikasi
├── ui.py                # Layout dan event handler PySide6
├── detector.py          # Memuat model YOLO dan menjalankan inferensi
├── camera_manager.py    # Scan, buka, dan uji kamera OpenCV
├── worker.py            # QThread: capture kamera + inferensi di background
├── config.py            # Lokasi model, threshold, ukuran input, mapping kelas
├── requirements.txt     # Dependensi Python
├── README.md            # Panduan penggunaan
├── weights/
│   ├── best.pt          # LETAKKAN MODEL ANDA DI SINI (tidak disertakan)
│   └── .gitkeep
└── captures/            # Hasil capture otomatis disimpan di sini
    └── .gitkeep
```

## 3. Persiapan Windows dan VS Code

Disarankan menggunakan **Python 3.12 64-bit** dan Windows 10/11. Pastikan Python sudah ditambahkan ke PATH. Periksa melalui terminal:

```powershell
py --version
```

Buka folder `Buoy_Detection_System` di VS Code, kemudian buka **Terminal → New Terminal**. Jalankan perintah berikut satu per satu:

### A. Buat virtual environment

```powershell
py -3.12 -m venv .venv
```

### B. Aktifkan virtual environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell menolak aktivasi karena execution policy, jalankan perintah berikut hanya pada terminal saat ini, lalu ulangi aktivasi:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatif melalui Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Pastikan terminal menunjukkan prefix `(.venv)`.

### C. Perbarui pip dan instal library

Untuk penggunaan CPU (jalur paling sederhana):

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instalasi pertama dapat memerlukan waktu dan ruang disk cukup besar karena PyTorch serta dependensi Ultralytics.

**Untuk NVIDIA GPU:** sebelum `pip install -r requirements.txt`, buka halaman resmi PyTorch **Start Locally**, pilih Windows + pip + Python dan versi CUDA yang sesuai dengan driver GPU Anda, lalu jalankan perintah instalasi PyTorch yang dihasilkan halaman tersebut. Setelah itu jalankan `pip install -r requirements.txt`. Jangan menebak nomor CUDA atau memasang wheel CUDA yang tidak cocok.

Verifikasi instalasi:

```powershell
python -c "import torch, cv2; import PySide6; import ultralytics; print('Torch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('OpenCV:', cv2.__version__); print('Ultralytics:', ultralytics.__version__)"
```

### D. Pilih interpreter VS Code

Tekan `Ctrl+Shift+P` → **Python: Select Interpreter** → pilih interpreter dari folder project ` .venv\Scripts\python.exe `.

## 4. Pasang model Roboflow Anda

1. Salin file hasil training, biasanya bernama `best.pt`.
2. Letakkan di `Buoy_Detection_System/weights/best.pt`.
3. Pastikan nama file persis `best.pt` atau ubah `MODEL_PATH` di `config.py`.
4. Jalankan aplikasi. Nama kelas akan dibaca langsung dari metadata model YOLO saat model berhasil dimuat.

### Konfigurasi mapping nama kelas

Aplikasi mencoba mengenali beberapa alias umum secara otomatis, seperti `red buoy`, `red_buoy`, `buoy_merah`, `green buoy`, dan `buoy_hijau`.

Apabila nama kelas pada model berbeda, edit `CLASS_NAME_MAP` dalam `config.py`. Contoh:

```python
CLASS_NAME_MAP = {
    "buoy_merah": "red",
    "buoy_hijau": "green",
}
```

Kunci harus sama dengan nama kelas yang dibaca model (pencocokan tidak membedakan huruf besar/kecil dan underscore/hyphen dinormalisasi). Nilai mapping harus `red` atau `green`. Anda juga dapat menambah alias pada `RED_CLASS_ALIASES` dan `GREEN_CLASS_ALIASES`.

Jika model Anda menamai kelas dengan nama lain, lihat bagian **MODEL INFORMATION** pada sidebar setelah model dimuat, lalu masukkan nama persis tersebut ke mapping.

## 5. Jalankan aplikasi

Dari root project dan dengan `.venv` aktif:

```powershell
python main.py
```

## 6. Cara penggunaan

1. Hubungkan kamera laptop atau webcam USB.
2. Klik **Refresh Camera**. Program mencoba indeks kamera 0–5.
3. Pilih kamera dari dropdown.
4. Atur confidence threshold (contoh awal 45%) dan input size (640 × 640).
5. Klik **Start Detection**.
6. Tunggu model selesai dimuat. Jika `best.pt` valid, bounding box dan jumlah buoy akan tampil.
7. Klik **Capture Image** untuk menyimpan frame teranotasi ke folder `captures/`.
8. Klik **Stop Detection** untuk melepas kamera.

Saat kamera sedang berjalan, memilih kamera lain pada dropdown akan menghentikan worker lama, melepas perangkatnya, kemudian membuka kamera baru.

## 7. Alur dan arsitektur

```text
Camera dropdown
      │
      ▼
CameraManager ── OpenCV VideoCapture
      │
      ▼
DetectionWorker (QThread)
      │ frame BGR
      ▼
BuoyDetector ── local weights/best.pt (Ultralytics YOLO)
      │ annotated frame + counters
      ▼
Qt signals
      │
      ▼
PySide6 GUI ── video, metrics, FPS, event log, capture
```

- `main.py`: membuat QApplication dan membuka MainWindow.
- `ui.py`: seluruh komponen GUI, kontrol kamera, pengaturan, counter, log, dan capture.
- `camera_manager.py`: mencoba backend DirectShow, Media Foundation, dan default OpenCV; semua kamera probe dilepas kembali.
- `worker.py`: menjalankan kamera dan inferensi di QThread sehingga GUI tidak menjalankan inferensi di main thread.
- `detector.py`: hanya memuat file model lokal, membaca `model.names`, memetakan kelas, dan menggambar bounding box.
- `config.py`: satu tempat untuk mengubah path model, kamera yang discan, threshold, image size, dan mapping nama kelas.

## 8. Pengujian yang harus dilakukan di laptop

Pengujian perangkat fisik memerlukan akses ke kamera dan file `best.pt` milik Anda. Gunakan checklist ini setelah instalasi:

| Pengujian | Langkah | Hasil yang diharapkan |
|---|---|---|
| Kamera laptop | Refresh Camera, pilih indeks yang terdeteksi, Start | Live preview tampil |
| Webcam eksternal | Sambungkan USB, Refresh, pilih kamera baru | Webcam tampil |
| Pergantian kamera | Saat preview aktif, pilih kamera lain | Kamera lama dilepas dan kamera baru aktif |
| Red Buoy | Arahkan objek Red Buoy ke kamera | Box merah dan label kelas/confidence muncul |
| Green Buoy | Arahkan objek Green Buoy ke kamera | Box hijau dan label kelas/confidence muncul |
| Counter | Tampilkan beberapa buoy | Counter sesuai objek pada frame saat itu |
| Confidence | Ubah slider | Jumlah deteksi berubah sesuai threshold |
| Stop | Klik Stop Detection | Frame berhenti dan kamera dilepas |
| Capture | Saat preview aktif, klik Capture Image | JPG tersimpan di `captures/` |
| Model hilang | Pindahkan sementara `best.pt` | Aplikasi tetap terbuka; preview kamera bisa berjalan tanpa deteksi |

**Batas validasi:** source code dapat diperiksa secara sintaksis, tetapi keberhasilan deteksi aktual, kecocokan label dan akurasi hanya dapat dipastikan menggunakan `best.pt`, kamera, dan kondisi pencahayaan/perangkat Anda. Tidak ada file model palsu di dalam project ini.

## 9. Troubleshooting

### `No module named ...`
Pastikan `.venv` aktif dan interpreter VS Code benar. Jalankan ulang:

```powershell
python -m pip install -r requirements.txt
```

### PowerShell tidak mengizinkan aktivasi venv
Gunakan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, atau aktifkan melalui `cmd` dengan `.venv\Scripts\activate.bat`.

### Kamera tidak ditemukan
- Pastikan kamera terlihat di Windows Settings → Bluetooth & devices → Cameras.
- Tutup aplikasi lain yang mungkin sedang memakai kamera (Teams, Zoom, browser, aplikasi Camera).
- Klik Refresh Camera setelah webcam USB dipasang.
- Coba indeks lain jika Anda mengubah `CAMERA_SCAN_RANGE` dalam `config.py`.
- Beberapa kamera virtual atau kamera jaringan memerlukan driver/stream URL khusus dan tidak selalu muncul sebagai indeks OpenCV.

### Kamera terbuka tetapi layar hitam / gagal membaca frame
Coba cabut-pasang webcam, ganti port USB, tutup aplikasi kamera lain, atau perbarui driver. Backend dicoba berurutan melalui DirectShow, Media Foundation, lalu backend default OpenCV.

### `best.pt` tidak ditemukan
Pastikan file berada di `weights/best.pt`. Periksa ejaan nama dan ekstensi file Windows (hindari `best.pt.pt`).

### Model terbaca tetapi kelas buoy tidak terhitung
Periksa nama kelas yang ditampilkan di **MODEL INFORMATION**. Tambahkan nama kelas tersebut ke `CLASS_NAME_MAP`, misalnya `{"class_merah": "red", "class_hijau": "green"}`. Kelas yang tidak dipetakan tetap ditampilkan sebagai objek dengan box warna netral dan masuk ke total, tetapi tidak menambah counter Red/Green.

### GPU NVIDIA tidak digunakan
Jalankan:

```powershell
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

Jika `False`, kemungkinan PyTorch yang terpasang adalah build CPU, driver tidak cocok, atau lingkungan GPU belum terkonfigurasi. Instal ulang PyTorch menggunakan perintah resmi sesuai pilihan CUDA/driver Anda. Sistem tetap dapat berjalan di CPU.

### Inferensi lambat
- Pastikan laptop memiliki mode daya/performa yang sesuai.
- Coba turunkan input size ke 512 atau 416.
- Naikkan confidence threshold untuk mengurangi jumlah box yang diproses (ini tidak selalu mempercepat inferensi secara signifikan).
- Gunakan GPU NVIDIA dengan PyTorch CUDA yang cocok bila tersedia.

### `DLL load failed` atau konflik library
Buat ulang virtual environment yang bersih, lalu instal ulang dependensi. Hindari mencampur instalasi `opencv-python` dan `opencv-contrib-python` dalam satu environment.

## 10. Catatan teknis

- Counter diperbarui berdasarkan deteksi pada **frame saat ini**, bukan pelacakan ID objek. Objek yang sama akan tetap dihitung pada setiap frame selama terdeteksi.
- Total objek mencakup seluruh kelas yang terdeteksi model. Counter Red/Green hanya bertambah jika kelas terpetakan ke `red`/`green`.
- Sistem ini menjalankan inference secara lokal; frame tidak dikirim ke Roboflow atau layanan cloud.
- Deteksi buoy hanya sebaik kualitas dataset, hasil training, resolusi kamera, pencahayaan, dan sudut pandang.


## Model yang disertakan

Project siap ini sudah berisi `weights/best.pt` hasil model yang dikirim pengguna. Nama kelas yang dibaca dari metadata checkpoint: `red_buoy` dan `Green_Buoy` (mapping eksplisit ke red/green telah disiapkan di `config.py`). Jangan buka/edit `best.pt` sebagai teks.
