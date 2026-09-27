"""Fiyat grafigi olusturma: mum grafik + hareketli ortalamalar + hacim + MACD + RSI."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_price_chart(df, symbol: str):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        row_heights=[0.45, 0.15, 0.20, 0.20],
        vertical_spacing=0.03,
        subplot_titles=(f"{symbol} Fiyat", "Hacim", "MACD", "RSI"),
    )

    fig.add_trace(go.Candlestick(
        x=df["open_time"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="Fiyat",
        increasing_line_color="#3fb950", decreasing_line_color="#f85149",
    ), row=1, col=1)

    ma_colors = {"SMA_20": "#58a6ff", "SMA_50": "#e3b341", "SMA_200": "#d2a8ff"}
    for col_name, color in ma_colors.items():
        if col_name in df.columns:
            fig.add_trace(go.Scatter(
                x=df["open_time"], y=df[col_name], name=col_name.replace("_", " "),
                line=dict(width=1.2, color=color),
            ), row=1, col=1)

    volume_colors = ["#3fb950" if c >= o else "#f85149" for o, c in zip(df["open"], df["close"])]
    fig.add_trace(go.Bar(
        x=df["open_time"], y=df["volume"], name="Hacim", marker_color=volume_colors,
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df["open_time"], y=df["MACD"], name="MACD", line=dict(color="#58a6ff", width=1.2),
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=df["open_time"], y=df["MACD_signal"], name="Sinyal", line=dict(color="#e3b341", width=1.2),
    ), row=3, col=1)
    macd_colors = ["#3fb950" if v >= 0 else "#f85149" for v in df["MACD_hist"]]
    fig.add_trace(go.Bar(
        x=df["open_time"], y=df["MACD_hist"], name="Histogram", marker_color=macd_colors,
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df["open_time"], y=df["RSI"], name="RSI", line=dict(color="#d2a8ff", width=1.2),
    ), row=4, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#f85149", row=4, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#3fb950", row=4, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
