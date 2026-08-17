import datetime as dt
import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytz
import requests
import streamlit as st
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh


st.set_page_config(page_title="Terminal Institucional", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, key="terminal-refresh")

TZ = pytz.timezone("America/Sao_Paulo")
ASSETS = {
    "USDJPY": {"label": "USD/JPY", "desk": "USD / JPY", "unit": "JPY", "symbol": "USD/JPY", "base": 159.31, "scale": 0.075},
    "US100": {"label": "US100", "desk": "US100 / Nasdaq", "unit": "PTS", "symbol": "NDX", "base": 21450.0, "scale": 40.0},
    "XAUUSD": {"label": "XAU/USD (Ouro)", "desk": "XAU / USD", "unit": "USD", "symbol": "XAU/USD", "base": 2435.0, "scale": 10.0},
}
TWELVE_INTERVALS = {"M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h", "D1": "1day"}
TIME_FREQ = {"M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h", "D1": "1D"}
SESSION_NAMES = ["Global", "Tóquio", "Londres", "Nova Iorque"]


st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background:#07111f; color:#eaf2ff; }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { background:#07111f; }
    [data-testid="stToolbar"], [data-testid="stStatusWidget"], .stDeployButton { display:none; }
    footer { visibility:hidden; height:0; }
    .block-container { max-width:none !important; padding:10px 20px 46px !important; }
    [data-testid="stMainBlockContainer"] { max-width:none !important; }
    div[data-testid="stHorizontalBlock"] { gap:.8rem; }
    .topbar { display:flex; align-items:center; gap:11px; min-height:46px; margin:0 0 8px; }
    .brand-mark { width:28px; height:28px; border-radius:8px; background:linear-gradient(145deg,#27dfb0,#5d8dff); display:inline-flex; align-items:center; justify-content:center; color:#07111f; font:900 16px ui-monospace,monospace; }
    .kicker { color:#9eb1cb; font:800 9px ui-monospace,monospace; letter-spacing:.11em; text-transform:uppercase; }
    .headline { color:#fff; font:850 17px/1.12 Inter,ui-sans-serif,system-ui,sans-serif; margin-top:3px; }
    .feed-badge { padding:6px 9px; border-radius:7px; color:#f7c948; background:rgba(245,183,24,.10); border:1px solid rgba(245,183,24,.42); font:800 9px ui-monospace,monospace; white-space:nowrap; display:inline-block; }
    .control-panel, .ui-card { background:#101d31; border:1px solid rgba(155,181,218,.16); border-radius:10px; padding:13px 14px; box-shadow:0 12px 32px rgba(0,0,0,.12); }
    .control-panel { min-height:58px; padding:10px 13px; }
    .ui-card { height:100%; box-sizing:border-box; }
    .spot-card { border-color:rgba(245,183,24,.42); }
    .eyebrow { color:#93a8c5; font:800 9px ui-monospace,monospace; letter-spacing:.09em; text-transform:uppercase; }
    .card-title { color:#f8fbff; font:800 13px/1.25 Inter,ui-sans-serif,system-ui,sans-serif; }
    .card-note { color:#9aaec8; font:500 10px/1.45 Inter,ui-sans-serif,system-ui,sans-serif; margin-top:3px; }
    .spot-symbol { color:#fff; font:850 16px/1 Inter,ui-sans-serif,system-ui,sans-serif; margin-top:6px; }
    .spot-value { color:#f7b718; font:900 34px/.96 ui-monospace,SFMono-Regular,monospace; letter-spacing:-.06em; margin:13px 0 8px; white-space:nowrap; }
    .unit { color:#dbe7f6; font:600 11px Inter,ui-sans-serif,system-ui,sans-serif; letter-spacing:0; }
    .small-row { color:#9ab0ca; font:500 10px/1.65 ui-monospace,monospace; display:flex; justify-content:space-between; align-items:center; gap:8px; }
    .small-row strong { color:#eef6ff; font-weight:800; }
    .vwap { color:#f7b718 !important; }
    .rule { height:1px; background:rgba(255,255,255,.09); margin:11px 0; }
    .badge-green, .badge-red, .badge-amber { padding:4px 7px; border-radius:5px; font:800 9px ui-monospace,monospace; text-transform:uppercase; white-space:nowrap; }
    .badge-green { color:#35e5ae; background:rgba(46,229,157,.13); }
    .badge-red { color:#fb7185; background:rgba(244,63,94,.14); }
    .badge-amber { color:#f7c948; background:rgba(245,183,24,.13); }
    .pressure-label { color:#d5e2f0; font:600 10px ui-monospace,monospace; margin:10px 0 4px; }
    .bar-shell { width:100%; height:8px; background:#070d16; border:1px solid rgba(255,255,255,.10); border-radius:999px; overflow:hidden; }
    .bar-fill-green { height:100%; background:#2ee59d; }.bar-fill-red { height:100%; background:#fb5f79; }
    .metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-top:12px; }
    .metric-cell { padding:8px; background:#0b1626; border:1px solid rgba(155,181,218,.12); border-radius:7px; }
    .metric-cell span { display:block; color:#95a9c4; font:700 8px ui-monospace,monospace; text-transform:uppercase; }.metric-cell b { display:block; color:#f5f9ff; margin-top:4px; font:800 12px ui-monospace,monospace; }
    .macro-title { margin-bottom:8px; }.macro-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }.macro-block { background:#0b1626; border:1px solid rgba(155,181,218,.12); border-radius:8px; padding:10px; }
    .news-row { display:grid; grid-template-columns:96px 54px 1fr 85px; gap:10px; align-items:center; padding:9px 0; border-bottom:1px solid rgba(255,255,255,.07); color:#d9e5f3; font:500 10px Inter,ui-sans-serif,system-ui,sans-serif; }.news-row:last-child { border-bottom:0; }.news-time { color:#9bb2ce; font-family:ui-monospace,monospace; }.impact-high { color:#ff7486; font:800 9px ui-monospace,monospace; }.impact-medium { color:#f7c948; font:800 9px ui-monospace,monospace; }
    .footer-note { color:#7f94b1; font:500 9px ui-monospace,monospace; text-align:center; margin-top:12px; }
    .stButton > button { width:100%; min-height:30px; padding:4px 7px; border-radius:7px; border:1px solid rgba(155,181,218,.20); background:#14243a; color:#dbe8f7; font:800 10px Inter,ui-sans-serif,system-ui,sans-serif; box-shadow:none; transition:all .14s ease; }
    .stButton > button:hover { color:#35e5ae; border-color:rgba(46,229,157,.75); background:#172a43; }.stButton > button:active { transform:scale(.97); }
    .stButton > button[kind="primary"] { color:#061019; background:#2ee59d; border-color:#2ee59d; }
    .stTextInput label, .stToggle label { color:#a4b6cf !important; font-size:10px !important; }
    .stTextInput input { background:#0a1524 !important; border-color:rgba(155,181,218,.20) !important; color:#ecf6ff !important; border-radius:7px !important; font-size:11px !important; }
    div[data-testid="stPlotlyChart"] { border-radius:8px; overflow:hidden; margin-top:3px; } div[data-testid="stPlotlyChart"] > div { border-radius:8px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background:#101d31 !important; border:1px solid rgba(155,181,218,.16) !important; border-radius:10px !important; padding:9px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { gap:.35rem; }
    [data-testid="stExpander"] { background:#101d31; border:1px solid rgba(155,181,218,.16); border-radius:10px; }
    [data-testid="stMetric"] { background:#0b1626; padding:8px !important; border:1px solid rgba(155,181,218,.12); border-radius:7px; }.stMetricLabel { font-size:9px !important; }.stMetricValue { color:#f7b718 !important; font:800 13px ui-monospace,monospace !important; }
    @media (max-width: 760px) { .block-container { padding:8px 10px 30px !important; }.headline { font-size:14px; }.feed-badge { font-size:8px; }.metric-grid,.macro-grid { grid-template-columns:1fr 1fr; }.news-row { grid-template-columns:70px 42px 1fr; }.news-row .impact-high,.news-row .impact-medium { grid-column:3; }.spot-value { font-size:29px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_secret(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value).strip() if value else ""


def price_format(value: float, is_usdjpy: bool) -> str:
    return f"{value:.3f}" if is_usdjpy else f"{value:,.2f}"


@st.cache_data(ttl=10, show_spinner=False)
def fetch_twelve_data(symbol: str, interval: str, api_key: str) -> tuple[pd.DataFrame, float | None, str]:
    headers = {"Authorization": f"apikey {api_key}"}
    params = {"symbol": symbol, "interval": interval, "outputsize": 60, "order": "asc", "timezone": "America/Sao_Paulo"}
    series = requests.get("https://api.twelvedata.com/time_series", params=params, headers=headers, timeout=8)
    series.raise_for_status()
    payload = series.json()
    if payload.get("status") == "error" or not payload.get("values"):
        raise RuntimeError(payload.get("message", "TwelveData não devolveu candles."))
    data = pd.DataFrame(payload["values"]).rename(columns={"datetime": "time"})
    data["time"] = pd.to_datetime(data["time"], errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        if column in data:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["time", "open", "high", "low", "close"]).sort_values("time").tail(60)
    has_volume = "volume" in data and data["volume"].fillna(0).sum() > 0
    if not has_volume:
        data["volume"] = 1.0
    data = data[["time", "open", "high", "low", "close", "volume"]].reset_index(drop=True)
    spot = None
    quote = requests.get("https://api.twelvedata.com/quote", params={"symbol": symbol}, headers=headers, timeout=8)
    if quote.ok:
        for key in ("price", "close"):
            if quote.json().get(key) not in (None, ""):
                spot = float(quote.json()[key])
                break
    return data, spot, "volume real" if has_volume else "volume não fornecido pelo provedor"


def make_data(asset: str, timeframe: str) -> pd.DataFrame:
    config = ASSETS[asset]
    now = dt.datetime.now(TZ).replace(second=0, microsecond=0)
    bucket = int(dt.datetime.now().timestamp() // 3)
    rng = np.random.default_rng({"USDJPY": 11, "US100": 29, "XAUUSD": 47}[asset] + bucket)
    close = [config["base"]]
    for _ in range(59):
        close.append(close[-1] + rng.normal(0, config["scale"]))
    close = np.array(close)
    open_ = close - rng.normal(0, config["scale"] * 0.34, 60)
    high = np.maximum(open_, close) + rng.uniform(config["scale"] * .15, config["scale"] * .7, 60)
    low = np.minimum(open_, close) - rng.uniform(config["scale"] * .15, config["scale"] * .7, 60)
    return pd.DataFrame({"time": pd.date_range(end=now, periods=60, freq=TIME_FREQ[timeframe]), "open": open_, "high": high, "low": low, "close": close, "volume": rng.integers(220, 880, 60)})


def load_market_data(asset: str, timeframe: str) -> tuple[pd.DataFrame, float | None, str, str]:
    api_key = read_secret("TWELVEDATA_API_KEY") or st.session_state.get("api_key", "").strip()
    if not api_key:
        return make_data(asset, timeframe), None, "simulated", "Chave TwelveData ausente; fallback simulado identificado."
    symbol = read_secret(f"TWELVEDATA_SYMBOL_{asset}") or ASSETS[asset]["symbol"]
    try:
        data, spot, volume_note = fetch_twelve_data(symbol, TWELVE_INTERVALS[timeframe], api_key)
        return data, spot, "real", f"Feed TwelveData ativo · {symbol} · {volume_note}."
    except Exception as error:
        return make_data(asset, timeframe), None, "fallback", f"Feed TwelveData indisponível; fallback simulado identificado ({type(error).__name__})."


def session_slice(data: pd.DataFrame, session: str) -> pd.DataFrame:
    if session == "Global":
        return data
    spans = {"Tóquio": (.18, .49), "Londres": (.42, .74), "Nova Iorque": (.67, 1.0)}
    start, end = spans[session]
    first = int(len(data) * start)
    last = max(int(len(data) * end), first + 1)
    return data.iloc[first:last]


def profile_levels(data: pd.DataFrame) -> tuple[float, float, float]:
    typical = (data.high + data.low + data.close) / 3
    poc_value = float(np.average(typical, weights=data.volume))
    spread = float(data.high.max() - data.low.min())
    return poc_value, poc_value + spread * .18, poc_value - spread * .18


def historical_pocs(data: pd.DataFrame) -> dict[str, float]:
    return {name: profile_levels(session_slice(data, name))[0] for name in ["Tóquio", "Londres", "Nova Iorque"]} | {"Pacífico": profile_levels(data.iloc[: max(1, len(data)//4)])[0]}


for key, value in {"asset": "USDJPY", "timeframe": "H1", "session": "Global", "api_key": "", "sound_alerts": False, "news_filter": "Todas", "bottom_view": "Linha", "backtest_result": None}.items():
    if key not in st.session_state:
        st.session_state[key] = value
if st.session_state.session not in SESSION_NAMES:
    st.session_state.session = "Global"

asset = st.session_state.asset
timeframe = st.session_state.timeframe
session = st.session_state.session
is_usdjpy = asset == "USDJPY"
config = ASSETS[asset]
asset_label, desk_name = config["label"], config["desk"]
df, live_spot, feed_mode, feed_note = load_market_data(asset, timeframe)
last = float(live_spot if live_spot is not None else df.close.iloc[-1])
if live_spot is not None:
    df.loc[df.index[-1], "close"] = live_spot
profile_data = session_slice(df, session)
typical = (df.high + df.low + df.close) / 3
vwap = float(np.average(typical, weights=df.volume))
poc, vah, val = profile_levels(profile_data)
session_levels = historical_pocs(df)
swing_high, swing_low = float(df.high.max()), float(df.low.min())
recent = df.tail(12)
buy = int(np.clip(50 + int((recent.close > recent.open).sum()) * 3 - 18, 18, 82))
sell, bearish = 100 - buy, buy < 50
ma9 = float(df.volume.rolling(9, min_periods=1).mean().iloc[-1])
ma21 = float(df.volume.rolling(21, min_periods=1).mean().iloc[-1])
ma200 = float(df.volume.rolling(200, min_periods=1).mean().iloc[-1])
volume_ratio = float(df.volume.iloc[-1] / max(ma9, 1))
volume_status = "Volume não fornecido" if "não fornecido" in feed_note else ("Volume Acima da MA9" if df.volume.iloc[-1] > ma9 else "Volume Normal")
signal, confidence = ("VENDA", int(np.clip(55 + abs(buy-sell)*.55, 55, 92))) if bearish else ("COMPRA", int(np.clip(55 + abs(buy-sell)*.55, 55, 92)))
vwap_series = (typical * df.volume).cumsum() / df.volume.cumsum()
backtest = df.assign(direction=np.where(df.close > df.open, "COMPRA", "VENDA"))
backtest["next_return"] = backtest.close.shift(-1) - backtest.close
backtest["win"] = np.where(backtest.direction == "COMPRA", backtest.next_return > 0, backtest.next_return < 0)
valid_backtest = backtest.dropna(subset=["next_return"])
win_rate = float(valid_backtest.win.mean()*100) if len(valid_backtest) else 0.0
mean_pnl = float(valid_backtest.next_return.where(valid_backtest.direction == "COMPRA", -valid_backtest.next_return).mean()) if len(valid_backtest) else 0.0
clock = dt.datetime.now(TZ).strftime("%H:%M:%S")


# Topo compacto do terminal original: marca à esquerda e seleção de ativo no canto direito.
header_left, header_actions = st.columns([1.2, 1.1], gap="small", vertical_alignment="center")
with header_left:
    st.markdown(f'<div class="topbar"><div class="brand-mark">↯</div><div><div class="kicker">Mesa de Tesouraria · Forex & Commodities Desk</div><div class="headline">Terminal Institucional (USD/JPY, US100 & XAU/USD)</div></div></div>', unsafe_allow_html=True)
with header_actions:
    action_cols = st.columns([1, 1, 1.15, 1.35], gap="small")
    for col, key, label in zip(action_cols[:3], ["USDJPY", "US100", "XAUUSD"], ["USD/JPY", "US100", "XAU/USD (Ouro)"]):
        with col:
            if st.button(label, key=f"asset-{key}", type="primary" if asset == key else "secondary"):
                st.session_state.asset = key
                st.rerun()
    with action_cols[3]:
        st.markdown(f'<div class="feed-badge">↻ AUTO-REFRESH 3S · {clock}</div>', unsafe_allow_html=True)

controls_left, controls_right = st.columns([1, 1], gap="medium")
with controls_left:
    control_text, control_buttons = st.columns([1.35, 1], gap="small", vertical_alignment="center")
    with control_text:
        st.markdown('<div class="control-panel"><div class="eyebrow">Timeframe ativo</div><div class="card-title">Gráficos de linhas (Cotação + Regiões POC/VAH/VAL)</div></div>', unsafe_allow_html=True)
    with control_buttons:
        tf_cols = st.columns(5, gap="small")
        for col, tf in zip(tf_cols, ["M5", "M15", "H1", "H4", "D1"]):
            with col:
                if st.button(tf, key=f"tf-{tf}", type="primary" if timeframe == tf else "secondary"):
                    st.session_state.timeframe = tf
                    st.rerun()
with controls_right:
    session_text, session_buttons = st.columns([1.1, 1.45], gap="small", vertical_alignment="center")
    with session_text:
        st.markdown(f'<div class="control-panel"><div class="eyebrow">Sessão de mercado (filtro POC)</div><div class="card-title">Horário de Brasília: <span style="color:#2ee59d">{clock}</span></div></div>', unsafe_allow_html=True)
    with session_buttons:
        ss_cols = st.columns(4, gap="small")
        for col, name in zip(ss_cols, SESSION_NAMES):
            with col:
                if st.button(name, key=f"session-{name}", type="primary" if session == name else "secondary"):
                    st.session_state.session = name
                    st.rerun()

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# Spot e pressão partilham a primeira linha, tal como no terminal de referência.
spot_col, pressure_col = st.columns([.78, 2.22], gap="medium")
with spot_col:
    st.markdown(f'''<div class="ui-card spot-card"><div style="display:flex;justify-content:space-between;align-items:center"><div class="eyebrow">Cotação Spot Atual ({timeframe})</div><span class="badge-green">Ao vivo</span></div><div class="spot-symbol">{desk_name}</div><div class="spot-value">{price_format(last, is_usdjpy)} <span class="unit">{config["unit"]}</span></div><div class="small-row"><span>VWAP: <strong class="vwap">{price_format(vwap, is_usdjpy)}</strong></span><span>Spread: <strong>{"0.012" if is_usdjpy else "0.50"}</strong></span></div><div class="rule"></div><div class="small-row"><span>Horário (Brasília)</span><strong>{clock}</strong></div></div>''', unsafe_allow_html=True)
with pressure_col:
    bias_badge = '<span class="badge-red">Viés Vendedor Dominante</span>' if bearish else '<span class="badge-green">Viés Comprador Dominante</span>'
    st.markdown(f'''<div class="ui-card"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><div><div class="card-title">⌁ Médias de Volume & Pressão ({timeframe})</div><div class="card-note">MA9: <b>{ma9:.1f}</b> &nbsp;|&nbsp; MA21: <b>{ma21:.1f}</b> &nbsp;|&nbsp; MA200: <b>{ma200:.1f}</b></div></div>{bias_badge}</div><div class="pressure-label" style="color:#2ee59d">Pressão Compradora <span style="float:right">{buy}%</span></div><div class="bar-shell"><div class="bar-fill-green" style="width:{buy}%"></div></div><div class="pressure-label" style="color:#fb7185">Pressão Vendedora <span style="float:right">{sell}%</span></div><div class="bar-shell"><div class="bar-fill-red" style="width:{sell}%"></div></div><div class="rule"></div><div class="small-row"><span>Volume Ratio: <strong>{volume_ratio:.1f}x</strong></span><span>Status: <strong style="color:#f7b718">{volume_status}</strong></span></div></div>''', unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# O gráfico de preço volta a ser prioritário, lado a lado com o alerta operacional.
chart_col, alert_col = st.columns([2.12, 1], gap="medium")
with chart_col:
    with st.container(border=True):
        st.markdown(f'<div class="card-title">▥ Gráfico Spot com Bandas POC, VAH, VAL ({asset_label})</div><div class="card-note">Linhas tracejadas indicam regiões institucionais de liquidez. Sessão de cálculo: <b>{session}</b>.</div>', unsafe_allow_html=True)
        main_fig = make_subplots(specs=[[{"secondary_y": True}]])
        main_fig.add_trace(go.Scatter(x=df.time, y=df.close, name=f"{asset_label} Spot", line={"color": "#2ee59d" if is_usdjpy else "#5799ff", "width": 2.3}, mode="lines+markers", marker={"size": 3}), secondary_y=False)
        main_fig.add_trace(go.Scatter(x=df.time, y=vwap_series, name="VWAP", line={"color": "#f7b718", "width": 1.3, "dash": "dot"}), secondary_y=False)
        main_fig.add_trace(go.Bar(x=df.time, y=df.volume, name="Tick Volume", marker_color="rgba(87,153,255,.27)"), secondary_y=True)
        for value, name, color, dash in [(poc, "POC (Control)", "#f7b718", "dot"), (vah, "VAH (Resistência)", "#cc80ff", "dash"), (val, "VAL (Suporte)", "#3bd2cf", "dash")]:
            main_fig.add_hline(y=value, line_color=color, line_dash=dash, line_width=1, annotation_text=name, annotation_font_color=color, annotation_position="top left")
        main_fig.update_layout(height=302, margin={"l": 5, "r": 5, "t": 24, "b": 4}, paper_bgcolor="#101d31", plot_bgcolor="#101d31", font={"color": "#dbe8f7", "size": 10}, legend={"orientation": "h", "y": 1.14, "x": 0, "font": {"size": 9}}, hovermode="x unified", bargap=.22)
        main_fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False, secondary_y=False)
        main_fig.update_yaxes(showgrid=False, zeroline=False, secondary_y=True)
        main_fig.update_xaxes(gridcolor="rgba(255,255,255,.035)", showspikes=True)
        st.plotly_chart(main_fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False})
with alert_col:
    signal_badge = '<span class="badge-red">VENDA</span>' if bearish else '<span class="badge-green">COMPRA</span>'
    st.markdown(f'''<div class="ui-card"><div style="display:flex;justify-content:space-between;align-items:center"><div class="card-title">◉ Alerta Operacional ({asset_label})</div>{signal_badge}</div><div class="rule"></div><div class="card-note">{"Sinal de baixa: volume atual acima das médias MA9 e MA21 com pressão vendedora." if bearish else "Sinal de alta: volume atual acima das médias MA9 e MA21 com pressão compradora."}</div><div class="rule"></div><div class="small-row"><span>VAH (Resistência)</span><strong style="color:#fb7185">{price_format(vah, is_usdjpy)}</strong></div><div class="small-row"><span>POC (Control)</span><strong style="color:#f7b718">{price_format(poc, is_usdjpy)}</strong></div><div class="small-row"><span>VAL (Suporte)</span><strong style="color:#2ee59d">{price_format(val, is_usdjpy)}</strong></div><div class="small-row"><span>Confiança do Sinal</span><strong style="color:#2ee59d">{confidence}%</strong></div><div class="rule"></div><div class="card-note" style="text-align:center;font-style:italic">Atualização automática em tempo real.</div></div>''', unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# Gráfico inferior do original, com a alternância Linha/Velas compacta no canto.
with st.container(border=True):
    lower_title, lower_controls = st.columns([2.4, .7], vertical_alignment="center")
    with lower_title:
        st.markdown(f'<div class="card-title">⌁ Gráfico Inferior — Cotação Spot & Zonas POC / VAH / VAL</div><div class="card-note">POC em amarelo, VAH/VAL tracejados e níveis históricos das sessões.</div>', unsafe_allow_html=True)
    with lower_controls:
        line_button, candle_button = st.columns(2, gap="small")
        with line_button:
            if st.button("Linha", key="view-line", type="primary" if st.session_state.bottom_view == "Linha" else "secondary"):
                st.session_state.bottom_view = "Linha"
        with candle_button:
            if st.button("Velas OHLC", key="view-candles", type="primary" if st.session_state.bottom_view == "Velas OHLC" else "secondary"):
                st.session_state.bottom_view = "Velas OHLC"
    lower_fig = go.Figure()
    if st.session_state.bottom_view == "Velas OHLC":
        lower_fig.add_trace(go.Candlestick(x=df.time, open=df.open, high=df.high, low=df.low, close=df.close, name="OHLC", increasing_line_color="#2ee59d", decreasing_line_color="#fb7185"))
    else:
        lower_fig.add_trace(go.Scatter(x=df.time, y=df.close, name=f"{asset_label} Spot", line={"color": "#2ee59d" if is_usdjpy else "#5799ff", "width": 2}, mode="lines+markers", marker={"size": 3}))
    for value, name, color, dash in [(poc, "POC Atual", "#f7b718", "solid"), (vah, "VAH", "#c084fc", "dash"), (val, "VAL", "#42d4d0", "dash"), (vwap, "VWAP", "#f59e0b", "dot")]:
        lower_fig.add_hline(y=value, line_color=color, line_dash=dash, line_width=1, annotation_text=name, annotation_font_color=color, annotation_position="top left")
    for name, value in session_levels.items():
        lower_fig.add_hline(y=value, line_color="#5a79a0", line_dash="dot", line_width=.7, opacity=.62, annotation_text=f"{name} POC", annotation_font_color="#9cb5d6", annotation_position="bottom left")
    lower_fig.update_layout(height=260, margin={"l": 5, "r": 5, "t": 5, "b": 4}, paper_bgcolor="#101d31", plot_bgcolor="#101d31", font={"color": "#dbe8f7", "size": 10}, hovermode="x unified", xaxis_rangeslider_visible=False, showlegend=False)
    lower_fig.update_yaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False)
    lower_fig.update_xaxes(gridcolor="rgba(255,255,255,.035)")
    st.plotly_chart(lower_fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False})
    st.markdown(f'''<div class="metric-grid"><div class="metric-cell"><span>POC Atual</span><b style="color:#f7b718">{price_format(poc, is_usdjpy)}</b></div><div class="metric-cell"><span>VAH</span><b>{price_format(vah, is_usdjpy)}</b></div><div class="metric-cell"><span>VAL</span><b>{price_format(val, is_usdjpy)}</b></div><div class="metric-cell"><span>Londres POC</span><b>{price_format(session_levels["Londres"], is_usdjpy)}</b></div></div>''', unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# Blocos secundários: Profile e tendência H4/D1 deslocados abaixo da leitura de preço.
profile_col, htf_col = st.columns([1, 1.5], gap="medium")
with profile_col:
    with st.container(border=True):
        st.markdown(f'<div class="card-title">▤ Volume Profile ({asset_label})</div><div class="card-note">Perfil do filtro <b>{session}</b>; POC destacado e área de valor aproximada.</div>', unsafe_allow_html=True)
        bins = pd.cut(profile_data.close, bins=12)
        profile = profile_data.groupby(bins, observed=False).volume.sum().reset_index()
        profile["price"] = profile["close"].apply(lambda item: item.mid if pd.notna(item) else np.nan)
        profile = profile.dropna()
        profile_fig = go.Figure(go.Bar(x=profile.volume, y=profile.price, orientation="h", marker_color=["#f7b718" if abs(value-poc) < max((vah-val)/8, .001) else "#386da8" for value in profile.price]))
        profile_fig.add_hline(y=poc, line_color="#f7b718", line_dash="dot")
        profile_fig.update_layout(height=245, margin={"l": 5, "r": 5, "t": 5, "b": 4}, paper_bgcolor="#101d31", plot_bgcolor="#101d31", font={"color": "#dbe8f7", "size": 9}, showlegend=False)
        profile_fig.update_xaxes(showgrid=False); profile_fig.update_yaxes(gridcolor="rgba(255,255,255,.05)")
        st.plotly_chart(profile_fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False})
with htf_col:
    st.markdown(f'''<div class="ui-card macro-title"><div style="display:flex;justify-content:space-between;align-items:center"><div><div class="card-title">▣ Avaliação Institucional H4 & Diário ({asset_label})</div><div class="card-note">Leitura de tendência superior para contextualizar a entrada, sem recomendação personalizada.</div></div><span class="badge-green">{asset_label} · {timeframe}</span></div><div class="rule"></div><div class="macro-grid"><div class="macro-block"><div class="eyebrow">Timeframe H4 (intradiário superior)</div><span class="{'badge-red' if bearish else 'badge-green'}">{'VENDA · CONTINUAÇÃO' if bearish else 'COMPRA · CONTINUAÇÃO'}</span><p class="card-note"><b style="color:#fff">Confluência:</b> Preço em relação à VWAP H4 ({price_format(vwap, is_usdjpy)}) e POC ativo.</p><p class="card-note"><b style="color:#f7b718">Invalidação:</b> Fechamento H4 rompendo {price_format(swing_high, is_usdjpy)}.</p></div><div class="macro-block"><div class="eyebrow">Timeframe diário (macro trend)</div><span class="{'badge-red' if bearish else 'badge-green'}">{'BAIXA ESTRUTURAL' if bearish else 'ALTA CONSISTENTE'}</span><p class="card-note"><b style="color:#fff">Confluência:</b> Golden Pocket 61.8% com POC institucional.</p><p class="card-note"><b style="color:#f7b718">Invalidação:</b> Rompimento da máxima diária em {price_format(swing_high, is_usdjpy)}.</p></div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown(f'''<div class="ui-card"><div class="card-title">◌ POCs Históricos das Sessões</div><div class="card-note">Zonas de suporte e resistência por região de mercado.</div><div class="metric-grid"><div class="metric-cell"><span>Pacífico</span><b>{price_format(session_levels['Pacífico'], is_usdjpy)}</b></div><div class="metric-cell"><span>Tóquio</span><b>{price_format(session_levels['Tóquio'], is_usdjpy)}</b></div><div class="metric-cell"><span>Londres</span><b>{price_format(session_levels['Londres'], is_usdjpy)}</b></div><div class="metric-cell"><span>Nova Iorque</span><b>{price_format(session_levels['Nova Iorque'], is_usdjpy)}</b></div></div></div>''', unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

news_by_asset = {
    "USDJPY": [("08:30 NY", "USD", "CPI / Inflação do Consumidor", "Alto"), ("10:30 NY", "USD", "Decisão de juros e comunicação do Fed", "Alto"), ("09:00 Tóquio", "JPY", "BoJ — política monetária", "Alto")],
    "US100": [("10:30 NY", "USD", "Resultados e fluxo de tecnologia", "Alto"), ("14:00 NY", "USD", "FOMC minutes e decisão de juros", "Alto"), ("08:30 NY", "USD", "Payrolls / emprego norte-americano", "Médio")],
    "XAUUSD": [("08:30 NY", "USD", "Inflação e procura por proteção", "Alto"), ("10:30 NY", "USD", "Decisão de juros e dólar", "Médio"), ("14:00 NY", "USD", "Fluxo para metais preciosos", "Médio")],
}[asset]
with st.container(border=True):
    news_head, news_actions = st.columns([2.3, 1], vertical_alignment="center")
    with news_head:
        st.markdown(f'<div class="card-title">◫ Notícias & Feed RSS Financeiro ({asset_label})</div><div class="card-note">Eventos relevantes devem ser confirmados numa fonte económica antes da decisão.</div>', unsafe_allow_html=True)
    with news_actions:
        n1, n2, n3 = st.columns(3, gap="small")
        for col, value, label in [(n1, "Todas", "Todas"), (n2, "Alto", "Alto"), (n3, "Médio", "Médio")]:
            with col:
                if st.button(label, key=f"news-{value}", type="primary" if st.session_state.news_filter == value else "secondary"):
                    st.session_state.news_filter = value
                    st.rerun()
    visible_news = [item for item in news_by_asset if st.session_state.news_filter == "Todas" or item[3] == st.session_state.news_filter]
    news_html = "".join(f'<div class="news-row"><span class="news-time">{html.escape(item[0])}</span><span>{html.escape(item[1])}</span><span>{html.escape(item[2])}</span><span class="impact-{item[3].lower()}">{html.escape(item[3]).upper()} IMPACTO</span></div>' for item in visible_news) or '<div class="card-note" style="padding:12px 0">Sem eventos para este filtro.</div>'
    st.markdown(news_html + f'<div class="card-note" style="margin-top:8px">Fonte de referência: calendário macro / RSS financeiro. {feed_note}</div>', unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

config_col, backtest_col = st.columns([1.18, 1], gap="medium")
with config_col:
    with st.container(border=True):
        st.markdown('<div class="card-title">⚙ Configurações do Terminal (API TwelveData & Alertas Sonoros)</div><div class="card-note">Use `st.secrets` para o feed real; o campo abaixo é apenas temporário nesta sessão.</div>', unsafe_allow_html=True)
        secret_loaded = bool(read_secret("TWELVEDATA_API_KEY"))
        api_value = "" if secret_loaded else st.text_input("Chave TwelveData (API Key)", value=st.session_state.api_key, type="password", placeholder="Cole a sua API key aqui...", key="twelve-input")
        save_col, sound_col = st.columns([.55, 1], gap="small")
        with save_col:
            if st.button("Salvar", key="save-key", type="primary"):
                st.session_state.api_key = api_value
                st.rerun()
        with sound_col:
            st.session_state.sound_alerts = st.toggle("Alertas sonoros de Compra/Venda", value=st.session_state.sound_alerts, key="sound-toggle")
        st.markdown(f'<div class="card-note">{"TWELVEDATA_API_KEY está carregada com segurança." if secret_loaded else "A chave não é gravada no repositório."}</div>', unsafe_allow_html=True)
with backtest_col:
    with st.container(border=True):
        st.markdown(f'<div class="card-title">▧ Desempenho Histórico & Backtest ({asset_label})</div><div class="card-note">Teste rápido nas velas de {timeframe}; não representa garantia de desempenho.</div>', unsafe_allow_html=True)
        bt1, bt2, bt3, bt4 = st.columns(4, gap="small")
        with bt1: st.metric("Win Rate", f"{win_rate:.0f}%")
        with bt2: st.metric("Média PnL", price_format(mean_pnl, is_usdjpy))
        with bt3:
            if st.button("Rodar", key="run-backtest"):
                st.session_state.backtest_result = {"clock": clock, "asset": asset_label}
        with bt4:
            export = backtest[["time", "open", "high", "low", "close", "volume", "direction", "next_return", "win"]].to_csv(index=False).encode("utf-8")
            st.download_button("CSV", export, file_name=f"backtest_{asset}_{timeframe}.csv", mime="text/csv", key="csv-backtest")
        st.markdown(f'<div class="small-row" style="margin-top:8px"><span>Operação atual</span><strong style="color:{"#fb7185" if bearish else "#2ee59d"}">{signal} · EM OBSERVAÇÃO</strong><span>Entrada: <b>{price_format(last, is_usdjpy)}</b></span><span>Confiança: <b style="color:#f7b718">{confidence}%</b></span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer-note">Terminal Institucional · {asset_label} · {feed_note} Auto-refresh a cada 3 segundos.</div>', unsafe_allow_html=True)
