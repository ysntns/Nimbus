# 🚀 GitHub'a Yükleme Rehberi

Bu rehber, Nimbus projesini GitHub'a private repository olarak yüklemeniz için adım adım talimatları içerir.

## 📋 Önkoşullar

1. **Git kurulu olmalı**
```bash
git --version
# Eğer kurulu değilse:
sudo apt install git
```

2. **GitHub hesabı** (www.github.com)

3. **GitHub CLI (gh) - Önerilen**
```bash
# Ubuntu/Debian:
sudo apt install gh

# veya snap ile:
sudo snap install gh
```

---

## 🔐 Yöntem 1: GitHub CLI ile (Önerilen)

### Adım 1: GitHub'a Giriş Yapın

```bash
gh auth login
```

- "GitHub.com" seçin
- "HTTPS" seçin
- "Login with a web browser" seçin
- Tarayıcıda açılan sayfada giriş yapın

### Adım 2: Otomatik Deployment

```bash
cd /home/claude/nimbus
./scripts/deploy-github.sh
```

Bu script:
- ✅ Git repo'yu başlatır
- ✅ Dosyaları ekler
- ✅ Initial commit oluşturur
- ✅ Private repo oluşturur
- ✅ GitHub'a push yapar

**Tamamdır! 🎉**

Repo adresi: https://github.com/ysntns/nimbus

---

## 🔧 Yöntem 2: Manuel (GitHub CLI olmadan)

### Adım 1: Git Repo Başlatma

```bash
cd /home/claude/nimbus
git init
git add .
git commit -m "Initial commit: Nimbus v2.0.0

- Complete backup engine with incremental support
- CLI interface with rich output
- Configuration management system
- Multi-threading support
- Verification and checksums
- Test suite
- Documentation
- CI/CD pipeline

Created by Yasin TANIŞ - CerebrAI-VorTX"

git branch -M main
```

### Adım 2: GitHub'da Repository Oluşturma

1. https://github.com/new adresine gidin
2. **Repository name:** `nimbus`
3. **Description:** `Enterprise Backup & Cloud Sync Solution for Linux`
4. ✅ **Private** seçin
5. ❌ README, .gitignore, license EKLEMEYIN (zaten var)
6. "Create repository" tıklayın

### Adım 3: Local Repo'yu GitHub'a Bağlama

GitHub'da gösterilen komutları kullanın:

```bash
git remote add origin https://github.com/ysntns/nimbus.git
git push -u origin main
```

**Kullanıcı adı ve şifre isterse:**
- Username: GitHub kullanıcı adınız
- Password: **Personal Access Token** (şifre değil!)

### Adım 4: Personal Access Token Oluşturma (Gerekirse)

1. https://github.com/settings/tokens adresine gidin
2. "Generate new token" → "Generate new token (classic)"
3. **Note:** "Nimbus Access"
4. **Expiration:** 90 days veya istediğiniz süre
5. **Scopes:** `repo` seçin (tüm alt seçenekler işaretlenir)
6. "Generate token"
7. Token'ı kopyalayın (bir daha gösterilmez!)
8. Password yerine bu token'ı kullanın

---

## 🔄 Sonraki Güncellemeler İçin

```bash
# Değişiklikleri ekle
git add .

# Commit oluştur
git commit -m "Açıklayıcı mesaj"

# GitHub'a gönder
git push origin main
```

---

## 🌿 Branch Stratejisi (İsteğe Bağlı)

```bash
# Feature branch oluştur
git checkout -b feature/cloud-integration

# Değişiklikleri commit et
git add .
git commit -m "Add cloud integration"

# GitHub'a push et
git push origin feature/cloud-integration

# GitHub'da Pull Request oluştur
```

---

## 📊 Repository Durumunu Kontrol

```bash
# Remote bilgilerini görüntüle
git remote -v

# Son commit'leri görüntüle
git log --oneline -5

# Dosya durumunu kontrol et
git status

# Branch'leri listele
git branch -a
```

---

## 🛡️ .gitignore Kontrolü

Hassas dosyaların yüklenmediğinden emin olun:

```bash
# .gitignore'da olması gerekenler:
cat .gitignore | grep -E "\.env|\.key|secrets|credentials"
```

Eğer hassas dosya varsa:

```bash
# Git'ten kaldır (dosyayı silmeden)
git rm --cached sensitive-file.txt

# Tekrar commit et
git commit -m "Remove sensitive file"
git push origin main
```

---

## ✅ Doğrulama Checklist

Yükleme sonrası kontrol edin:

- [ ] Repository private olarak oluşturuldu
- [ ] README.md görünüyor
- [ ] Dosya yapısı eksiksiz
- [ ] .gitignore çalışıyor (venv, __pycache__ yüklenmemiş)
- [ ] CI/CD workflow dosyası var (.github/workflows/ci.yml)
- [ ] License dosyası var
- [ ] Hassas bilgiler (key, credential) yüklenmemiş

---

## 🚨 Sorun Giderme

### "Permission denied" hatası

```bash
# SSH key kullanıyorsanız:
ssh-keygen -t ed25519 -C "ysn.tnss@gmail.com"
cat ~/.ssh/id_ed25519.pub
# Bu key'i GitHub > Settings > SSH Keys'e ekleyin

# HTTPS kullanıyorsanız:
gh auth login  # Tekrar giriş yapın
```

### "Remote already exists" hatası

```bash
git remote remove origin
git remote add origin https://github.com/ysntns/nimbus.git
```

### Büyük dosya hatası

```bash
# Git LFS kurun
sudo apt install git-lfs
git lfs install

# Büyük dosyaları track edin
git lfs track "*.zip"
git lfs track "*.tar.gz"

git add .gitattributes
git commit -m "Add Git LFS"
git push origin main
```

---

## 📧 Destek

Sorun yaşarsanız:
- Email: ysn.tnss@gmail.com
- GitHub: @ysntns

---

## 🎉 Başarılı Yükleme Sonrası

Repository başarıyla yüklendikten sonra:

1. **GitHub Actions** otomatik çalışacak
2. **Issues** ve **Discussions** aktif edilebilir
3. **Project Board** oluşturabilirsiniz
4. **Wiki** sayfaları ekleyebilirsiniz
5. **Collaborators** ekleyebilirsiniz

Repository URL'iniz:
**https://github.com/ysntns/nimbus**

---

**Tebrikler! Nimbus artık GitHub'da! 🚀**

_Son Güncelleme: 7 Kasım 2024_
