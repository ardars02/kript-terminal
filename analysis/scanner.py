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
from data.binance_client import (
    fetch_exchange_info,
    fetch_rolling_tickers,
    fetch_all_tickers_24hr,
)


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


def build_momentum_table(exchange_info: dict, window_size: str,
                          top_n: int = 20, direction: str = "gainers") -> pd.DataFrame:
    """Secilen zaman penceresinde en cok yukselen (veya en cok dusen)
    coinlerin tablosunu olusturur.

    direction: "gainers" (en cok yukselenler) veya "losers" (en cok
    dusenler).
    """
    symbols = get_scannable_symbols(exchange_info)

    rolling = fetch_rolling_tickers(symbols, window_size)
    daily = fetch_all_tickers_24hr()
    daily_map = {d["symbol"]: d for d in daily if isinstance(d, dict) and "symbol" in d}

    window_minutes = _window_size_to_minutes(window_size)

    rows = []
    for t in rolling:
        symbol = t.get("symbol")
        if not symbol:
            continue
        try:
            open_price = float(t.get("openPrice", 0) or 0)
            last_price = float(t.get("lastPrice", 0) or 0)
            window_volume = float(t.get("volume", 0) or 0)
        except (TypeError, ValueError):
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

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    ascending = direction == "losers"
    df = df.sort_values("Değişim (%)", ascending=ascending).head(top_n).reset_index(drop=True)
    return df
