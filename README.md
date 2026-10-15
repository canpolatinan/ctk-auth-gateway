# 🛡️ AuthShield & Trie Visualizer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%252B-blue?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-UI-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

*Modern ve Güvenli Masaüstü Kimlik Doğrulama Ağ Geçidi ile Dinamik Trie (Sözlük Ağacı) Görselleştirme Motoru*

</div>

---

## 📖 Proje Hakkında

**AuthShield**, modern bir masaüstü arayüzü (`CustomTkinter`) arkasında güçlü bir kriptografik kimlik doğrulama altyapısı barındıran ve başarılı giriş sonrasında kullanıcıyı **Algoritma ve Veri Yapıları Görselleştirme Motoru**na yönlendiren hibrit bir yazılım projesidir. 

Proje, hem kurumsal düzeyde güvenli parola yönetimi standartlarını (`PBKDF2-SHA256`) hem de veri yapıları algoritmalarının (`Trie`) tuval (`Canvas`) üzerinde dinamik, animasyonlu ve ölçeklenebilir bir şekilde görselleştirilmesini bir arada sunar.

---

## ✨ Öne Çıkan Özellikler

### 🔐 1. Güvenli Kimlik Doğrulama Paneli
* **Parola Kriptografisi:** Şifreler asla düz metin (plaintext) olarak saklanmaz; `hashlib.pbkdf2_hmac` ve `secrets` modülleri ile 200.000 iterasyonla tuzlanarak (`salt`) hashlenir.
* **Zamanlama Saldırısı Koruması:** `hmac.compare_digest` kullanılarak güvenli string karşılaştırması yapılır.
* **Canlı Parola Gücü Analizi:** Kayıt ekranında şifre kriterlerini (uzunluk, büyük/küçük harf, rakam, özel karakter) anlık olarak denetleyen ilerleme çubuğu (`ProgressBar`).
* **Brute-Force Koruması:** Üst üste hatalı giriş denemelerinde otomatik süreli hesap kilitleme mekanizması.

### 🌳 2. Trie (Sözlük Ağacı) Görselleştirme Motoru
* **Dinamik Ağaç Algoritması:** Özyinelemeli (`recursive`) konumlandırma ve genişlik hesaplama mantığı.
* **Yumuşak Bézier Eğrileri:** Düğümler arasındaki bağlantı yolları kübik Bézier eğrileriyle (`Cubic Bézier`) pürüzsüz bir şekilde çizilir.
* **Akıcı Animasyonlar:** Kelime ekleme ve silme işlemlerinde adım adım vurgulama (`path animation`) efektleri.
* **Gelişmiş Kontroller:** Fare tekerleği ile yakınlaştırma (`Zoom`), tuval üzerinde sürükleme (`Pan`), dinamik ölçeklendirme ve düğümlere çift tıklayarak önek seçme kolaylığı.
* **Yerel Veri Kalıcılığı:** Kullanıcı hesapları `kullanicilar.json` dosyasında güvenli bir şekilde saklanır.

---

## 🛠️ Kullanılan Teknolojiler

* **Python 3.x**
* **CustomTkinter** (Modern ve şık arayüz bileşenleri)
* **Tkinter Canvas** (Özel vektörel çizim motoru)
* **Hashlib & Hmac** (Kriptografik güvenlik katmanı)
* **Pathlib & JSON** (Dosya yönetimi ve kalıcılık)

---

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için şu adımları izleyebilirsiniz:

1. **Depoyu klonlayın:**
   ```bash
   git clone [https://github.com/canpolatinan/ctk-auth-gateway.git](https://github.com/canpolatinan/ctk-auth-gateway.git)
   cd ctk-auth-gateway
