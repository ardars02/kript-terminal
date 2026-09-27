# 📊 Kripto Karar Destek ve Olasılık Terminali

Python ve Streamlit ile geliştirilmiş, Binance genel (public) API'sini
kullanan, masaüstünde tek komutla çalıştırılabilen bir kripto para karar
destek panelidir.

> ⚠️ **Önemli Uyarı:** Bu uygulama yalnızca eğitim ve bilgilendirme
> amaçlıdır. Yatırım tavsiyesi değildir ve gerçek emir gönderme/alma
> özelliği YOKTUR — yalnızca izleme ve bilgi amaçlıdır. Uygulama
> içindeki "Piyasa Eğilim Skoru", teknik göstergeler ile haber
> başlıklarının ağırlıklı bir sezgisel (heuristic) bileşimidir;
> istatistiksel olarak doğrulanmış/backtest edilmiş bir fiyat hareketi
> olasılığı DEĞİLDİR. Kripto para piyasaları yüksek risklidir; kaldıraçlı
> işlemler sermayenizin tamamının kaybına yol açabilir. Kendi
> araştırmanızı yapın (DYOR).

---

## 🧠 "Olasılık Skoru" hakkında önemli bir not

İlk istekte, "X coininin önümüzdeki 5-15 dakika içinde %3 yükselme
olasılığı: %75" türünden kesin bir istatistiksel olasılık üretilmesi
istenmişti. Bunu dürüstçe belirtmek gerekir: RSI/MACD/hareketli
ortalama/hacim ve basit haber taraması gibi girdilerden böyle bir sayı
üretmenin bir yolu yoktur — bu girdilerle gerçekten var olmayan bir
istatistiksel kesinlik/doğrulama iddia etmiş olurdunuz, ki bu da sizi
(ya da uygulamayı kullanacak başka birini) yanıltabilir, özellikle de
kaldıraç kararları buna dayandırıldığında.

Bunun yerine bu uygulama, **aynı girdileri** kullanarak şeffaf ve
tamamen `config.py` içinden ayarlanabilir bir ağırlıklandırma formülüyle
hesaplanan bir **"Piyasa Eğilim Skoru" (0-100, renk kodlu)** sunar:
göstergelerin o anki durumunun bir özetidir, gelecekle ilgili doğrulanmış
bir tahmin değildir. Aynı sebeple, risk/pozisyon hesaplayıcı da bu skora
bağlı bir "önerilen kaldıraç" üretmez; yalnızca sizin girdiğiniz risk
yüzdesi ve stop-loss mesafesine göre standart sermaye risk yönetimi
matematiğini (pozisyon büyüklüğü) hesaplar.

## ✨ Özellikler

- **Canlı Veri:** Binance genel API'sinden anlık fiyat, hacim ve mum verisi
- **Teknik Göstergeler:** RSI (14), MACD (12/26/9), SMA (20/50/200), Hacim
  Değişimi (%), ATR (oynaklık)
- **Haber Duyarlılığı:** CoinDesk, Cointelegraph ve FED RSS akışlarından
  başlık toplama + anahtar kelime tabanlı duyarlılık skorlaması
  (opsiyonel olarak Claude API ile daha nüanslı hale getirilebilir)
- **Piyasa Eğilim Skoru:** Teknik + duyarlılık skorlarının ağırlıklı
  birleşimi, 0-100 arası, renk kodlu (yeşil/sarı/kırmızı)
- **Risk / Pozisyon Hesaplayıcı:** Hesap bakiyesi, risk yüzdesi ve
  stop-loss mesafesine göre standart pozisyon büyüklüğü hesaplaması
- **Koyu Tema Arayüz:** Streamlit + özel CSS ile modern görünüm
- **Otomatik Yenileme:** Ayarlanabilir aralıkla canlı veri güncelleme

## 📁 Proje Yapısı

```
kripto-terminal/
├── app.py                     # Ana Streamlit uygulaması
├── requirements.txt            # Python bağımlılıkları
├── .env.example                 # Opsiyonel ortam değişkenleri şablonu
├── config.py                    # Tüm ayarlanabilir parametreler + uyarı metni
├── data/
│   └── binance_client.py        # Binance genel API istemcisi (sadece okuma)
├── analysis/
│   ├── indicators.py             # RSI, MACD, SMA, Hacim, ATR hesaplamaları
│   ├── sentiment.py               # Haber toplama ve duyarlılık skorlama
│   └── decision_engine.py         # Kompozit "Piyasa Eğilim Skoru" mantığı
├── utils/
│   └── risk.py                    # Pozisyon büyüklüğü / risk hesaplayıcı
└── ui/
    ├── styles.py                  # Koyu tema CSS
    └── charts.py                  # Plotly grafik oluşturma
```

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.10 veya üzeri
- İnternet bağlantısı (Binance API ve haber RSS akışları için)

### 2. Sanal Ortam Oluşturma (önerilir)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Kurma
```bash
pip install -r requirements.txt
```

### 4. (Opsiyonel) AI Destekli Haber Analizi
Varsayılan olarak haber duyarlılığı basit anahtar kelime eşleştirmesiyle
hesaplanır ve hiçbir API anahtarı gerektirmez. Daha nüanslı bir analiz
isterseniz:
1. `.env.example` dosyasını `.env` olarak kopyalayın ve
   `ANTHROPIC_API_KEY` değerini girin.
2. `config.py` içinde `USE_LLM_SENTIMENT = True` yapın.
Bu adım tamamen opsiyoneldir ve etkinleştirildiğinde her haber başlığı
için bir API çağrısı yapıldığından maliyete/gecikmeye neden olabilir.

### 5. Uygulamayı Çalıştırma
```bash
streamlit run app.py
```
Tarayıcınızda otomatik olarak `http://localhost:8501` açılacaktır.

## ⚙️ Özelleştirme

Tüm parametreler `config.py` içinde toplanmıştır:
- `DEFAULT_SYMBOLS` — İzleme listesindeki pariteler
- `NEWS_FEEDS` — Taranacak RSS adresleri
- `TECH_WEIGHTS` / `COMPOSITE_WEIGHTS` — Skor ağırlıkları
- `BULLISH_KEYWORDS` / `BEARISH_KEYWORDS` — Duyarlılık anahtar kelimeleri
- `SCORE_GREEN_THRESHOLD` / `SCORE_RED_THRESHOLD` — Renk eşikleri

## 🌍 Binance Erişimi Hakkında Not

Binance'in genel API'sine erişim, bulunduğunuz ülkeye/bölgeye ve yerel
mevzuata göre değişebilir. Erişim sorunu yaşarsanız,
`data/binance_client.py` içindeki `BINANCE_BASE_URL` değerini
bölgenizde erişilebilir bir uç noktaya (ör. binance.us) veya CoinGecko
gibi alternatif bir genel API'ye uyarlayabilirsiniz. Herhangi bir
borsanın kullanım koşullarına ve bulunduğunuz yargı bölgesindeki
düzenlemelere uymak sizin sorumluluğunuzdadır.

## ❗ Bilinen Sınırlamalar

- Haber duyarlılığı varsayılan olarak basit anahtar kelime eşleştirmesi
  kullanır; gerçek bir dil modeli analizi değildir (opsiyonel LLM modu
  hariç).
- Piyasa Eğilim Skoru, backtest edilmiş/istatistiksel olarak
  doğrulanmış bir model değildir — bkz. yukarıdaki not.
- Uygulama herhangi bir emir GÖNDERMEZ/ALMAZ; yalnızca bilgi amaçlıdır.
- RSS akış adresleri zamanla değişebilir; çalışmazsa `config.py`
  içinden güncelleyin.
- SMA200 gibi uzun periyotlu göstergeler, seçilen mum aralığında yeterli
  geçmiş veri yoksa (ör. yeni listelenen bir coin) daha az anlamlı olur.
