"""
Binance Genel (Public) API istemcisi.

Yalnizca herkese acik piyasa verisi (market data) uc noktalarini kullanir;
API anahtari veya hesap erisimi GEREKTIRMEZ. Bu modulde emir verme/alma,
cuzdan erisimi gibi hicbir islev YOKTUR - sadece okuma amaclidir.
"""
import concurrent.futures

import pandas as pd
import requests

import config


class BinanceAPIError(Exception):
    """Binance API'den veri alinirken olusan hatalar icin ozel istisna."""
    pass


def _get(endpoint: str, params: dict):
    url = f"{config.BINANCE_BASE_URL}{endpoint}"
    response = None
    try:
        response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        detail = str(exc)
        if response is not None:
            try:
                detail = response.json().get("msg", detail)
            except Exception:
                pass
        raise BinanceAPIError(f"{endpoint}: {detail}") from exc
    except requests.exceptions.RequestException as exc:
        raise BinanceAPIError(f"{endpoint} adresine ulasilamadi: {exc}") from exc


def fetch_klines(symbol: str, interval: str, limit: int = 250):
    """Mum (candlestick) verisini ceker ve pandas DataFrame olarak dondurur.

    Sutunlar: open_time, open, high, low, close, volume, close_time
    """
    raw = _get("/api/v3/klines", {"symbol": symbol.upper(), "interval": interval, "limit": limit})

    if not isinstance(raw, list) or len(raw) == 0:
        raise BinanceAPIError(f"{symbol} icin mum verisi bos dondu.")

    columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore",
    ]
    df = pd.DataFrame(raw, columns=columns)

    numeric_cols = ["open", "high", "low", "close", "volume", "quote_asset_volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

    return df[["open_time", "open", "high", "low", "close", "volume", "close_time"]]


def fetch_ticker_24hr(symbol: str) -> dict:
    """24 saatlik fiyat/hacim degisim istatistiklerini dondurur."""
    data = _get("/api/v3/ticker/24hr", {"symbol": symbol.upper()})
    if not isinstance(data, dict):
        raise BinanceAPIError(f"{symbol} icin 24 saatlik veri beklenmeyen formatta dondu.")
    return data


def fetch_all_tickers_24hr() -> list:
    """TUM paritelerin 24 saatlik istatistiklerini TEK istekte ceker
    (sembol parametresi verilmezse Binance tum semboller icin veri doner).
    Hacim Tarayicisi (scanner) icin kullanilir."""
    data = _get("/api/v3/ticker/24hr", {})
    if not isinstance(data, list):
        raise BinanceAPIError("Toplu 24 saatlik veri beklenmeyen formatta dondu.")
    return data


def fetch_exchange_info() -> dict:
    """Borsada islem goren tum paritelerin listesini ve durumunu dondurur.
    Hangi paritelerin taranabilir oldugunu belirlemek icin kullanilir."""
    data = _get("/api/v3/exchangeInfo", {})
    if not isinstance(data, dict):
        raise BinanceAPIError("exchangeInfo beklenmeyen formatta dondu.")
    return data


def fetch_klines_bulk(symbols: list, interval: str, limit: int, max_workers: int = 20) -> dict:
    """Birden fazla sembol icin mum verisini ES ZAMANLI (concurrent) olarak
    ceker.

    NOT: Binance'in bazi aynalarinda / bazi agirliklarda (ozellikle
    data-api.binance.vision uzerinden) coklu-sembol JSON-array parametresi
    ("symbols=[...]") beklenmedik sekilde reddedilebiliyor ("Illegal
    characters found in parameter 'symbols'" hatasi). Bu yuzden burada,
    HER ZAMAN guvenilir calisan TEKIL sembol parametresi (`symbol=`)
    kullanilir; hiz kaybini onlemek icin cok sayida istek es zamanli
    calistirilir.

    Bir sembol icin istek basarisiz olursa o sembol sessizce atlanir,
    digerleri etkilenmez. Donus: {sembol: DataFrame}."""
    results = {}
    if not symbols:
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(fetch_klines, s, interval, limit): s for s in symbols
        }
        for future in concurrent.futures.as_completed(future_map):
            symbol = future_map[future]
            try:
                results[symbol] = future.result()
            except BinanceAPIError:
                continue
    return results
