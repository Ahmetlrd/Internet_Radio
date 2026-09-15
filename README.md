# AREF-I: Re-Creating University Radio Using Internet Technologies 📻🌐

**AREF-I**, Sabancı Üniversitesi topluluğu için geleneksel radyo yayıncılığı kültürünü güncel internet ve Wi-Fi teknolojileriyle buluşturmayı hedefleyen uçtan uca bir **İnternet Radyosu (IoT Verici/Alıcı & Web Platformu)** projesidir.

Proje; donanım tarafında analog ses sinyalinin işlenmesi, sayısallaştırılması, Wi-Fi üzerinden UDP ile kablosuz iletimi ve alıcıda yeniden analog sese dönüştürülmesini; yazılım tarafında ise radyo kayıtlarının paylaşılabildiği bir web portalını kapsar.

---

## 📌 İçindekiler
- [Mimari ve Çalışma Mantığı](#-mimari-ve-çalışma-mantığı)
  - [1. Verici (Transmitter) Mimarisi](#1-verici-transmitter-mimarisi)
  - [2. Alıcı (Receiver) Mimarisi](#2-alıcı-receiver-mimarisi)
  - [3. Web Platformu (Flask & MySQL)](#3-web-platformu-flask--mysql)
- [Donanım Bileşenleri ve Araçlar](#-donanım-bileşenleri-ve-araçlar)
- [Proje Dizin Yapısı](#-proje-dizin-yapısı)
- [Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
  - [Gereksinimler](#gereksinimler)
  - [Web Sunucusu (Flask) Kurulumu](#web-sunucusu-flask-kurulumu)
  - [Mikrodenetleyici Kodlarının Yüklenmesi](#mikrodenetleyici-kodlarının-yüklenmesi)
- [Teknik Detaylar ve Devre Tasarımı](#-teknik-detaylar-ve-devre-tasarımı)
- [Mevcut Durum ve Gelecek Geliştirmeler](#-mevcut-durum-ve-gelecek-geliştirmeler)
- [Geliştiriciler & Danışman](#-geliştiriciler--danışman)
- [Lisans ve Kaynaklar](#-lisans-ve-kaynaklar)

---

## 🚀 Mimari ve Çalışma Mantığı

```
[ Analog Ses Girişi ]
        │
        ▼
[ Diyot Koruma Devresi (1.4V Pk-Pk) ]
        │
        ▼
[ Emitter Follower (BJT BC237 / Tampon & DC Bias) ]
        │
        ▼
[ Arduino Nano ADC (10-bit -> 6-bit char dönüşümü) ]
        │ UART (115200 Baud)
        ▼
[ ESP8266 NodeMCU (Verici) ]
        │
        │ Wi-Fi / UDP Paketleri (Port: 8808, 256 Bayt Paket Boyutu)
        ▼
[ ESP8266 NodeMCU (Alıcı) ]
        │ UART (115200 Baud)
        ▼
[ Arduino Nano (PORTB Doğrudan Pin Kontrolü) ]
        │
        ▼
[ 6-Bit R-2R Benzeri Dirençli DAC Devresi (Max 5 kHz) ]
        │
        ▼
[ Emitter Follower Akım Tamponu (Hoparlör Sürücü) ]
        │
        ▼
   🔊 [ Hoparlör ]
```

### 1. Verici (Transmitter) Mimarisi
1. **Giriş Koruması:** Stereo ses sinyali girişinde bulunan diyot koruma devresi ve 1 kΩ seri akım sınırlama direnci, giriş sinyalinin tepe-tepe gerilimini maksimum 1.4V seviyesinde tutarak mikrodenetleyiciyi aşırı gerilimden korur.
2. **Emitter Follower (BJT BC237):** Gerilim kazancı sağlamadan (Av ≈ 1) yüksek giriş empedansı ve güç kazancı sağlar. Kuplaj kondansatörü ile AC bileşeni geçirilir ve Arduino'nun 0–5V aralığını simetrik işleyebilmesi için sinyal DC orta gerilim (offset) üzerine oturtulur.
3. **Arduino Nano (Örnekleme):** Analog girişten (`A1`) okunan 10-bitlik değer (`0-1023`), alıcı DAC mimarisine uyum sağlamak amacıyla `16`'ya bölünerek 6-bit seviyesine (`0-63`) indirgenir. Hızlı işlem için `unsigned char` tipi kullanılır ve UART (115200 baud) üzerinden ESP8266'ya aktarılır.
4. **ESP8266 NodeMCU (UDP İletimi):** UART'tan okunan 256 baytlık bloklar paketlenerek yerel Wi-Fi ağı üzerinden hedef alıcı IP adresine UDP protokolü (varsayılan port: `8808`) ile iletilir.

### 2. Alıcı (Receiver) Mimarisi
1. **ESP8266 NodeMCU (UDP Alıcı):** 8808 portunu dinler, gelen 256 baytlık UDP veri paketlerini çözer ve gecikmeyi en aza indirmek için doğrudan seri port (UART) üzerinden alıcı Arduino'ya iletir.
2. **Arduino Nano (Paralel Çıkış):** Seri porttan gelen 6-bitlik ses verisi doğrudan `PORTB` register'ına (`Pin 8-13`) basılır.
3. **6-Bit DAC (Digital-to-Analog Converter):** Direnç ağı (Thevenin eşdeğeri tabanlı voltaj bölücü), 6-bit dijital veriyi ~5 kHz bant genişliğinde analog ses dalgasına dönüştürür.
4. **Çıkış Katı & Hoparlör Sürücüsü:** Standart op-amp'lerin tek kaynaklı düşük gerilimdeki sınırları ve Arduino'nun pin başına akım kısıtlaması (maksimum 70 mA port / ~10-20 mA güvenli) göz önüne alınarak BJT emitter follower akım tampon devresi kurulmuş, empedans uyumu sağlanarak ses hoparlöre iletilmiştir.

### 3. Web Platformu (Flask & MySQL)
Topluluğun yayınlanan kayıtları indirebilmesi ve yeni ses kayıtlarını yükleyebilmesi için Python tabanlı bir web portalı geliştirilmiştir:
- **Kullanıcı İşlemleri:** WTForms ile kayıt ve giriş formları, `passlib` (SHA-256) ile parola özetleme/şifreleme.
- **Radyo Kayıt Yönetimi:** `.wav` ve benzeri ses dosyalarının UUID ile isimlendirilerek sunucuya yüklenmesi (`/upload`) ve doğrudan dinlenip indirilmesi (`/download/<filename>`).

---

## 🛠 Donanım Bileşenleri ve Araçlar

| Kategori | Parça / Yazılım | Açıklama |
| :--- | :--- | :--- |
| **Mikrodenetleyici** | 2x NodeMCU ESP8266 | Wi-Fi UDP iletimi ve alımı |
| **Mikrodenetleyici** | 2x Arduino Nano | ADC örnekleme & DAC PORTB paralel çıkışı |
| **Yarıiletkenler** | BC237 NPN BJT Transistörler | Emitter follower tampon devreleri |
| **Devre Elemanları** | Muhtelif Direnç & Kondansatörler | R-2R DAC ağı, kuplaj ve filtreleme |
| **Giriş / Çıkış** | Ses Jakı, 8Ω Hoparlör | Stereo hat girişi ve analog ses çıkışı |
| **Test & Ölçüm** | Keysight Dijital Osiloskop, Multimetre | AC/DC sinyal analizi ve dalga formu gözlemi |
| **Simülasyon** | Falstad Circuit Simulator | Ön devre ve filtre testleri |
| **Geliştirme Ortamı** | Arduino IDE, VS Code, XAMPP (MySQL) | Gömülü yazılım ve web geliştirme |

---

## 📂 Proje Dizin Yapısı

```bash
AREF-I-Internet-Radio/
├── firmware/
│   ├── transmitter_arduino/
│   │   └── transmitter_arduino.ino   # ADC okuma (A1 / 16) & UART gönderim
│   ├── transmitter_esp8266/
│   │   └── transmitter_esp8266.ino   # Wi-Fi bağlantısı & UDP Verici (Port 8808)
│   ├── receiver_esp8266/
│   │   └── receiver_esp8266.ino      # UDP Alıcı & UART köprüleme
│   └── receiver_arduino/
│       └── receiver_arduino.ino      # UART okuma & PORTB (Pin 8-13) DAC çıkışı
├── hardware/
│   ├── schematics/                   # Devre şemaları (Proteus, Falstad, KiCAD vb.)
│   └── simulations/                  # Falstad devre simülasyon modelleri
├── web_app/
│   ├── app.py                        # Flask ana backend sunucu uygulaması
│   ├── uploads/                      # Yüklenen ses kayıtları (.wav)
│   ├── templates/
│   │   ├── index.html                # Ana sayfa
│   │   ├── register.html             # Kayıt sayfası
│   │   ├── login.html                # Giriş sayfası
│   │   ├── radio.html / upload.html  # Ses kayıt listeleme ve yükleme arayüzü
│   │   └── about.html                # Proje bilgi sayfası
│   └── requirements.txt              # Python bağımlılıkları
├── docs/
│   └── final_report.pdf              # Detaylı proje bitirme raporu
└── README.md
```

---

## 💻 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.8+
- MySQL / MariaDB (XAMPP önerilir)
- Arduino IDE ve ESP8266 Kart Kütüphanesi

### Web Sunucusu (Flask) Kurulumu

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/kullanici-adi/AREF-I-Internet-Radio.git
   cd AREF-I-Internet-Radio/web_app
   ```

2. Sanal ortam oluşturup aktif edin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için: venv\Scripts\activate
   ```

3. Gerekli Python paketlerini yükleyin:
   ```bash
   pip install Flask flask-mysqldb wtforms passlib
   ```

4. Veritabanını hazırlayın:
   - XAMPP üzerinde Apache ve MySQL servislerini başlatın.
   - phpMyAdmin üzerinden `ybblog` adında bir veritabanı oluşturun.
   - `users` tablosunu aşağıdaki alanlarla tanımlayın:
     ```sql
     CREATE TABLE users (
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(100),
         username VARCHAR(50),
         email VARCHAR(100),
         password VARCHAR(255)
     );
     ```

5. Sunucuyu başlatın:
   ```bash
   python app.py
   ```
   Tarayıcınızdan `http://localhost:5000` adresine gidin.

### Mikrodenetleyici Kodlarının Yüklenmesi

1. **ESP8266 (Verici & Alıcı):**
   - Kod içerisindeki `ssid` ve `password` alanlarını kendi yerel Wi-Fi ağınıza göre güncelleyin.
   - Verici ESP8266 kodundaki hedef IP adresini (`udp.beginPacket("192.168.x.x", udpPort)`), Alıcı ESP8266'nın aldığı IP adresi ile eşleştirin.
   - Baud rate'in her iki tarafta da `115200` olduğundan emin olun.
2. **Arduino Nano (Verici & Alıcı):**
   - Vericide analog ses kaynağını `A1` pinine bağlayın.
   - Alıcıda `D8` - `D13` (PORTB) pinlerini 6-bit DAC direnç girişlerine sırayla bağlayın.

---

## 🔬 Teknik Detaylar ve Devre Tasarımı

* **Giriş Koruması:** Ters paralel diyot eşiği sayesinde 1.4V pk-pk sınırlaması.
* **Hız Optimizasyonu:** UART aktarımlarında `int` yerine `unsigned char` ve `short` türleri tercih edilerek işlem gecikmesi en aza indirildi.
* **PORTB Manipülasyonu:** Standart `digitalWrite()` gecikmelerini bertaraf etmek amacıyla Arduino'nun donanımsal `PORTB` portu kullanılarak 6-bitlik DAC verisi tek saat çevriminde çıkışa basılır.
* **DAC & Frekans Yanıtı:** 6-bit direnç ağı ile insan sesinin anlaşılabilirliği için yeterli olan ~5 kHz bant genişliğinde çıkış elde edildi.

---

## 🔮 Mevcut Durum ve Gelecek Geliştirmeler

- [x] Analog giriş koruma ve DC seviye öteleme devresi
- [x] Arduino Nano 10-bit -> 6-bit örnekleme ve UART köprüsü
- [x] ESP8266 UDP üzerinden kablosuz ses veri aktarımı (256B buffer)
- [x] 6-bit direnç tipi DAC ve BJT çıkış tampon sürücüsü
- [x] Flask ses dosyası yükleme/indirme altyapısı
- [ ] 8-bit DAC yükseltmesi ve oluşan sinyal distorsiyonunun donanımsal çözümü
- [ ] Düşük gerilim rail-to-rail op-amp veya LM386 tabanlı güç amplifikatörü eklenmesi
- [ ] Flask - MySQL oturum (session) ve kullanıcı doğrulama mekanizmasının tam entegrasyonu
- [ ] ESP8266 Wi-Fi istemcisi için güvenlik duvarı (Firewall) ve kimlik doğrulama katmanı

---

## 👥 Geliştiriciler & Danışman

- **Ahmet Çavuşoğlu**
- **Efe Aydın**
- **Proje Danışmanı:** Prof. Dr. İbrahim Tekin (Sabancı Üniversitesi)

---

## 📜 Lisans ve Kaynaklar
Bu proje Sabancı Üniversitesi bünyesinde akademik ve araştırma amacıyla geliştirilmiştir. Açık kaynaklı bileşenler ve ilgili dokümantasyonlar eğitim amaçlı kullanıma uygundur.
