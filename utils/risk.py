"""
Sermaye risk yonetimi hesaplamalari.

NOT: Bu modul herhangi bir kaldirac veya alim/satim ONERISI SUNMAZ; hicbir
"skor"a veya "guven duzeyine" bagli degildir. Yalnizca kullanicinin KENDI
girdigi risk parametrelerine (bakiye, risk yuzdesi, stop-loss mesafesi)
dayali standart, seffaf pozisyon buyuklugu matematigini hesaplar. Bu,
profesyonel risk yonetiminde yaygin kullanilan "hesap basina sabit risk
yuzdesi" yontemidir.
"""
import config


def compute_position_size(account_balance: float, risk_percent: float,
                           stop_loss_percent: float, current_price: float = None) -> dict:
    """
    risk_amount_usd   : Bu islemde riske atilan (kaybedilebilecek) tutar
    position_size_usd : Stop-loss'a bu mesafeyle ulasildiginda risk_amount_usd
                         kadar kayip verecek pozisyon buyuklugu
    """
    account_balance = max(0.0, account_balance)
    risk_percent = max(0.0, risk_percent)
    stop_loss_percent = max(0.0, stop_loss_percent)

    risk_amount_usd = account_balance * (risk_percent / 100)

    if stop_loss_percent <= 0:
        position_size_usd = 0.0
    else:
        position_size_usd = risk_amount_usd / (stop_loss_percent / 100)

    result = {
        "risk_amount_usd": risk_amount_usd,
        "position_size_usd": position_size_usd,
        "max_loss_usd": risk_amount_usd,
    }

    if current_price and current_price > 0:
        result["position_size_units"] = position_size_usd / current_price

    return result


def classify_volatility(atr_pct) -> str:
    """ATR yuzdesine gore basit bir oynaklik etiketi dondurur."""
    if atr_pct is None:
        return "Bilinmiyor"
    if atr_pct < config.VOLATILITY_LOW_THRESHOLD:
        return "Düşük"
    if atr_pct > config.VOLATILITY_HIGH_THRESHOLD:
        return "Yüksek"
    return "Orta"
