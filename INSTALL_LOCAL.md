# 🚀 Nimbus - Local Kurulum Rehberi

## 📋 İçindekiler
- [Ön Gereksinimler](#ön-gereksinimler)
- [Hızlı Kurulum](#hızlı-kurulum)
- [Detaylı Kurulum](#detaylı-kurulum)
- [Kurulum Doğrulama](#kurulum-doğrulama)
- [İlk Backup](#ilk-backup)
- [Sorun Giderme](#sorun-giderme)

---

## Ön Gereksinimler

Nimbus'u çalıştırmak için:

- **Python 3.8 veya üzeri**
- **pip** (Python paket yöneticisi)
- **Git**
- **10 MB boş disk alanı** (core kurulum için)
- **500 MB boş disk alanı** (tüm optional özellikler için)

### Sistem Kontrolü

```bash
# Python versiyonunu kontrol edin
python3 --version
# Beklenen: Python 3.8.x veya üzeri

# pip kontrol
pip3 --version

# Git kontrol
git --version
```

---

## Hızlı Kurulum

Tek komutla hızlı kurulum:

```bash
# Projeyi klonla, virtual environment oluştur ve kur
git clone https://github.com/ysntns/Nimbus.git && \
cd Nimbus && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
pip install -e . && \
echo "✅ Kurulum tamamlandı!"
```

---

## Detaylı Kurulum

### 1. Projeyi Klonlayın

```bash
# GitHub'dan klonla
git clone https://github.com/ysntns/Nimbus.git

# Proje dizinine gir
cd Nimbus

# Dosyaları listele
ls -la
```

**Göreceğiniz dosyalar:**
```
├── app/                  # Ana uygulama
├── tests/                # Test dosyaları
├── requirements.txt      # Core bağımlılıklar
├── requirements-dev.txt  # Development bağımlılıkları
├── requirements-optional.txt  # Optional özellikler
├── setup.py              # Kurulum dosyası
├── README.md             # Dokümantasyon
└── ...
```

### 2. Virtual Environment Oluştur

**Neden virtual environment?**
- Sistem Python'unu kirletmez
- Proje bağımlılıkları izole edilir
- Farklı projeler arasında çakışma olmaz

```bash
# Virtual environment oluştur
python3 -m venv venv

# Aktif et (Linux/macOS)
source venv/bin/activate

# Aktif et (Windows CMD)
venv\Scripts\activate.bat

# Aktif et (Windows PowerShell)
venv\Scripts\Activate.ps1

# Başarılı aktivasyon sonrası terminalde göreceksiniz:
# (venv) user@computer:~/Nimbus$
```

### 3. Bağımlılıkları Kur

**3.1 pip'i Güncelle:**
```bash
pip install --upgrade pip
```

**3.2 Core Bağımlılıklar (Zorunlu):**
```bash
pip install -r requirements.txt
```

Bu 6 paketi kurar:
- `click` - CLI arayüzü
- `rich` - Güzel terminal çıktıları
- `loguru` - Loglama
- `pyyaml` - Config dosyaları
- `psutil` - Sistem bilgileri
- `requests` - HTTP istekleri

**3.3 Development Bağımlılıkları (Test için):**
```bash
pip install -r requirements-dev.txt
```

Test ve kod kalitesi araçları:
- `pytest` - Test framework
- `pytest-cov` - Coverage raporu
- `black` - Code formatter
- `isort` - Import sorter
- `flake8` - Linter
- `mypy` - Type checker

**3.4 Optional Özellikler (İsteğe Bağlı):**
```bash
pip install -r requirements-optional.txt
```

Ek özellikler:
- **Cloud**: Google Drive, AWS S3
- **Encryption**: AES-256-GCM
- **GUI**: PyQt6 desktop uygulaması
- **Scheduler**: Otomatik yedekleme
- **Compression**: Çoklu sıkıştırma
- **Notifications**: Email, Telegram

**Not:** Optional bağımlılıklar büyük (500+ MB). İhtiyacınız olmayanları kurmanıza gerek yok.

**3.5 Paketi Kur:**
```bash
# Development modunda kur (kodda yaptığınız değişiklikler hemen aktif olur)
pip install -e .
```

### 4. Kurulu Paketleri Kontrol Et

```bash
# Tüm kurulu paketleri listele
pip list

# Nimbus'un kurulu olduğunu doğrula
pip show nimbus-backup
```

---

## Kurulum Doğrulama

### Test 1: CLI Çalışıyor mu?

```bash
# Versiyon kontrolü
nimbus --version
# Beklenen: Nimbus Backup Solution v2.0.0

# Yardım menüsü
nimbus --help
# Komutları göreceksiniz: backup, restore, config, schedule, gui
```

### Test 2: Python Import Çalışıyor mu?

```bash
python3 -c "from app.core.backup import BackupEngine; print('✅ Import başarılı!')"
```

### Test 3: Testler Geçiyor mu?

```bash
# Tüm testleri çalıştır
pytest tests/unit/ -v

# Beklenen: 10 passed
```

### Test 4: Flake8 Temiz mi?

```bash
flake8 app/ tests/ --max-line-length=127

# Beklenen: Hata yok (sessizlik)
```

---

## İlk Backup

Kurulum başarılı! İlk yedeklemenizi yapın:

### Basit Örnek

```bash
# Test dizini oluştur
mkdir -p ~/test-source
echo "Merhaba Nimbus!" > ~/test-source/test.txt

# Yedekleme dizini
mkdir -p ~/test-backup

# Yedekleme yap
nimbus backup ~/test-source --destination ~/test-backup

# Sonuç:
# ✅ Backup Completed!
# Backed up 1 file(s)
```

### Gelişmiş Örnek

```bash
# Incremental + Compression + Verification
nimbus backup ~/Documents \
  --destination ~/Backups/documents \
  --incremental \
  --compress \
  --verify

# Progress bar ve istatistikler göreceksiniz
```

### Config Yönetimi

```bash
# Mevcut config'i gör
nimbus config show

# Ayar değiştir
nimbus config set performance.threads 8
nimbus config set backup.compression true

# Config dosyası: ~/.config/nimbus/config.yaml
```

---

## Python API Kullanımı

CLI yerine Python'dan da kullanabilirsiniz:

```python
from pathlib import Path
from app.core.backup import BackupEngine

# Kaynak ve hedef
source = Path.home() / "Documents"
destination = Path.home() / "Backups" / "documents"

# Backup engine oluştur
engine = BackupEngine(source, destination)

# Yedekleme yap
stats = engine.backup()

# Sonuçları göster
print(f"✅ {stats['backed_up_files']} dosya yedeklendi")
print(f"📦 Toplam boyut: {stats['total_size'] / (1024**3):.2f} GB")
```

### Progress Callback ile

```python
def progress_callback(data):
    percent = data['percentage']
    files = f"{data['backed_up_files']}/{data['total_files']}"
    print(f"Progress: {percent:.1f}% | Files: {files}")

engine = BackupEngine(source, destination)
engine.backup(progress_callback=progress_callback)
```

---

## GUI Kullanımı

PyQt6 GUI'yi başlatın (optional bağımlılıklar kuruluysa):

```bash
# GUI'yi başlat
nimbus gui

# veya Python'dan
python3 -c "from app.gui.main import main; main()"
```

**GUI Özellikleri:**
- 📁 Drag & drop source/destination seçimi
- ⚙️ Kolay ayar yönetimi
- 📊 Real-time progress tracking
- 📜 Backup geçmişi görüntüleme
- 🎨 Modern ve kullanıcı dostu arayüz

---

## Development Workflow

### Kod Değişikliği Yaptıktan Sonra

```bash
# Formatla
black app/ tests/
isort app/ tests/

# Lint kontrol
flake8 app/ tests/ --max-line-length=127

# Type check
mypy app/ --ignore-missing-imports

# Testleri çalıştır
pytest tests/ -v

# Coverage raporu
pytest tests/ --cov=app --cov-report=html
# Rapor: htmlcov/index.html
```

### Yeni Özellik Eklemek

```bash
# 1. Yeni branch oluştur
git checkout -b feature/my-new-feature

# 2. Kodu yaz
# ... kod değişiklikleri ...

# 3. Test yaz
# tests/unit/test_my_feature.py

# 4. Testleri çalıştır
pytest tests/unit/test_my_feature.py -v

# 5. Commit et
git add .
git commit -m "feat: Add my new feature"

# 6. Push et
git push origin feature/my-new-feature
```

---

## Sorun Giderme

### Problem 1: "ModuleNotFoundError: No module named 'app'"

**Çözüm:**
```bash
# Virtual environment aktif mi kontrol edin
which python3
# Görmeli: /path/to/Nimbus/venv/bin/python3

# Aktif değilse:
source venv/bin/activate

# Paketi tekrar kurun
pip install -e .
```

### Problem 2: "Permission denied"

**Çözüm:**
```bash
# sudo KULLANMAYIN!
# Virtual environment içinde sudo'ya gerek yok

# Eğer hala sorun varsa:
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Problem 3: "Command 'nimbus' not found"

**Çözüm:**
```bash
# 1. Virtual environment aktif mi?
source venv/bin/activate

# 2. Paket kurulu mu?
pip show nimbus-backup

# 3. PATH'e eklenmiş mi?
which nimbus

# Eğer hala çalışmazsa, Python modülü olarak çalıştırın:
python3 -m app.cli.main --help
```

### Problem 4: "ImportError: libQt6Core.so.6: cannot open shared object file"

PyQt6 için sistem kütüphaneleri gerekli.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0
```

**Fedora/RHEL:**
```bash
sudo dnf install -y \
    mesa-libGL \
    mesa-libEGL \
    libxkbcommon-x11
```

### Problem 5: Testler başarısız oluyor

```bash
# Cache temizle
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Bağımlılıkları yeniden kur
pip install --upgrade -r requirements.txt -r requirements-dev.txt

# Testleri tekrar çalıştır
pytest tests/ -v --tb=short
```

### Problem 6: "cryptography" kurulumu başarısız

**Windows:**
```powershell
# Microsoft C++ Build Tools gerekli
# https://visualstudio.microsoft.com/downloads/
# "Build Tools for Visual Studio" indirin
```

**Linux:**
```bash
# Build dependencies kur
sudo apt-get install -y python3-dev libffi-dev libssl-dev
# veya
sudo yum install -y python3-devel libffi-devel openssl-devel

# Tekrar dene
pip install cryptography
```

**macOS:**
```bash
# Xcode Command Line Tools
xcode-select --install

# OpenSSL
brew install openssl
```

---

## Kaldırma

Nimbus'u kaldırmak için:

```bash
# Virtual environment'tan çık
deactivate

# Proje dizinini sil
cd ..
rm -rf Nimbus

# Config dosyalarını da silmek isterseniz (opsiyonel)
rm -rf ~/.config/nimbus
```

---

## Ek Kaynaklar

- 📖 **README**: Genel bakış ve özellikler
- 🧪 **tests/**: Örnek kullanımlar
- 🎯 **app/cli/main.py**: CLI komutları
- 🔧 **app/core/config.py**: Config seçenekleri
- 🌐 **GitHub Issues**: Sorun bildirme

---

## İletişim

Sorunlarınız için:

- 🐛 **GitHub Issues**: https://github.com/ysntns/Nimbus/issues
- 📧 **Email**: ysn.tnss@gmail.com
- 💬 **Discussions**: https://github.com/ysntns/Nimbus/discussions

---

<div align="center">

**✅ Kurulum tamamlandı! Artık Nimbus ile yedekleme yapabilirsiniz!**

Made with ❤️ by Yasin TANIŞ

</div>
