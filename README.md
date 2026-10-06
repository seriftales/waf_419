# WAF419 - Web Application Firewall

WAF419, OSI 7. Katman (Uygulama) seviyesinde çalışan, `aiohttp` tabanlı asenkron bir Reverse Proxy ve Web Application Firewall prototipidir. 

Sistem, istemciden gelen HTTP isteklerini karşılar, önceden derlenmiş Regex kural motorundan geçirir ve trafik temizse asenkron olarak arka plandaki hedef sunucuya  iletir.

**Bu proje ; reverse proxy mimarisini, asenkron ağ programlamayı ve bazı zafiyetlerin WAF seviyesinde nasıl engellendiğini analiz etmek için tasarlanmıştır.**

## 🚀 Özellikler

* **Yüksek Performans:** JSON formatındaki güvenlik kuralları sistem ayağa kalkarken yalnızca bir kez okunup Regex objelerine derlenir. Bu sayede her istekte dosya okuma darboğazı engellenir.
* **Zafiyet Koruması:** URL parametreleri ayrıştırılırken, aynı isimle gönderilen birden fazla parametre birleştirilerek taranır. Böylece yükü bölerek WAF'ı atlatma girişimleri engellenir.
* **Güvenli Payload Ayrıştırma:** Gelen POST/PUT isteklerinin gövdesi taranırken, binary form verilerinin  sistemi çökertmemesi için hatalı karakterler yoksayılarak güvenli bir decode işlemi uygulanır.
* **Asenkron Yönlendirme:** `aiohttp` sayesinde I/O bloklaması yapılmadan, binlerce istek eşzamanlı olarak hedefe yönlendirilebilir.

## 🛠️ Kurulum ve Çalıştırma

Test ortamını izole etmek için WAF'ın arkasında koruyacağı hedef sunucu ayağa kaldırılmalıdır.

1. **Hedef Sunucuyu (Backend) Başlatın:**
Yeni bir terminalde, boş bir dizin içinde hedef sunucuyu 8000 portunda başlatın (config.py dosyasını kontrol edin):
```bash
python3 -m http.server 8000
```
2. **Bağımlılıkları Kurun ve WAF'ı Başlatın:**
```bash
pip install requirements.txt
python3 run.py
```
## ⚙️ Test Senaryoları

WAF aktifken üçüncü bir terminalden (veya farklı bir cihazdan) aşağıdaki curl komutlarıyla sistemin tepkilerini ölçebilirsiniz:

Not:`curl` paketi işletim sistemi seviyesinde kurulu olması gerekmektedir.

```bash 
    sudo apt update
    sudo apt install curl 
```

**Test 1: Temiz Trafik (Beklenen: 200 OK)**
Normal bir istek hedefe ulaşmalı ve arka plandaki sunucunun içeriğini döndürmelidir.

```bash 
curl -i http://localhost:8080/
```

**Test 2: URL Parametresinden SQL Injection (Beklenen: 403 Forbidden)**
Veritabanını atlatmaya yönelik klasik mantıksal zafiyet yükü WAF tarafından engellenmelidir.

```bash 
curl -i "http://localhost:8080/login?username=' OR 1=1 --"
```

**Test 3: HTTP Gövdesinden (POST) SQL Injection (Beklenen: 403 Forbidden)**
Saldırgan komutu URL yerine POST gövdesine gizlediğinde WAF'ın Body tarayıcısı devreye girmelidir.

```bash 
curl -i -X POST -d "search_query=select * from users" http://localhost:8080/api/search
```

**Test 4: Gelişmiş HPP Zafiyet Testi (Beklenen: 403 Forbidden)**
Saldırgan ilk parametreye temiz, aynı isimli ikinci parametreye zararlı kod yazarak WAF'ı atlatmaya çalışır. HPP koruması bunu yakalamalıdır.

```bash 
curl -i "http://localhost:8080/profile?id=5&id=sleep(10)"
```

## 📁 Dizin Yapısı

```text
WAF419/
├── app/
│   ├── config.py         # Hedef sunucu, port ve WAF konfigürasyonları
│   ├── core/
│   │   └── proxy.py      # Asenkron aiohttp reverse proxy motoru
│   ├── filters/
│   │   ├── filters.py    # Regex tabanlı kural motoru ve analiz mantığı
│   │   └── rules.json    # JSON formatında WAF güvenlik kuralları 
│   └── utils/
│       └── logger.py     # Loguru tabanlı sistem loglayıcısı
├── logs/                 # Çalışma zamanında üretilen trafik ve engelleme logları
├── run.py                # WAF uygulamasını başlatan ana tetikleyici
├── requirements.txt      
└── README.md             
└──.gitignore
```