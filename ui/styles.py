"""Ozel CSS: koyu tema (dark mode) kripto terminali gorunumu."""


def get_custom_css() -> str:
    return """
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .disclaimer-box {
        background-color: #2d2200;
        border-left: 4px solid #d4a017;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #f0c674;
        margin-bottom: 16px;
    }
    .score-box {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .score-box h1 { margin: 0; font-size: 2.6rem; }
    .score-box p { margin: 4px 0 0 0; font-weight: 600; }
    .score-green { background-color: #0d2818; border: 1px solid #2ea043; color: #3fb950; }
    .score-yellow { background-color: #2d2600; border: 1px solid #d4a017; color: #e3b341; }
    .score-red { background-color: #2d0d0d; border: 1px solid #da3633; color: #f85149; }
    .news-item {
        padding: 8px 0;
        border-bottom: 1px solid #21262d;
        font-size: 0.9rem;
    }
    .news-item a { color: #58a6ff; text-decoration: none; }
    .news-item a:hover { text-decoration: underline; }
    .news-source { color: #8b949e; font-size: 0.8rem; }
    .tag-green, .tag-red, .tag-gray {
        color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; margin-right: 6px;
    }
    .tag-green { background-color: #2ea043; }
    .tag-red { background-color: #da3633; }
    .tag-gray { background-color: #6e7681; }
    </style>
    """
