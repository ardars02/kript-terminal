"""
Kripto Karar Destek ve Olasilik Terminali - Merkezi Konfigurasyon
Tum ayarlanabilir parametreler burada toplanmistir.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# BORSA / VERI AYARLARI
# ------------------------------------------------------------------
BINANCE_BASE_URL = "https://data-api.binance.vision"
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
AVAILABLE_INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d"]
DEFAULT_INTERVAL = "15m"
KLINE_LIMIT = 250  # SMA200 icin yeterli veri noktasi

REQUEST_TIMEOUT_SECONDS = 10

# ------------------------------------------------------------------
# OTOMATIK YENILEME
# ------------------------------------------------------------------
DEFAULT_AUTOREFRESH_SECONDS = 30
MIN_AUTOREFRESH_SECONDS = 10
MAX_AUTOREFRESH_SECONDS = 300

# ------------------------------------------------------------------
# TEKNIK GOSTERGE PARAMETRELERI
# ------------------------------------------------------------------
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MA_WINDOWS = [20, 50, 200]
VOLUME_MA_WINDOW = 20
ATR_PERIOD = 14

# Teknik alt-skorlarin agirliklandirilmasi (toplami 1.0 olmalidir)
TECH_WEIGHTS = {
    "rsi": 0.30,
    "macd": 0.30,
    "ma": 0.25,
    "volume": 0.15,
}

# ------------------------------------------------------------------
# HABER / DUYARLILIK ANALIZI
# ------------------------------------------------------------------
NEWS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://www.federalreserve.gov/feeds/press_all.xml",
]
NEWS_MAX_ITEMS_PER_FEED = 10
NEWS_LOOKBACK_ITEMS = 20  # skor hesaplamasinda kullanilacak toplam haber sayisi

# Basit anahtar kelime tabanli duyarlilik sozlugu.
# NOT: Bu KABA ve SEZGISEL bir yontemdir, gercek bir dogal dil anlama
# (NLP) modeli DEGILDIR. Daha nuansli sonuclar icin asagidaki
# USE_LLM_SENTIMENT secenegine bakin.
BULLISH_KEYWORDS = [
    "rally", "surge", "soar", "bullish", "adoption", "approval", "approved",
    "etf approved", "rate cut", "all-time high", "record high", "breakout",
    "inflow", "accumulation", "partnership", "upgrade", "outperform",
    "yukselis", "yukseldi", "onay", "rekor",
]
BEARISH_KEYWORDS = [
    "crash", "plunge", "sell-off", "selloff", "bearish", "ban", "banned",
    "hack", "hacked", "exploit", "lawsuit", "sec charges", "rate hike",
    "recession", "default", "liquidation", "outflow", "downgrade", "fraud",
    "dusus", "cokus", "yasak", "sorusturma",
]

# Opsiyonel: LLM tabanli (Claude/Anthropic) duyarlilik analizi.
# True yapmadan once ANTHROPIC_API_KEY ortam degiskenini tanimlayin (.env).
# NOT: Etkinlestirildiginde her haber basligi icin bir API cagrisi yapilir,
# bu maliyete ve gecikmeye neden olabilir.
USE_LLM_SENTIMENT = False
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-sonnet-4-6"

# ------------------------------------------------------------------
# KOMPOZIT SKOR AGIRLIKLARI
# ------------------------------------------------------------------
# ONEMLI: Bu agirliklar, teknik gostergeler ile haber duyarliligini
# birlestiren SEZGISEL (heuristic) bir "Piyasa Egilim Skoru" uretir.
# Bu skor istatistiksel olarak dogrulanmis / backtest edilmis bir
# olasilik TAHMINI DEGILDIR; sadece secilen gostergelerin agirlikli
# ortalamasidir. Gelecekteki fiyat hareketlerini garanti etmez.
COMPOSITE_WEIGHTS = {
    "technical": 0.60,
    "sentiment": 0.40,
}

SCORE_GREEN_THRESHOLD = 65
SCORE_RED_THRESHOLD = 35

# ------------------------------------------------------------------
# RISK YONETIMI VARSAYILANLARI
# ------------------------------------------------------------------
# Bu degerler bir kaldirac/pozisyon ONERISI degildir; yalnizca
# kullanicinin kendi girdigi standart sermaye risk yonetimi
# hesaplamasi icin varsayilan baslangic degerleridir.
DEFAULT_ACCOUNT_BALANCE = 1000.0
DEFAULT_RISK_PERCENT = 1.0
DEFAULT_STOP_LOSS_PERCENT = 2.0

VOLATILITY_LOW_THRESHOLD = 1.0   # ATR% < bu deger -> Dusuk
VOLATILITY_HIGH_THRESHOLD = 3.0  # ATR% > bu deger -> Yuksek

# ------------------------------------------------------------------
# HAREKETLILIK TARAYICISI (MOMENTUM SCANNER)
# ------------------------------------------------------------------
# NOT: Bu tarayici, SECILEN zaman penceresinde GERCEKLESMIS OLAN fiyat
# degisimine gore siralama yapar - GECMISE DONUK bir olcumdur. Bir coinin
# bundan sonra da ayni yonde hareket edecegine dair bir garanti veya
# tahmin DEGILDIR.
MOMENTUM_WINDOW_OPTIONS = ["5m", "15m", "30m", "1h"]
MOMENTUM_DEFAULT_WINDOW = "15m"
MOMENTUM_DEFAULT_TOP_N = 20
MOMENTUM_CACHE_TTL_SECONDS = 60
MOMENTUM_EXCHANGE_INFO_TTL_SECONDS = 3600

# Taramadan haric tutulacak varlik turleri (heuristic filtreler):
# - Stabilcoin bazli paritelerde "hareket" cogunlukla anlamsiz gurultudur.
# - Kaldiracli token'lar (UP/DOWN/BULL/BEAR) normal spot coin degildir.
MOMENTUM_EXCLUDE_STABLE_BASES = {
    "USDC", "FDUSD", "TUSD", "BUSD", "DAI", "USDP", "PYUSD", "EURI", "USTC",
}
MOMENTUM_EXCLUDE_LEVERAGED_SUFFIXES = ("UP", "DOWN", "BULL", "BEAR")

# ------------------------------------------------------------------
# YASAL UYARI METNI
# ------------------------------------------------------------------
DISCLAIMER_TEXT = (
    "Bu uygulama yalnızca eğitim ve bilgilendirme amaçlıdır; yatırım "
    "tavsiyesi niteliği taşımaz. Gösterilen skorlar, teknik göstergeler "
    "ve haber başlıklarının ağırlıklı bir sezgisel (heuristic) "
    "birleşimidir; istatistiksel olarak doğrulanmış/backtest edilmiş "
    "bir fiyat tahmini veya olasılığı değildir. Kripto para piyasaları "
    "yüksek oynaklık içerir; kaldıraçlı işlemler sermayenizin tamamının "
    "kaybına yol açabilir. Karar vermeden önce kendi araştırmanızı yapın "
    "(DYOR) ve gerekiyorsa lisanslı bir finansal danışmana başvurun."
)
