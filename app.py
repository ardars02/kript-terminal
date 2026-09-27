"""
Kripto Karar Destek ve Olasilik Terminali
Ana Streamlit uygulamasi.

Bu uygulama YALNIZCA bilgilendirme/egitim amaclidir ve yatirim tavsiyesi
niteligi tasimaz. Hicbir emir gonderme/alma islevi icermez. Detaylar icin
README.md dosyasini ve asagida gosterilen uyari metnini okuyun.
"""
from datetime import datetime

import streamlit as st

import config
from data.binance_client import fetch_klines, fetch_ticker_24hr, BinanceAPIError
from analysis.indicators import add_all_indicators
from analysis.sentiment import fetch_news_headlines, compute_news_sentiment
from analysis.decision_engine import (
    compute_technical_score,
    compute_composite_score,
    classify_score,
)
from utils.risk import compute_position_size, classify_volatility
from ui.styles import get_custom_css
from ui.charts import build_price_chart

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False


st.set_page_config(
    page_title="Kripto Karar Destek ve Olasilik Terminali",
    page_icon="📊",
    layout="wide",
)
st.markdown(get_custom_css(), unsafe_allow_html=True)


@st.cache_data(ttl=10, show_spinner=False)
def cached_klines(symbol: str, interval: str, limit: int):
    return fetch_klines(symbol, interval, limit)


@st.cache_data(ttl=10, show_spinner=False)
def cached_ticker(symbol: str):
    return fetch_ticker_24hr(symbol)


@st.cache_data(ttl=300, show_spinner=False)
def cached_news():
    return fetch_news_headlines(config.NEWS_FEEDS, config.NEWS_MAX_ITEMS_PER_FEED)


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("⚙️ Ayarlar")

selected_symbol = st.sidebar.selectbox("Ana Coin", config.DEFAULT_SYMBOLS, index=0)
custom_symbol = st.sidebar.text_input("Özel Parite (ör. DOGEUSDT)", "").strip().upper()
if custom_symbol:
    selected_symbol = custom_symbol

interval = st.sidebar.selectbox(
    "Mum Aralığı", config.AVAILABLE_INTERVALS,
    index=config.AVAILABLE_INTERVALS.index(config.DEFAULT_INTERVAL),
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Otomatik Yenile", value=True)
refresh_seconds = st.sidebar.slider(
    "Yenileme Sıklığı (saniye)",
    config.MIN_AUTOREFRESH_SECONDS, config.MAX_AUTOREFRESH_SECONDS,
    config.DEFAULT_AUTOREFRESH_SECONDS,
)
if auto_refresh:
    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=refresh_seconds * 1000, key="data_refresh")
    else:
        st.sidebar.warning(
            "streamlit-autorefresh kurulu değil. `pip install streamlit-autorefresh` "
            "çalıştırın veya aşağıdaki butonla manuel yenileyin."
        )
if st.sidebar.button("🔄 Şimdi Yenile"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Risk / Pozisyon Hesaplayıcı")
st.sidebar.caption("Bu hesaplama bir kaldıraç/işlem önerisi değildir; yalnızca girdiğiniz değerlere göre standart sermaye risk matematiğidir.")
account_balance = st.sidebar.number_input(
    "Hesap Bakiyesi (USDT)", min_value=0.0, value=config.DEFAULT_ACCOUNT_BALANCE, step=100.0
)
risk_percent = st.sidebar.slider(
    "İşlem Başına Risk (%)", 0.1, 10.0, config.DEFAULT_RISK_PERCENT, step=0.1
)
stop_loss_percent = st.sidebar.slider(
    "Stop-Loss Mesafesi (%)", 0.1, 20.0, config.DEFAULT_STOP_LOSS_PERCENT, step=0.1
)

# ============================================================
# BAŞLIK VE YASAL UYARI
# ============================================================
st.title("📊 Kripto Karar Destek ve Olasılık Terminali")
st.markdown(f"<div class='disclaimer-box'>⚠️ {config.DISCLAIMER_TEXT}</div>", unsafe_allow_html=True)
st.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# İZLEME LİSTESİ
# ============================================================
st.subheader("👁️ İzleme Listesi")
watch_cols = st.columns(len(config.DEFAULT_SYMBOLS))
for i, sym in enumerate(config.DEFAULT_SYMBOLS):
    with watch_cols[i]:
        try:
            t = cached_ticker(sym)
            chg = float(t["priceChangePercent"])
            st.metric(sym.replace("USDT", ""), f"${float(t['lastPrice']):,.2f}", f"{chg:+.2f}%")
        except BinanceAPIError:
            st.warning(f"{sym}: alınamadı")

st.markdown("---")

# ============================================================
# ANA SEMBOL: VERİ ÇEKME
# ============================================================
try:
    df = cached_klines(selected_symbol, interval, config.KLINE_LIMIT)
    df = add_all_indicators(df)
    ticker_data = cached_ticker(selected_symbol)
except BinanceAPIError as e:
    st.error(f"Binance API hatası: {e}")
    st.info("Parite adının doğru olduğundan (ör. BTCUSDT) ve internet bağlantınızın aktif olduğundan emin olun.")
    st.stop()

news_items = cached_news()
sentiment_score, annotated_news = compute_news_sentiment(news_items[: config.NEWS_LOOKBACK_ITEMS])
tech_score, tech_breakdown = compute_technical_score(df)
composite = compute_composite_score(tech_score, sentiment_score)
label, color = classify_score(composite)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{selected_symbol} — Teknik Analiz ({interval})")
    st.plotly_chart(build_price_chart(df, selected_symbol), use_container_width=True)

with col2:
    st.subheader("🧮 Piyasa Eğilim Skoru")
    st.markdown(
        f"<div class='score-box score-{color}'><h1>{composite:.0f}/100</h1><p>{label}</p></div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Bu skor istatistiksel olarak doğrulanmış bir olasılık tahmini "
        "DEĞİLDİR; teknik göstergeler ile haber duyarlılığının ağırlıklı "
        "bir sezgisel (heuristic) bileşimidir. Bkz. README.md."
    )

    st.markdown("**Alt Skorlar**")
    st.write(f"Teknik Skor: {tech_score:.0f}/100")
    for k, v in tech_breakdown.items():
        st.progress(min(max(v / 100, 0.0), 1.0), text=f"{k}: {v:.0f}/100")
    st.write(f"Haber Duyarlılık Skoru: {sentiment_score:.0f}/100")

    st.markdown("---")
    atr_pct = df["ATR_Pct"].iloc[-1]
    vol_label = classify_volatility(atr_pct)
    st.subheader("📉 Oynaklık (ATR)")
    st.write(f"ATR: %{atr_pct:.2f} — **{vol_label} Oynaklık**")

    st.markdown("---")
    st.subheader("💰 Pozisyon Büyüklüğü Hesabı")
    pos = compute_position_size(
        account_balance, risk_percent, stop_loss_percent,
        current_price=float(ticker_data["lastPrice"]),
    )
    st.write(f"Önerilen Maks. Pozisyon: **${pos['position_size_usd']:,.2f}**")
    st.write(f"Riske Atılan Tutar: ${pos['max_loss_usd']:,.2f}")
    if "position_size_units" in pos:
        st.write(f"Yaklaşık Miktar: {pos['position_size_units']:.6f} {selected_symbol.replace('USDT', '')}")
    st.caption(
        "Bu, standart sermaye risk yönetimi matematiğidir; bir kaldıraç "
        "veya alım/satım tavsiyesi değildir."
    )

st.markdown("---")

# ============================================================
# HABER AKIŞI
# ============================================================
st.subheader("📰 Piyasa Haberleri ve Duyarlılık Analizi")
if annotated_news:
    tag_map = {"Pozitif": "green", "Negatif": "red", "Nötr": "gray"}
    for item in annotated_news[:15]:
        tag_color = tag_map.get(item["sentiment_label"], "gray")
        st.markdown(
            f"<div class='news-item'><span class='tag-{tag_color}'>{item['sentiment_label']}</span> "
            f"<a href='{item['link']}' target='_blank'>{item['title']}</a> "
            f"<span class='news-source'>— {item['source']}</span></div>",
            unsafe_allow_html=True,
        )
else:
    st.info("Şu anda haber kaynaklarından veri alınamadı.")

st.markdown("---")
st.caption(config.DISCLAIMER_TEXT)
if not config.USE_LLM_SENTIMENT:
    st.caption(
        "ℹ️ Haber duyarlılığı şu anda basit anahtar kelime eşleştirmesiyle "
        "hesaplanıyor. Daha gelişmiş AI destekli analiz için config.py "
        "içinde USE_LLM_SENTIMENT'ı etkinleştirin (bkz. README.md)."
    )
