"""
Haber toplama ve duyarlilik (sentiment) analizi.

Varsayilan yontem: basit anahtar kelime eslestirmesine dayali sezgisel bir
skorlamadir (gercek bir NLP/AI modeli DEGILDIR). config.USE_LLM_SENTIMENT
True yapilip bir ANTHROPIC_API_KEY tanimlanirsa, basliklar opsiyonel olarak
Claude API'si ile degerlendirilir ve daha nuansli bir skor uretilir.
"""
import feedparser

import config


def fetch_news_headlines(feed_urls: list, max_items_per_feed: int = 10) -> list:
    """Verilen RSS adreslerinden haber basliklarini toplar. Bir feed
    alinamazsa sessizce atlanir, digerlerine devam edilir."""
    headlines = []
    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            source_name = url
            if hasattr(parsed, "feed") and parsed.feed.get("title"):
                source_name = parsed.feed.get("title")
            for entry in parsed.entries[:max_items_per_feed]:
                title = entry.get("title", "").strip()
                if not title:
                    continue
                headlines.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": source_name,
                })
        except Exception:
            continue
    return headlines


def keyword_sentiment_score(text: str) -> float:
    """-1.0 (cok negatif) ile +1.0 (cok pozitif) arasinda basit bir skor.
    Anahtar kelime sayimina dayanir; gercek bir dogal dil anlama yontemi
    DEGILDIR - kaba bir sezgiseldir."""
    text_lower = text.lower()
    bullish_hits = sum(1 for kw in config.BULLISH_KEYWORDS if kw in text_lower)
    bearish_hits = sum(1 for kw in config.BEARISH_KEYWORDS if kw in text_lower)
    total = bullish_hits + bearish_hits
    if total == 0:
        return 0.0
    return (bullish_hits - bearish_hits) / total


def llm_sentiment_score(headline: str):
    """Opsiyonel: Claude API ile daha nuansli bir duyarlilik skoru uretir.
    API anahtari yoksa veya bir hata olusursa None dondurur - bu durumda
    cagiran kod otomatik olarak anahtar kelime yontemine geri doner."""
    if not config.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": (
                    "Su kripto/finans haber basligini SADECE bir ondalik "
                    "sayi ile degerlendir: -1.0 (cok negatif/dususe isaret) "
                    "ile +1.0 (cok pozitif/yukselise isaret) arasinda. "
                    "Baska hicbir aciklama veya metin ekleme, sadece sayiyi "
                    "yaz.\n\n"
                    f"Baslik: {headline}"
                ),
            }],
        )
        value = float(message.content[0].text.strip())
        return max(-1.0, min(1.0, value))
    except Exception:
        return None


def compute_news_sentiment(headlines: list):
    """Verilen haber listesinden 0-100 arasi genel duyarlilik skoru ve
    her basligin etiketlendigi (Pozitif/Negatif/Notr) bir liste dondurur.

    Donus: (overall_score: float, annotated_headlines: list)
    """
    if not headlines:
        return 50.0, []

    annotated = []
    scores = []
    for item in headlines:
        raw_score = keyword_sentiment_score(item["title"])
        if config.USE_LLM_SENTIMENT:
            llm_score = llm_sentiment_score(item["title"])
            if llm_score is not None:
                raw_score = llm_score
        scores.append(raw_score)

        if raw_score > 0.15:
            label = "Pozitif"
        elif raw_score < -0.15:
            label = "Negatif"
        else:
            label = "Nötr"

        annotated.append({**item, "sentiment_score": raw_score, "sentiment_label": label})

    avg_score = sum(scores) / len(scores)
    scaled = 50 + avg_score * 50
    scaled = max(0.0, min(100.0, scaled))
    return scaled, annotated
