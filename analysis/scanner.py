"""
Piyasa Genelinde Hareketlilik Tarayicisi (Momentum Scanner).

NOT / DURUST UYARI: Burada uretilen siralama, KULLANICININ SECTIGI zaman
penceresinde (ornegin son 5 veya 15 dakika) GERCEKLESMIS OLAN fiyat
degisimine dayanir. Bu GECMISE DONUK bir olcumdur - bir coinin "yukselmesi
planlanan" ya da "yukselecek" oldugunun bir tahmini veya garantisi
DEGILDIR. Guclu bir kisa vadeli hareket ayni sekilde devam edebilecegi
gibi aninda tersine de donebilir. Sadece o ana kadar ne oldugunu gosterir.

Bu modul, sadece popüler birkaç coin yerine Binance'teki TUM USDT
paritelerini tarar.
"""
import pandas as pd

import config
from data.binance_client import fetch_klines_bulk

MAX_WINDOW_MINUTES = 60  # config.MOMENTUM_WINDOW_OPTIONS icindeki en genis secenek ("1h")


def get_scannable_symbols(exchange_info: dict) -> list:
    """exchangeInfo yanitindan, taramaya uygun USDT paritelerinin
    listesini cikarir. Stabilcoin ve kaldiracli token paritelerini
    (heuristic olarak) haric tutar."""
    symbols = []
    for s in exchange_info.get("symbols", []):
        if s.get("status") != "TRADING":
            continue
        if s.get("quoteAsset") != "USDT":
            continue
        base = s.get("baseAsset", "")
        if base in config.MOMENTUM_EXCLUDE_STABLE_BASES:
            continue
        if any(base.endswith(suf) for suf in config.MOMENTUM_EXCLUDE_LEVERAGED_SUFFIXES):
            continue
        symbols.append(s["symbol"])
    return symbols


def _window_size_to_minutes(window_size: str) -> float:
    unit = window_size[-1]
    value = float(window_size[:-1])
    if unit == "m":
        return value
    if unit == "h":
        return value * 60
    if unit == "d":
        return value * 60 * 24
    return value


def fetch_momentum_klines(exchange_info: dict) -> dict:
    """Taranabilir tum semboller icin son ~60 dakikalik 1-dakikalik mum
    verisini ceker. TUM pencere secenekleri (5dk/15dk/30dk/1sa) bu TEK
    veri setinden hesaplanir - pencere degistirmek yeni bir ag istegi
    GEREKTIRMEZ."""
    symbols = get_scannable_symbols(exchange_info)
    return fetch_klines_bulk(symbols, "1m", MAX_WINDOW_MINUTES + 2)


def build_momentum_table(klines_map: dict, daily_tickers: list, window_size: str,
                          top_n: int = 20, direction: str = "gainers") -> pd.DataFrame:
    """Onceden cekilmis mum verisinden (klines_map) ve 24 saatlik toplu
    veriden (daily_tickers), secilen zaman penceresinde en cok yukselen
    (veya en cok dusen) coinlerin tablosunu olusturur. Hicbir network
    istegi YAPMAZ - saf bir hesaplama fonksiyonudur.

    direction: "gainers" (en cok yukselenler) veya "losers" (en cok
    dusenler).
    """
    window_minutes = int(_window_size_to_minutes(window_size))
    daily_map = {d["symbol"]: d for d in daily_tickers if isinstance(d, dict) and "symbol" in d}

    rows = []
    for symbol, df in klines_map.items():
        if df is None or len(df) < window_minutes + 1:
            continue

        try:
            open_price = float(df["close"].iloc[-(window_minutes + 1)])
            last_price = float(df["close"].iloc[-1])
            window_volume = float(df["volume"].iloc[-window_minutes:].sum())
        except (IndexError, ValueError, TypeError):
            continue
        if open_price <= 0:
            continue

        change_pct = (last_price - open_price) / open_price * 100

        vol_ratio = None
        d = daily_map.get(symbol)
        if d:
            try:
                daily_volume = float(d.get("volume", 0) or 0)
                expected_share = daily_volume * (window_minutes / (24 * 60))
                if expected_share > 0:
                    vol_ratio = window_volume / expected_share
            except (TypeError, ValueError):
                pass

        rows.append({
            "Sembol": symbol,
            "Fiyat": last_price,
            "Değişim (%)": change_pct,
            "Pencere Hacmi": window_volume,
            "Hacim Oranı": vol_ratio,
        })

    df_result = pd.DataFrame(rows)
    if df_result.empty:
        return df_result

    ascending = direction == "losers"
    df_result = df_result.sort_values("Değişim (%)", ascending=ascending).head(top_n).reset_index(drop=True)
    return df_result
