"""
Karar Motoru: Teknik gostergeler ve haber duyarliligini birlestirerek
0-100 arasi bir "Piyasa Egilim Skoru" hesaplar.

ONEMLI / DURUST UYARI:
Bu skor istatistiksel olarak dogrulanmis (backtest edilmis) bir olasilik
tahmini DEGILDIR. "Coin X, Y dakika icinde Z% olasilikla hareket edecek"
turunden kesin bir istatistik, sadece RSI/MACD/hareketli ortalama/hacim
ve basit haber taramasindan uretilemez - boyle bir sayi uretmek gercekte
var olmayan bir kesinlik iddia etmek olurdu. Bunun yerine burada, secilen
gostergelerin agirlikli bir sezgisel (heuristic) birlesimi hesaplanir:
gostergelerin O ANKI durumunun seffaf bir ozetidir, gelecege dair
dogrulanmis bir garanti degildir.
"""
import numpy as np
import pandas as pd

import config


def _score_rsi(rsi_value: float) -> float:
    if pd.isna(rsi_value):
        return 50.0
    return float(np.clip(rsi_value, 0, 100))


def _score_macd(current_hist: float, hist_series: pd.Series) -> float:
    if pd.isna(current_hist):
        return 50.0
    recent = hist_series.dropna().tail(50)
    mean_abs = recent.abs().mean() if len(recent) > 0 else 0.0
    scale = mean_abs * 3 if mean_abs and mean_abs > 0 else 1.0
    normalized = np.clip(current_hist / scale, -1, 1)
    return float(50 + normalized * 50)


def _score_ma(price: float, sma20: float, sma50: float) -> float:
    if pd.isna(sma20) or pd.isna(sma50):
        return 50.0
    if price > sma20 > sma50:
        return 100.0
    if price < sma20 < sma50:
        return 0.0
    if price > sma20:
        return 65.0
    if price < sma20:
        return 35.0
    return 50.0


def _score_volume(volume_change_pct: float) -> float:
    if pd.isna(volume_change_pct):
        return 50.0
    return float(50 + np.clip(volume_change_pct, -50, 50))


def compute_technical_score(df: pd.DataFrame):
    """Gostergelerle zenginlestirilmis DataFrame'in son satirindan 0-100
    arasi kompozit bir teknik skor ve alt-skor kirilimini dondurur.

    Donus: (composite_score: float, breakdown: dict)
    """
    last = df.iloc[-1]

    rsi_s = _score_rsi(last.get("RSI"))
    macd_s = _score_macd(last.get("MACD_hist"), df["MACD_hist"])
    ma_s = _score_ma(last.get("close"), last.get("SMA_20"), last.get("SMA_50"))
    vol_s = _score_volume(last.get("Volume_Change_Pct"))

    w = config.TECH_WEIGHTS
    composite = rsi_s * w["rsi"] + macd_s * w["macd"] + ma_s * w["ma"] + vol_s * w["volume"]

    breakdown = {"RSI": rsi_s, "MACD": macd_s, "MA": ma_s, "Hacim": vol_s}
    return float(composite), breakdown


def compute_composite_score(technical_score: float, sentiment_score: float) -> float:
    """Teknik skor ile haber duyarlilik skorunu config.py'deki agirliklara
    gore birlestirir. Sonuc 0-100 arasi sezgisel bir egilim skorudur."""
    w = config.COMPOSITE_WEIGHTS
    return float(technical_score * w["technical"] + sentiment_score * w["sentiment"])


def classify_score(score: float):
    """Skoru etiket + renge cevirir. Donus: (etiket: str, renk: str)"""
    if score >= config.SCORE_GREEN_THRESHOLD:
        return "Pozitif Eğilim", "green"
    if score <= config.SCORE_RED_THRESHOLD:
        return "Negatif Eğilim", "red"
    return "Nötr / Kararsız", "yellow"
