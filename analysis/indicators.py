"""
Teknik gosterge hesaplamalari: RSI, MACD, Hareketli Ortalamalar,
Hacim Degisimi ve ATR (oynaklik). Standart, yaygin bilinen formuller
kullanilir (Wilder RSI/ATR, klasik 12/26/9 MACD).
"""
import numpy as np
import pandas as pd

import config


def _compute_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def _compute_macd(close: pd.Series, fast: int, slow: int, signal: int):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def _compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """OHLCV DataFrame'ine tum teknik gostergeleri ekler ve dondurur.
    Girdi DataFrame'i degistirmez (kopya uzerinde calisir)."""
    df = df.copy()

    df["RSI"] = _compute_rsi(df["close"], config.RSI_PERIOD)

    macd_line, signal_line, hist = _compute_macd(
        df["close"], config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL
    )
    df["MACD"] = macd_line
    df["MACD_signal"] = signal_line
    df["MACD_hist"] = hist

    for window in config.MA_WINDOWS:
        df[f"SMA_{window}"] = df["close"].rolling(window=window, min_periods=1).mean()

    vol_ma = df["volume"].rolling(window=config.VOLUME_MA_WINDOW, min_periods=1).mean()
    df["Volume_MA"] = vol_ma
    df["Volume_Change_Pct"] = ((df["volume"] - vol_ma) / vol_ma.replace(0, np.nan)) * 100
    df["Volume_Change_Pct"] = df["Volume_Change_Pct"].fillna(0.0)

    df["ATR"] = _compute_atr(df, config.ATR_PERIOD)
    df["ATR_Pct"] = (df["ATR"] / df["close"]) * 100

    return df
