import datetime as dt
import html
import json
import math
import os
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots


if __name__ == "__main__":
    st.set_page_config(page_title="Terminal Institucional", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

TZ = ZoneInfo("America/Sao_Paulo")
ASSETS = {
    "USDJPY": {"label": "USD/JPY", "desk": "USD / JPY", "unit": "JPY", "symbol": "USD/JPY", "google_symbol": "USD-JPY", "google_name": "USD / JPY", "base": 159.31, "scale": 0.075},
    "US100": {"label": "US100", "desk": "US100 / Nasdaq", "unit": "PTS", "symbol": "NDX", "google_symbol": "NDX:INDEXNASDAQ", "google_name": "Nasdaq-100", "base": 29490.96, "scale": 55.0},
    "XAUUSD": {"label": "XAU/USD (Ouro spot)", "desk": "XAU / USD · Spot", "unit": "USD/oz", "symbol": "XAU/USD", "google_symbol": "GCW00:COMEX", "google_name": "Gold COMEX (futuro; não é XAU/USD spot)", "base": 4351.90, "scale": 35.0},
    "BTCUSD": {"label": "BTC/USD (Bitcoin)", "desk": "BTC / USD", "unit": "USD", "symbol": "BTC/USD", "google_symbol": "BTC-USD", "google_name": "Bitcoin", "base": 80542.94, "scale": 850.0},
    "MINIWIN": {"label": "Mini-Índice (WIN)", "desk": "WIN / Ibovespa", "unit": "PTS", "symbol": "WIN", "google_symbol": "IBOV:INDEXBVMF", "google_name": "Ibovespa · proxy WIN", "base": 175215.55, "scale": 420.0},
}
TWELVE_INTERVALS = {"M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h", "D1": "1day"}
TIME_FREQ = {"M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h", "D1": "1D"}
SESSION_NAMES = ["Global", "Tóquio", "Londres", "Nova Iorque"]


st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background:#07111f; color:#eaf2ff; }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display:none !important; }
    [data-testid="stStatusWidget"], .stDeployButton { display:none; }
    [data-testid="stMainBlockContainer"] { padding-top:6px !important; }
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
    .quote-change { display:inline-flex; gap:8px; align-items:center; font:800 12px ui-monospace,monospace; margin:0 0 10px; }.quote-change-up { color:#3d7bff; }.quote-change-down { color:#ef476f; }.quote-change-flat { color:#858585; }
    .unit { color:#dbe7f6; font:600 11px Inter,ui-sans-serif,system-ui,sans-serif; letter-spacing:0; }
    .small-row { color:#9ab0ca; font:500 10px/1.65 ui-monospace,monospace; display:flex; justify-content:space-between; align-items:center; gap:8px; }
    .small-row strong { color:#eef6ff; font-weight:800; }
    .vwap { color:#f7b718 !important; }
    .tv-rating-panel { background:#050505; border:1px solid rgba(255,255,255,.12); border-radius:10px; padding:16px 18px; color:#f4f4f4; }
    .tv-rating-head { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:4px; }
    .tv-gauge-layout { display:grid; grid-template-columns:1.15fr 1fr; gap:12px; align-items:center; margin:4px auto 10px; max-width:760px; }
    .tv-gauge { margin:0 auto; text-align:center; }
    .tv-gauge svg { display:block; width:100%; height:auto; overflow:visible; }
    .tv-gauge-title { color:#f4f4f4; font:800 13px Inter,ui-sans-serif,system-ui,sans-serif; margin-bottom:-2px; }
    .tv-gauge-state { font:800 18px/1.1 Inter,ui-sans-serif,system-ui,sans-serif; margin-top:-11px; }
    .tv-gauge-scale { display:flex; justify-content:space-between; gap:8px; color:#7f7f7f; font:600 9px ui-monospace,monospace; margin-top:5px; text-transform:uppercase; }
    .tv-gauge-compact .tv-gauge-title { font-size:11px; }.tv-gauge-compact .tv-gauge-state { font-size:11px; margin-top:-8px; }.tv-gauge-compact .tv-gauge-scale { font-size:7px; }
    .tv-mini-grid { display:grid; grid-template-columns:1fr 1fr; gap:4px; align-items:end; }
    .tv-counts { display:flex; justify-content:center; gap:24px; margin-top:-2px; font:600 10px Inter,ui-sans-serif,system-ui,sans-serif; }
    .tv-counts span { display:flex; flex-direction:column; gap:4px; align-items:center; white-space:nowrap; }.tv-counts b { color:#f2f2f2; font:800 16px ui-monospace,monospace; }
    .tv-rating-columns { display:grid; grid-template-columns:1fr 1fr; gap:36px; margin-top:10px; }
    .tv-section-title { border-bottom:1px solid rgba(255,255,255,.14); padding:0 0 8px; margin-bottom:0; color:#f4f4f4; font:800 12px Inter,ui-sans-serif,system-ui,sans-serif; }
    .tv-rating-row { display:grid; grid-template-columns:minmax(0,1fr) 82px 108px; gap:10px; align-items:center; min-height:32px; border-bottom:1px solid rgba(255,255,255,.14); color:#e6e6e6; font:500 10px Inter,ui-sans-serif,system-ui,sans-serif; }
    .tv-rating-row strong { color:#f1f1f1; font:700 10px ui-monospace,monospace; text-align:right; }.tv-rating-row em { font-style:normal; text-align:left; font-size:10px; }
    .tv-rating--1 { color:#ef476f; }.tv-rating-0 { color:#858585; }.tv-rating-1 { color:#3d7bff; }
    @media (max-width: 760px) { .tv-gauge-layout,.tv-rating-columns { grid-template-columns:1fr; }.tv-mini-grid { max-width:460px; margin:auto; }.tv-rating-row { grid-template-columns:minmax(0,1fr) 70px 92px; gap:5px; font-size:9px; }.tv-rating-head { flex-direction:column; }.tv-counts { gap:10px; } }
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
    value = ""
    try:
        # Acesso por índice é o caminho mais compatível entre versões do Streamlit Cloud.
        value = st.secrets[name]
    except (KeyError, TypeError, AttributeError, FileNotFoundError):
        value = ""
    except Exception:
        value = ""
    if not value:
        # Alguns ambientes de publicação injetam o mesmo Secret como variável de ambiente.
        value = os.getenv(name, "")
    return str(value).strip() if value else ""


def price_format(value: float, is_usdjpy: bool) -> str:
    return f"{value:.3f}" if is_usdjpy else f"{value:,.2f}"


def provider_message(response: requests.Response, label: str) -> str:
    """Extrai uma mensagem curta do provedor sem nunca incluir a chave de API."""
    try:
        payload = response.json()
        detail = payload.get("message") or payload.get("code") or payload.get("status")
    except ValueError:
        detail = response.text[:120]
    detail = str(detail or "sem detalhe do provedor").replace("\n", " ").strip()
    return f"{label} HTTP {response.status_code}: {detail[:140]}"


def parse_google_number(text: str) -> float:
    normalized = str(text).replace("\xa0", " ").replace(",", "").replace("$", "")
    match = re.search(r"[-+]?\s*\d+(?:\.\d+)?", normalized)
    if not match:
        raise ValueError(f"Número não encontrado em: {text[:80]}")
    return float(match.group().replace(" ", ""))


def quote_refresh_bucket(seconds: int = 5) -> int:
    """Gera uma janela curta para que os fragmentos renovem a cotação sem cache obsoleto."""
    return int(dt.datetime.now(TZ).timestamp() // seconds)


@st.cache_data(ttl=6, show_spinner=False)
def fetch_google_finance_quote(asset: str, refresh_bucket: int) -> tuple[float, float, float, str]:
    config = ASSETS[asset]
    url = f"https://www.google.com/finance/quote/{config['google_symbol']}?hl=en&refresh={refresh_bucket}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache, no-store, max-age=0",
        "Pragma": "no-cache",
    }
    response = requests.get(url, headers=headers, timeout=12)
    if not response.ok:
        raise RuntimeError(provider_message(response, "Google Finance"))
    soup = BeautifulSoup(response.text, "html.parser")
    price_node = soup.select_one("div.N6SYTe")
    if price_node is None:
        raise RuntimeError(f"Google Finance não encontrou o preço de {config['google_name']}.")
    price = parse_google_number(price_node.get_text(" ", strip=True))
    quote_block = price_node.find_parent("div", class_="ujg0He") or price_node.parent
    change_node = quote_block.select_one('span[jsname="xnruHf"]')
    change_pct_node = quote_block.select_one('span[jsname="vY9t3b"]')
    change = parse_google_number(change_node.get_text(" ", strip=True)) if change_node else 0.0
    change_pct = parse_google_number(change_pct_node.get_text(" ", strip=True)) if change_pct_node else 0.0
    return price, change, change_pct, config["google_name"]


SOURCE_LABELS = {"xtb": "XTB", "hantec": "Hantec", "google": "Google Finance", "real": "TwelveData", "unavailable": "Indisponível"}


def source_is_enabled(source: str) -> bool:
    return read_secret(f"{source.upper()}_ENABLED").lower() in {"1", "true", "yes", "on", "sim"}


def source_is_configured(source: str) -> bool:
    if source_is_enabled(source):
        return True
    return source.lower() == "xtb" and bool((read_secret("XTB_USER_ID") or read_secret("XTB_LOGIN")) and read_secret("XTB_PASSWORD"))


def _find_quote_value(payload: object, keys: tuple[str, ...]) -> float | None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key).lower() in keys and value not in (None, ""):
                try:
                    return float(str(value).replace(",", ""))
                except ValueError:
                    pass
        for value in payload.values():
            found = _find_quote_value(value, keys)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_quote_value(value, keys)
            if found is not None:
                return found
    return None


def _xtb_error(response: dict) -> str:
    code = response.get("errorCode", "sem código")
    description = str(response.get("errorDescr", "sem detalhe")).replace("\\n", " ").strip()
    return f"XTB xAPI {code}: {description[:180]}"


def _xtb_request(ws, payload: dict, timeout: int = 10) -> dict:
    """Envia um comando de leitura e valida a resposta sem registrar credenciais."""
    ws.settimeout(timeout)
    ws.send(json.dumps(payload, separators=(",", ":")))
    raw = ws.recv()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    messages = [part.strip() for part in str(raw).split("\n\n") if part.strip()]
    for message in messages:
        response = json.loads(message)
        if response.get("status") is not True:
            raise RuntimeError(_xtb_error(response))
        return response
    raise RuntimeError("XTB xAPI devolveu uma resposta vazia.")


@st.cache_data(ttl=6, show_spinner=False)
def fetch_xtb_xapi_quote(asset: str, refresh_bucket: int) -> tuple[float, float, float, str]:
    """Consulta cotação na xAPI sem executar ordens; uma sessão é aberta e encerrada por leitura."""
    try:
        import websocket
    except ImportError as exc:
        raise RuntimeError("Dependência websocket-client ausente; instale-a pelo requirements.txt.") from exc

    user_id = read_secret("XTB_USER_ID") or read_secret("XTB_LOGIN")
    password = read_secret("XTB_PASSWORD")
    if not user_id or not password:
        raise RuntimeError("Configure XTB_USER_ID e XTB_PASSWORD nos Secrets; credenciais nunca ficam no código.")
    environment = read_secret("XTB_ENVIRONMENT").lower() or "demo"
    default_url = "wss://ws.xapi.pro/real" if environment == "real" else "wss://ws.xapi.pro/demo"
    ws_url = read_secret("XTB_WS_URL") or default_url
    config = ASSETS[asset]
    xtb_defaults = {"XAUUSD": "GOLD", "MINIWIN": "WIN"}
    symbol = read_secret(f"XTB_SYMBOL_{asset}") or xtb_defaults.get(asset, config["symbol"])
    app_name = read_secret("XTB_APP_NAME") or "monitor-de-mercado"
    ws = None
    logged_in = False
    try:
        ws = websocket.create_connection(ws_url, timeout=10, enable_multithread=False)
        login = _xtb_request(ws, {"command": "login", "arguments": {"userId": user_id, "password": password, "appName": app_name}})
        logged_in = login.get("status") is True
        symbol_response = _xtb_request(ws, {"command": "getSymbol", "arguments": {"symbol": symbol}})
        tick_response = _xtb_request(ws, {"command": "getTickPrices", "arguments": {"level": 0, "symbols": [symbol], "timestamp": int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)}})
        symbol_data = symbol_response.get("returnData") or {}
        quotations = tick_response.get("returnData", {}).get("quotations", [])
        quote = next((item for item in quotations if str(item.get("symbol", "")).upper() == symbol.upper()), quotations[0] if quotations else {})
        bid = _find_quote_value(quote, ("bid",))
        ask = _find_quote_value(quote, ("ask",))
        last = _find_quote_value(quote, ("last", "price"))
        price = last if last is not None else ((bid + ask) / 2 if bid is not None and ask is not None else bid or ask)
        if price is None:
            price = _find_quote_value(symbol_data, ("bid", "ask", "last", "price"))
        if price is None:
            raise RuntimeError(f"XTB xAPI não devolveu preço para o símbolo {symbol}.")
        change = _find_quote_value(symbol_data, ("dailychange", "change", "pricechange")) or _find_quote_value(quote, ("change", "pricechange")) or 0.0
        change_pct = _find_quote_value(symbol_data, ("percentagechange", "changepct", "changepercent", "pct")) or _find_quote_value(quote, ("changepct", "changepercent", "pct")) or 0.0
        return float(price), float(change), float(change_pct), f"XTB xAPI · {symbol} · {environment}"
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError(f"XTB xAPI indisponível: {str(exc)[:180]}") from exc
    finally:
        if ws is not None:
            if logged_in:
                try:
                    _xtb_request(ws, {"command": "logout"}, timeout=3)
                except Exception:
                    pass
            try:
                ws.close()
            except Exception:
                pass


@st.cache_data(ttl=6, show_spinner=False)
def fetch_broker_quote(source: str, asset: str, refresh_bucket: int) -> tuple[float, float, float, str]:
    if source.lower() == "xtb" and (read_secret("XTB_USER_ID") or read_secret("XTB_LOGIN") or read_secret("XTB_PASSWORD")):
        return fetch_xtb_xapi_quote(asset, refresh_bucket)

    prefix = source.upper()
    url = read_secret(f"{prefix}_QUOTE_URL_{asset}") or read_secret(f"{prefix}_QUOTE_URL")
    if not url:
        raise RuntimeError(f"{source.upper()} não configurada: informe {prefix}_QUOTE_URL ou {prefix}_QUOTE_URL_{asset}.")
    config = ASSETS[asset]
    symbol = read_secret(f"{prefix}_SYMBOL_{asset}") or config["symbol"]
    token = read_secret(f"{prefix}_API_KEY") or read_secret(f"{prefix}_TOKEN")
    headers = {"Accept": "application/json", "User-Agent": "Monitor-de-Mercado/1.0", "Cache-Control": "no-cache, no-store, max-age=0", "Pragma": "no-cache"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, params={"symbol": symbol, "asset": asset}, headers=headers, timeout=12)
    if not response.ok:
        raise RuntimeError(provider_message(response, source.upper()))
    payload = response.json()
    price = _find_quote_value(payload, ("price", "last", "lastprice", "close", "bid"))
    if price is None:
        raise RuntimeError(f"{source.upper()} respondeu sem campo de preço para {symbol}.")
    change = _find_quote_value(payload, ("change", "changevalue", "pricechange")) or 0.0
    change_pct = _find_quote_value(payload, ("changepct", "changepercent", "percentchange", "pct")) or 0.0
    return price, change, change_pct, f"{source.upper()} · {symbol}"


@st.cache_data(ttl=10, show_spinner=False)
def fetch_twelve_data(symbol: str, interval: str, api_key: str) -> tuple[pd.DataFrame, float | None, str]:
    headers = {"Authorization": f"apikey {api_key}"}
    params = {"symbol": symbol, "interval": interval, "outputsize": 60, "order": "asc", "timezone": "America/Sao_Paulo"}
    series = requests.get("https://api.twelvedata.com/time_series", params=params, headers=headers, timeout=8)
    if not series.ok:
        raise RuntimeError(provider_message(series, "Candles"))
    payload = series.json()
    if payload.get("status") == "error" or not payload.get("values"):
        raise RuntimeError(str(payload.get("message", "TwelveData não devolveu candles."))[:160])
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


def make_data(asset: str, timeframe: str, anchor: float | None = None) -> pd.DataFrame:
    config = ASSETS[asset]
    base = float(anchor if anchor is not None else config["base"])
    now = dt.datetime.now(TZ).replace(second=0, microsecond=0)
    # O histórico estimado só é usado para visualização quando o provedor não oferece candles.
    bucket = int(dt.datetime.now().timestamp() // 15)
    rng = np.random.default_rng({"USDJPY": 11, "US100": 29, "XAUUSD": 47, "BTCUSD": 71, "MINIWIN": 89}[asset] + bucket)
    close = base + np.r_[0, np.cumsum(rng.normal(0, config["scale"], 59))]
    simulated_spot = base + rng.normal(0, config["scale"] * .62)
    close = close - close[-1] + simulated_spot
    open_ = close - rng.normal(0, config["scale"] * 0.34, 60)
    high = np.maximum(open_, close) + rng.uniform(config["scale"] * .15, config["scale"] * .7, 60)
    low = np.minimum(open_, close) - rng.uniform(config["scale"] * .15, config["scale"] * .7, 60)
    return pd.DataFrame({"time": pd.date_range(end=now, periods=60, freq=TIME_FREQ[timeframe]), "open": open_, "high": high, "low": low, "close": close, "volume": rng.integers(220, 880, 60)})


def load_market_data(asset: str, timeframe: str) -> tuple[pd.DataFrame, float | None, float | None, float | None, str, str]:
    config = ASSETS[asset]
    requested_source = st.session_state.get("source_mode", "auto")
    if requested_source == "auto":
        broker_candidates = [source for source in ("xtb", "hantec") if source_is_configured(source)]
    elif requested_source in {"xtb", "hantec"}:
        broker_candidates = [requested_source]
    else:
        broker_candidates = []
    source_errors = []
    refresh_bucket = quote_refresh_bucket()
    for source in broker_candidates:
        try:
            broker_spot, broker_change, broker_change_pct, broker_name = fetch_broker_quote(source, asset, refresh_bucket)
            data = make_data(asset, timeframe, anchor=broker_spot)
            data.loc[data.index[-1], "close"] = broker_spot
            return data, broker_spot, broker_change, broker_change_pct, source, f"{broker_name} ativo."
        except Exception as broker_error:
            source_errors.append(f"{source.upper()}: {str(broker_error)[:120]}")

    api_key = read_secret("TWELVEDATA_API_KEY") or st.session_state.get("api_key", "").strip()
    if asset == "XAUUSD" and api_key:
        symbol = read_secret(f"TWELVEDATA_SYMBOL_{asset}") or "XAU/USD"
        try:
            data, spot, volume_note = fetch_twelve_data(symbol, TWELVE_INTERVALS[timeframe], api_key)
            if spot is None:
                raise RuntimeError("Twelve Data não devolveu o spot XAU/USD.")
            data.loc[data.index[-1], "close"] = spot
            return data, spot, None, None, "real", f"TwelveData · Gold Spot / US Dollar ({symbol}) · {volume_note}. Google Finance foi evitado porque o identificador público disponível é futuro COMEX."
        except Exception as twelve_spot_error:
            source_errors.append(f"TwelveData XAU/USD: {str(twelve_spot_error)[:120]}")

    try:
        google_spot, google_change, google_change_pct, google_name = fetch_google_finance_quote(asset, refresh_bucket)
    except Exception as google_error:
        google_reason = str(google_error)[:170]
        api_key = read_secret("TWELVEDATA_API_KEY") or st.session_state.get("api_key", "").strip()
        if api_key:
            symbol = read_secret(f"TWELVEDATA_SYMBOL_{asset}") or config["symbol"]
            try:
                data, spot, volume_note = fetch_twelve_data(symbol, TWELVE_INTERVALS[timeframe], api_key)
                return data, spot, None, None, "real", f"Google Finance indisponível · {google_reason} · backup TwelveData {symbol} · {volume_note}."
            except Exception as twelve_error:
                google_reason = f"{google_reason}; TwelveData: {str(twelve_error)[:110]}"
        broker_note = " | ".join(source_errors)
        return make_data(asset, timeframe), None, None, None, "unavailable", f"Preço real indisponível · Google Finance {config['google_symbol']} · {google_reason}. {broker_note} Nenhum valor simulado é exibido como cotação."

    if asset == "XAUUSD":
        broker_note = " | ".join(source_errors)
        return make_data(asset, timeframe), None, None, None, "unavailable", f"XAU/USD spot indisponível. O Google Finance disponível é {config['google_symbol']} ({config['google_name']}) e não será usado como preço spot. Configure XTB/Hantec ou TWELVEDATA_API_KEY para XAU/USD. {broker_note}"

    api_key = read_secret("TWELVEDATA_API_KEY") or st.session_state.get("api_key", "").strip()
    if api_key:
        symbol = read_secret(f"TWELVEDATA_SYMBOL_{asset}") or config["symbol"]
        try:
            data, _, volume_note = fetch_twelve_data(symbol, TWELVE_INTERVALS[timeframe], api_key)
            data.loc[data.index[-1], "close"] = google_spot
            return data, google_spot, google_change, google_change_pct, "google", f"Google Finance · {google_name} ({config['google_symbol']}) · candles TwelveData {symbol} · {volume_note}."
        except Exception:
            pass

    data = make_data(asset, timeframe, anchor=google_spot)
    data.loc[data.index[-1], "close"] = google_spot
    fallback_note = f"Google Finance · {google_name} ({config['google_symbol']}) · histórico intradiário estimado a partir da cotação atual."
    if requested_source in {"xtb", "hantec"} and source_errors:
        fallback_note = f"{requested_source.upper()} indisponível ({source_errors[-1]}) · fallback automático para {fallback_note}"
    elif requested_source == "auto" and not broker_candidates:
        fallback_note = f"XTB e Hantec desativadas/não configuradas · fallback automático para {fallback_note}"
    return data, google_spot, google_change, google_change_pct, "google", fallback_note


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


def pivot_levels(data: pd.DataFrame) -> dict[str, float]:
    """Calcula pivôs clássicos usando a última barra concluída."""
    source = data.iloc[-2] if len(data) > 1 else data.iloc[-1]
    high, low, close = float(source.high), float(source.low), float(source.close)
    pivot = (high + low + close) / 3
    return {
        "R3": high + 2 * (pivot - low),
        "R2": pivot + (high - low),
        "R1": 2 * pivot - low,
        "P": pivot,
        "S1": 2 * pivot - high,
        "S2": pivot - (high - low),
        "S3": low - 2 * (high - pivot),
    }


def _vote(value: float, buy_threshold: float, sell_threshold: float) -> int:
    if value >= buy_threshold:
        return 1
    if value <= sell_threshold:
        return -1
    return 0


def _rating_label(score: float) -> str:
    if score <= -0.6:
        return "Tendência de Baixa Forte"
    if score <= -0.2:
        return "Tendência de Baixa"
    if score < 0.2:
        return "Tendência Neutra"
    if score < 0.6:
        return "Viés de alta"
    return "Viés de alta forte"


def _rating_color(score: float) -> str:
    if score <= -0.2:
        return "#ef476f"
    if score < 0.2:
        return "#858585"
    return "#3d7bff"


def _arc_path(cx: float, cy: float, radius: float, start_deg: float, end_deg: float) -> str:
    start = math.radians(start_deg)
    end = math.radians(end_deg)
    x1, y1 = cx + radius * math.cos(start), cy + radius * math.sin(start)
    x2, y2 = cx + radius * math.cos(end), cy + radius * math.sin(end)
    large = 1 if abs(end_deg - start_deg) > 180 else 0
    return f"M {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f}"


def render_gauge(score: float, title: str, compact: bool = False) -> str:
    score = float(np.clip(score, -1, 1))
    # Arco visual: esquerda = venda forte, centro = neutro, direita = compra forte.
    cx, cy, radius = (160, 154, 112) if not compact else (110, 106, 67)
    start, end = 180, 360
    segments = [(180, 216, "#ef476f"), (216, 252, "#b84d91"), (252, 288, "#754fa8"), (288, 324, "#435bd1"), (324, 360, "#3d7bff")]
    stroke = 13 if not compact else 9
    paths = "".join(f'<path d="{_arc_path(cx, cy, radius, a, b)}" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="butt"/>' for a, b, color in segments)
    angle = 270 + score * 90
    needle_len = radius - (26 if not compact else 16)
    needle_x = cx + needle_len * math.cos(math.radians(angle))
    needle_y = cy + needle_len * math.sin(math.radians(angle))
    label = _rating_label(score)
    color = _rating_color(score)
    width = "340px" if not compact else "220px"
    height = "205px" if not compact else "142px"
    label_size = "20px" if not compact else "12px"
    return f'''<div class="tv-gauge {'tv-gauge-compact' if compact else ''}" style="width:{width}"><div class="tv-gauge-title">{html.escape(title)}</div><svg viewBox="0 0 320 180" role="img" aria-label="{html.escape(label)}"><path d="{_arc_path(cx, cy, radius, 180, 360)}" fill="none" stroke="#333" stroke-width="{stroke}" opacity=".38"/>{paths}<line x1="{cx}" y1="{cy}" x2="{needle_x:.2f}" y2="{needle_y:.2f}" stroke="#f3f3f3" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="6" fill="#f3f3f3"/><circle cx="{cx}" cy="{cy}" r="3" fill="#202020"/></svg><div class="tv-gauge-state" style="color:{color};font-size:{label_size}">{html.escape(label)}</div><div class="tv-gauge-scale"><span>Venda forte</span><span>Neutro</span><span>Compra forte</span></div></div>'''


def technical_ratings(data: pd.DataFrame) -> dict[str, object]:
    close = data.close.astype(float)
    high = data.high.astype(float)
    low = data.low.astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean().replace(0, np.nan)
    rsi = (100 - (100 / (1 + gain / loss))).fillna(50).iloc[-1]
    lowest = low.rolling(14, min_periods=1).min().iloc[-1]
    highest = high.rolling(14, min_periods=1).max().iloc[-1]
    stoch = ((close.iloc[-1] - lowest) / max(highest - lowest, 1e-9)) * 100
    typical = (high + low + close) / 3
    cci_mean = typical.rolling(20, min_periods=1).mean().iloc[-1]
    cci_dev = (typical - typical.rolling(20, min_periods=1).mean()).abs().rolling(20, min_periods=1).mean().iloc[-1]
    cci = (typical.iloc[-1] - cci_mean) / max(0.015 * cci_dev, 1e-9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    ao = ((high + low) / 2).rolling(5, min_periods=1).mean().iloc[-1] - ((high + low) / 2).rolling(34, min_periods=1).mean().iloc[-1]
    momentum = close.iloc[-1] - close.iloc[max(0, len(close) - 11)]
    osc_votes = [
        ("Índice de Força Relativa (14)", float(rsi), _vote(float(rsi), 55, 45)),
        ("Estocástico %K (14, 3, 3)", float(stoch), _vote(float(stoch), 55, 45)),
        ("Índice Canal de Commodities (20)", float(cci), _vote(float(cci), 100, -100)),
        ("Índice Direcional Médio (14)", float(abs(momentum)), _vote(float(momentum), 0.0, 0.0)),
        ("Oscilador Maravilhoso (AO)", float(ao), _vote(float(ao), 0.0, 0.0)),
        ("Momentum (10)", float(momentum), _vote(float(momentum), 0.0, 0.0)),
        ("Nível MACD (12,26)", float(macd.iloc[-1] - signal_line.iloc[-1]), _vote(float(macd.iloc[-1] - signal_line.iloc[-1]), 0.0, 0.0)),
        ("IFR Estocástico Rápido (3, 3, 14, 14)", float(stoch), _vote(float(stoch), 60, 40)),
    ]
    lengths = [10, 20, 30, 50, 100, 200]
    ma_votes = []
    for length in lengths:
        ema = float(close.ewm(span=length, adjust=False).mean().iloc[-1])
        sma = float(close.rolling(length, min_periods=1).mean().iloc[-1])
        ma_votes.extend([
            (f"Média Móvel Exponencial ({length})", ema, 1 if close.iloc[-1] > ema else -1 if close.iloc[-1] < ema else 0),
            (f"Média Móvel Simples ({length})", sma, 1 if close.iloc[-1] > sma else -1 if close.iloc[-1] < sma else 0),
        ])
    def summarize(votes: list[tuple[str, float, int]]) -> dict[str, object]:
        values = [vote for _, _, vote in votes]
        score = float(np.mean(values)) if values else 0.0
        return {"votes": votes, "score": score, "sell": values.count(-1), "neutral": values.count(0), "buy": values.count(1), "label": _rating_label(score)}
    oscillators = summarize(osc_votes)
    moving_averages = summarize(ma_votes)
    summary = summarize(osc_votes + ma_votes)
    return {"summary": summary, "oscillators": oscillators, "moving_averages": moving_averages}


def pressure_confluence(data: pd.DataFrame, poc: float, vah: float, val: float) -> dict[str, object]:
    """Consolida indicadores, perfil de volume e volume relativo em uma pressão direcional."""
    features = strategy_features(data)
    row = features.iloc[-1]
    close = float(row["close"])
    atr = max(float(row["atr"]), abs(float(row["high"]) - float(row["low"])), 1e-9)
    clip = lambda value: float(np.clip(value, -1.0, 1.0))
    trend = clip((close - float(row["ema_fast_generic"])) / atr)
    momentum = clip((float(row["rsi"]) - 50.0) / 25.0)
    macd = clip(float(row["macd_hist"]) / atr)
    adx_direction = 0.0 if float(row["adx"]) < 10 else clip((float(row["plus_di"]) - float(row["minus_di"])) / 35.0) * float(np.clip(float(row["adx"]) / 25.0, 0.0, 1.0))
    bollinger = clip(float(row["bb_z"]) / 2.0)
    vwap_bias = clip((close - float(row["vwap_20"])) / atr)
    profile_width = max(float(vah - val), atr)
    poc_bias = clip((close - float(poc)) / profile_width * 2.0)
    value_bias = 1.0 if close > vah else -1.0 if close < val else clip((close - float(poc)) / profile_width * 2.0)
    volume_ratio = float(row["volume"] / max(float(row["volume_sma20"]), 1e-9))
    candle_direction = float(np.sign(float(row["close"]) - float(row["open"])))
    volume_confirmation = candle_direction * float(np.clip(volume_ratio / 1.5, 0.0, 1.0))
    components = {
        "Indicadores": float(np.mean([trend, momentum, macd, adx_direction, bollinger, vwap_bias])),
        "POC / Área de Valor": float(np.mean([poc_bias, value_bias])),
        "Volume relativo": volume_confirmation,
    }
    score = float(np.clip(components["Indicadores"] * 0.60 + components["POC / Área de Valor"] * 0.25 + components["Volume relativo"] * 0.15, -1.0, 1.0))
    buy = int(np.clip(round(50 + score * 45), 5, 95))
    return {"score": score, "buy": buy, "sell": 100 - buy, "ratio": volume_ratio, "components": components}


STRATEGY_PROFILES = {
    "BTCUSD": {
        "name": "BTC · tendência + momentum",
        "fast": 21,
        "slow": 55,
        "min_confirmations": 3,
        "volume_factor": 0.75,
        "exit_rsi_long": 45,
        "exit_rsi_short": 55,
        "exit_adx": 14,
    },
    "MINIWIN": {
        "name": "WIN · tendência + VWAP",
        "fast": 9,
        "slow": 21,
        "min_confirmations": 3,
        "volume_factor": 0.75,
        "exit_rsi_long": 46,
        "exit_rsi_short": 54,
        "exit_adx": 14,
    },
}


def strategy_features(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula indicadores somente com dados disponíveis até cada vela."""
    out = data.copy()
    close = out["close"].astype(float)
    high = out["high"].astype(float)
    low = out["low"].astype(float)
    volume = out["volume"].astype(float).clip(lower=0)
    typical = (high + low + close) / 3
    out["ema_fast_generic"] = close.ewm(span=9, adjust=False).mean()
    out["ema_slow_generic"] = close.ewm(span=21, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    out["rsi"] = (100 - (100 / (1 + gain / loss.replace(0, np.nan)))).fillna(50).clip(0, 100)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    out["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()
    true_range = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1 / 14, adjust=False).mean()
    out["atr"] = atr.replace(0, np.nan).fillna((high - low).abs().mean()).fillna(0)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=out.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=out.index)
    plus_di = (100 * plus_dm.ewm(alpha=1 / 14, adjust=False).mean() / out["atr"].replace(0, np.nan)).fillna(0)
    minus_di = (100 * minus_dm.ewm(alpha=1 / 14, adjust=False).mean() / out["atr"].replace(0, np.nan)).fillna(0)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
    out["adx"] = dx.ewm(alpha=1 / 14, adjust=False).mean().fillna(0)
    out["plus_di"] = plus_di
    out["minus_di"] = minus_di
    out["bb_mid"] = close.rolling(20, min_periods=1).mean()
    bb_std = close.rolling(20, min_periods=1).std(ddof=0).fillna(0)
    out["bb_z"] = ((close - out["bb_mid"]) / bb_std.replace(0, np.nan)).fillna(0)
    volume_sum = volume.rolling(20, min_periods=1).sum().replace(0, np.nan)
    out["vwap_20"] = ((typical * volume).rolling(20, min_periods=1).sum() / volume_sum).fillna(close)
    out["volume_sma20"] = volume.rolling(20, min_periods=1).mean()
    return out


def build_strategy_backtest(data: pd.DataFrame, asset: str) -> pd.DataFrame:
    """Aplica regras direcionais específicas a BTC/WIN e preserva o baseline nos demais ativos."""
    out = strategy_features(data)
    close = out["close"].astype(float)
    profile = STRATEGY_PROFILES.get(asset)
    if profile is None:
        out["ema_fast"] = out["ema_fast_generic"]
        out["ema_slow"] = out["ema_slow_generic"]
        out["entry_signal"] = np.where(close > out["open"], "COMPRA", "VENDA")
        out["exit_signal"] = "Próxima vela"
        out["exit_reason"] = "Baseline de direção da vela"
        out["position"] = np.where(close > out["open"], 1, -1).astype(float)
        out["direction"] = np.where(out["position"] > 0, "COMPRA", "VENDA")
    else:
        fast = close.ewm(span=profile["fast"], adjust=False).mean()
        slow = close.ewm(span=profile["slow"], adjust=False).mean()
        out["ema_fast"] = fast
        out["ema_slow"] = slow
        bullish = [
            close > fast,
            fast > slow,
            out["rsi"] > 52,
            out["macd_hist"] > 0,
            (out["adx"] > 18) & (out["plus_di"] > out["minus_di"]),
            close > out["bb_mid"],
            close > out["vwap_20"],
            out["volume"] >= out["volume_sma20"] * profile["volume_factor"],
        ]
        bearish = [
            close < fast,
            fast < slow,
            out["rsi"] < 48,
            out["macd_hist"] < 0,
            (out["adx"] > 18) & (out["minus_di"] > out["plus_di"]),
            close < out["bb_mid"],
            close < out["vwap_20"],
            out["volume"] >= out["volume_sma20"] * profile["volume_factor"],
        ]
        long_score = sum(condition.astype(int) for condition in bullish)
        short_score = sum(condition.astype(int) for condition in bearish)
        long_entry = (long_score >= profile["min_confirmations"]) & (long_score > short_score)
        short_entry = (short_score >= profile["min_confirmations"]) & (short_score > long_score)
        exit_long = (close < fast) | (out["rsi"] <= profile["exit_rsi_long"]) | (out["macd_hist"] < 0) | ((out["adx"] < profile["exit_adx"]) & (close < out["vwap_20"]))
        exit_short = (close > fast) | (out["rsi"] >= profile["exit_rsi_short"]) | (out["macd_hist"] > 0) | ((out["adx"] < profile["exit_adx"]) & (close > out["vwap_20"]))
        positions = np.zeros(len(out), dtype=float)
        entry_signal = np.full(len(out), "", dtype=object)
        exit_signal = np.full(len(out), "", dtype=object)
        exit_reason = np.full(len(out), "", dtype=object)
        current = 0
        for i in range(len(out)):
            if current == 0:
                if bool(long_entry.iloc[i]):
                    current = 1
                    entry_signal[i] = "COMPRA"
                elif bool(short_entry.iloc[i]):
                    current = -1
                    entry_signal[i] = "VENDA"
            elif current == 1 and bool(exit_long.iloc[i]):
                current = 0
                exit_signal[i] = "SAÍDA"
                exit_reason[i] = "Perda de tendência, momentum ou VWAP"
                if bool(short_entry.iloc[i]):
                    current = -1
                    entry_signal[i] = "VENDA"
            elif current == -1 and bool(exit_short.iloc[i]):
                current = 0
                exit_signal[i] = "SAÍDA"
                exit_reason[i] = "Perda de tendência, momentum ou VWAP"
                if bool(long_entry.iloc[i]):
                    current = 1
                    entry_signal[i] = "COMPRA"
            positions[i] = current
        out["entry_signal"] = entry_signal
        out["exit_signal"] = exit_signal
        out["exit_reason"] = exit_reason
        out["position"] = positions
        out["direction"] = np.where(positions > 0, "COMPRA", np.where(positions < 0, "VENDA", "FORA"))
    out["next_return"] = close.shift(-1) - close
    out["next_return_pct"] = out["next_return"] / close.replace(0, np.nan)
    out["strategy_return_pct"] = np.where(out["position"] != 0, out["position"] * out["next_return_pct"], 0.0)
    out["strategy_pnl"] = np.where(out["position"] != 0, out["position"] * out["next_return"], 0.0)
    out["win"] = np.where(out["position"] != 0, out["strategy_return_pct"] > 0, np.nan)
    return out


def render_rating_panel(ratings: dict[str, object], asset_label: str, timeframe: str) -> str:
    summary = ratings["summary"]
    oscillators = ratings["oscillators"]
    moving_averages = ratings["moving_averages"]
    def rows(group: dict[str, object]) -> str:
        return "".join(f'<div class="tv-rating-row"><span>{html.escape(name)}</span><strong>{value:,.3f}</strong><em class="tv-rating-{vote}">{_rating_label(vote):s}</em></div>' for name, value, vote in group["votes"])
    return f'''<div class="tv-rating-panel"><div class="tv-rating-head"><div><div class="card-title">Análise técnica · {html.escape(asset_label)}</div><div class="card-note">Resumo dos sinais no intervalo <b>{html.escape(timeframe)}</b>, com preço do ativo sincronizado ao feed selecionado.</div></div><span class="badge-amber">TRADING VIEW STYLE</span></div><div class="tv-gauge-layout"><div>{render_gauge(summary["score"], "Resumo", False)}<div class="tv-counts"><span class="tv-rating--1">Tendência de Baixa <b>{summary["sell"]}</b></span><span class="tv-rating-0">Tendência Neutra <b>{summary["neutral"]}</b></span><span class="tv-rating-1">Viés de alta <b>{summary["buy"]}</b></span></div></div><div class="tv-mini-grid">{render_gauge(oscillators["score"], "Osciladores", True)}{render_gauge(moving_averages["score"], "Médias Móveis", True)}</div></div><div class="tv-rating-columns"><div><div class="tv-section-title">Osciladores</div>{rows(oscillators)}</div><div><div class="tv-section-title">Médias Móveis</div>{rows(moving_averages)}</div></div></div>'''


def live_operational_state() -> dict[str, object]:
    """Calcula apenas os cartões operacionais que podem acompanhar a cotação sem rerun global."""
    live_asset = st.session_state.asset
    live_timeframe = st.session_state.timeframe
    live_session = st.session_state.session
    live_data, live_spot, live_change, live_change_pct, live_mode, live_note = load_market_data(live_asset, live_timeframe)
    if live_spot is not None:
        live_data.loc[live_data.index[-1], "close"] = live_spot
    live_last = float(live_spot if live_spot is not None else live_data.close.iloc[-1])
    live_profile = session_slice(live_data, live_session)
    live_poc, live_vah, live_val = profile_levels(live_profile)
    live_ma9 = float(live_data.volume.rolling(9, min_periods=1).mean().iloc[-1])
    live_ma21 = float(live_data.volume.rolling(21, min_periods=1).mean().iloc[-1])
    live_ma200 = float(live_data.volume.rolling(200, min_periods=1).mean().iloc[-1])
    live_pressure = pressure_confluence(live_data, live_poc, live_vah, live_val)
    live_buy = int(live_pressure["buy"])
    live_sell = int(live_pressure["sell"])
    live_bearish = live_buy < 50
    live_ratio = float(live_pressure["ratio"])
    live_volume_status = "Volume não fornecido" if "não fornecido" in live_note else ("Volume Acima da MA9" if live_ratio > 1.0 else "Volume Normal")
    live_confidence = ("VENDA", int(np.clip(50 + abs(live_pressure["score"]) * 42, 50, 92))) if live_bearish else ("COMPRA", int(np.clip(50 + abs(live_pressure["score"]) * 42, 50, 92)))
    return {
        "asset": live_asset,
        "label": ASSETS[live_asset]["label"],
        "timeframe": live_timeframe,
        "is_usdjpy": live_asset == "USDJPY",
        "mode": live_mode,
        "note": live_note,
        "last": live_last,
        "poc": live_poc,
        "vah": live_vah,
        "val": live_val,
        "ma9": live_ma9,
        "ma21": live_ma21,
        "ma200": live_ma200,
        "buy": live_buy,
        "sell": live_sell,
        "bearish": live_bearish,
        "ratio": live_ratio,
        "volume_status": live_volume_status,
        "signal": live_confidence[0],
        "confidence": live_confidence[1],
        "pressure_score": live_pressure["score"],
        "pressure_components": live_pressure["components"],
    }


for key, value in {"asset": "USDJPY", "timeframe": "H1", "session": "Global", "source_mode": "auto", "api_key": "", "sound_alerts": False, "news_filter": "Todas", "bottom_view": "Linha", "backtest_result": None}.items():
    if key not in st.session_state:
        st.session_state[key] = value
if st.session_state.session not in SESSION_NAMES:
    st.session_state.session = "Global"

# Um único rerun periódico evita condições de corrida DOM entre múltiplos fragmentos concorrentes.
st_autorefresh(interval=3000, limit=None, key="market-refresh")

has_live_feed = bool(read_secret("TWELVEDATA_API_KEY") or st.session_state.get("api_key", "").strip())

asset = st.session_state.asset
timeframe = st.session_state.timeframe
session = st.session_state.session
is_usdjpy = asset == "USDJPY"
config = ASSETS[asset]
asset_label, desk_name = config["label"], config["desk"]
df, live_spot, quote_change, quote_change_pct, feed_mode, feed_note = load_market_data(asset, timeframe)
last = float(live_spot if live_spot is not None else df.close.iloc[-1])
if live_spot is not None:
    df.loc[df.index[-1], "close"] = live_spot
profile_data = session_slice(df, session)
typical = (df.high + df.low + df.close) / 3
vwap = float(np.average(typical, weights=df.volume))
poc, vah, val = profile_levels(profile_data)
session_levels = historical_pocs(df)
pivots = pivot_levels(df)
swing_high, swing_low = float(df.high.max()), float(df.low.min())
recent = df.tail(12)
pressure = pressure_confluence(df, poc, vah, val)
buy = int(pressure["buy"])
sell, bearish = int(pressure["sell"]), buy < 50
ma9 = float(df.volume.rolling(9, min_periods=1).mean().iloc[-1])
ma21 = float(df.volume.rolling(21, min_periods=1).mean().iloc[-1])
ma200 = float(df.volume.rolling(200, min_periods=1).mean().iloc[-1])
volume_ratio = float(pressure["ratio"])
volume_status = "Volume não fornecido" if "não fornecido" in feed_note else ("Volume Acima da MA9" if volume_ratio > 1.0 else "Volume Normal")
signal, confidence = ("VENDA", int(np.clip(50 + abs(pressure["score"]) * 42, 50, 92))) if bearish else ("COMPRA", int(np.clip(50 + abs(pressure["score"]) * 42, 50, 92)))
ratings = technical_ratings(df)
vwap_series = (typical * df.volume).cumsum() / df.volume.cumsum()
backtest = build_strategy_backtest(df, asset)
valid_backtest = backtest.replace([np.inf, -np.inf], np.nan).dropna(subset=["next_return", "strategy_return_pct"])
traded_backtest = valid_backtest[valid_backtest["position"] != 0]
win_rate = float(traded_backtest.win.mean() * 100) if len(traded_backtest) else 0.0
mean_pnl = float(traded_backtest["strategy_pnl"].mean()) if len(traded_backtest) else 0.0
strategy_returns = valid_backtest["strategy_return_pct"].astype(float)
periods_per_day = {"M5": 288, "M15": 96, "H1": 24, "H4": 6, "D1": 1}[timeframe]
annualization_factor = math.sqrt(periods_per_day * 252)
return_std = float(strategy_returns.std(ddof=1)) if len(strategy_returns) > 1 else 0.0
sharpe_ratio = float(strategy_returns.mean() / return_std * annualization_factor) if return_std > 0 else 0.0
equity_curve = (1 + strategy_returns).cumprod()
drawdown_curve = equity_curve / equity_curve.cummax() - 1 if len(equity_curve) else pd.Series(dtype=float)
max_drawdown = float(drawdown_curve.min() * 100) if len(drawdown_curve) else 0.0
total_return = float((equity_curve.iloc[-1] - 1) * 100) if len(equity_curve) else 0.0
strategy_profile_label = STRATEGY_PROFILES.get(asset, {}).get("name", "Baseline direcional")
clock = dt.datetime.now(TZ).strftime("%H:%M:%S")
is_real_feed = feed_mode in {"google", "real", "xtb", "hantec"}
source_label = SOURCE_LABELS.get(feed_mode, feed_mode.upper())
feed_state_label = f"{source_label.upper()} · 15S" if is_real_feed else "PREÇO INDISPONÍVEL"
spot_title = f"Cotação {source_label} ({timeframe})" if is_real_feed else "Cotação indisponível"
spot_badge = f'<span class="badge-green">{source_label}</span>' if feed_mode in {"google", "xtb", "hantec"} else ('<span class="badge-amber">Backup</span>' if feed_mode == "real" else '<span class="badge-red">Sem preço</span>')
refresh_note = f"Cotação {source_label} atualizada conforme o provedor." if is_real_feed else "Não há cotação real disponível; nenhum valor simulado será exibido."
refresh_footer = f"Cotação {source_label} conforme o provedor." if is_real_feed else "Preço real indisponível."


# Topo compacto do terminal original: marca à esquerda e seleção de ativo no canto direito.
header_left, header_actions = st.columns([1.2, 1.1], gap="small", vertical_alignment="center")
with header_left:
    st.markdown(f'<div class="topbar"><div class="brand-mark">↯</div><div><div class="kicker">Mesa de Tesouraria · Forex, Índices & Cripto</div><div class="headline">Terminal Institucional (USD/JPY, US100, XAU/USD, BTC/USD & WIN)</div></div></div>', unsafe_allow_html=True)
with header_actions:
    action_cols = st.columns([1, 1, 1, 1, 1, 1.35], gap="small")
    for col, key, label in zip(action_cols[:5], ["USDJPY", "US100", "XAUUSD", "BTCUSD", "MINIWIN"], ["USD/JPY", "US100", "XAU/USD", "BTC/USD", "Mini WIN"]):
        with col:
            if st.button(label, key=f"asset-{key}", type="primary" if asset == key else "secondary"):
                st.session_state.asset = key
                st.rerun()
    with action_cols[3]:
        st.markdown(f'<div class="feed-badge">↻ {feed_state_label} · {clock}</div>', unsafe_allow_html=True)

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

with st.container(border=True):
    source_label_col, source_action_col, source_note_col = st.columns([.82, 2.15, .78], gap="small", vertical_alignment="center")
    with source_label_col:
        st.markdown('<div class="eyebrow">Fonte de cotação</div><div class="card-title">Prioridade do feed</div>', unsafe_allow_html=True)
    with source_action_col:
        source_cols = st.columns(4, gap="small")
        source_options = [("auto", "Auto"), ("xtb", "XTB"), ("hantec", "Hantec"), ("google", "Google")]
        for col, source, label in zip(source_cols, [item[0] for item in source_options], [item[1] for item in source_options]):
            with col:
                available = source in {"auto", "google"} or source_is_configured(source)
                button_label = label + (" ✓" if available else " · off")
                if st.button(button_label, key=f"source-{source}", disabled=not available, type="primary" if st.session_state.source_mode == source else "secondary"):
                    st.session_state.source_mode = source
                    st.rerun()
    with source_note_col:
        st.markdown('<div class="card-note" style="text-align:right">Auto: XTB → Hantec → Google.<br>Ative XTB_ENABLED/HANTEC_ENABLED nos Secrets.</div>', unsafe_allow_html=True)

with st.container(border=True):
    market_label_col, market_action_col, market_note_col = st.columns([.82, 2.15, .78], gap="small", vertical_alignment="center")
    with market_label_col:
        st.markdown('<div class="eyebrow">Mercado negociado</div><div class="card-title">Troca de ativo</div>', unsafe_allow_html=True)
    with market_action_col:
        accessible_asset_cols = st.columns(5, gap="small")
        for col, key, label in zip(accessible_asset_cols, ["USDJPY", "US100", "XAUUSD", "BTCUSD", "MINIWIN"], ["USD/JPY", "US100 / Nasdaq", "XAU/USD · Ouro", "BTC/USD · Bitcoin", "Mini-Índice · WIN"]):
            with col:
                if st.button(label, key=f"market-access-{key}", type="primary" if asset == key else "secondary"):
                    st.session_state.asset = key
                    st.rerun()
    with market_note_col:
        st.markdown('<div class="card-note" style="text-align:right">Seletor acessível abaixo do cabeçalho.</div>', unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# Spot e pressão partilham a primeira linha, tal como no terminal de referência.
spot_col, pressure_col = st.columns([.78, 2.22], gap="medium")
with spot_col:
    def render_spot_card():
        """Atualiza apenas o cartão Spot em ciclos de 3 segundos, sem recriar os painéis."""
        live_asset = st.session_state.asset
        live_timeframe = st.session_state.timeframe
        live_config = ASSETS[live_asset]
        live_is_usdjpy = live_asset == "USDJPY"
        live_data, live_spot, live_change, live_change_pct, live_mode, _ = load_market_data(live_asset, live_timeframe)
        live_last = float(live_spot if live_spot is not None else live_data.close.iloc[-1])
        if live_spot is not None:
            live_data.loc[live_data.index[-1], "close"] = live_spot
        live_typical = (live_data.high + live_data.low + live_data.close) / 3
        live_vwap = float(np.average(live_typical, weights=live_data.volume))
        live_real = live_mode in {"google", "real", "xtb", "hantec"}
        live_unavailable = live_mode == "unavailable"
        live_previous = float(live_data.close.iloc[-2]) if len(live_data) > 1 else live_last
        if live_mode in {"google", "xtb", "hantec"} and live_change is not None:
            live_change_value = float(live_change)
            live_change_percent = float(live_change_pct or 0.0)
        else:
            live_change_value = live_last - live_previous
            live_change_percent = (live_change_value / live_previous * 100) if live_previous else 0.0
        live_change_class = "quote-change-up" if live_change_value > 0 else "quote-change-down" if live_change_value < 0 else "quote-change-flat"
        live_change_sign = "+" if live_change_value > 0 else ""
        live_source_label = SOURCE_LABELS.get(live_mode, live_mode.upper())
        live_title = f"Cotação {live_source_label} ({live_timeframe})" if live_real else "Cotação indisponível"
        live_badge = f'<span class="badge-green">{live_source_label}</span>' if live_mode in {"google", "xtb", "hantec"} else ('<span class="badge-amber">Backup</span>' if live_mode == "real" else '<span class="badge-red">Sem preço</span>')
        live_clock = dt.datetime.now(TZ).strftime("%H:%M:%S")
        live_note = f"Atualização de {live_source_label} conforme o provedor." if live_real else "Preço real indisponível; nenhum valor simulado é exibido."
        live_value_html = "Indisponível" if live_unavailable else f"{price_format(live_last, live_is_usdjpy)} <span class=\"unit\">{live_config['unit']}</span>"
        live_change_html = "—" if live_unavailable else f"{live_change_sign}{price_format(live_change_value, live_is_usdjpy)} <span>{live_change_sign}{live_change_percent:.2f}%</span>"
        st.markdown(f'''<div class="ui-card spot-card"><div style="display:flex;justify-content:space-between;align-items:center"><div class="eyebrow">{live_title}</div>{live_badge}</div><div class="spot-symbol">{live_config["desk"]}</div><div class="spot-value">{live_value_html}</div><div class="quote-change {live_change_class}">{live_change_html}</div><div class="small-row"><span>VWAP: <strong class="vwap">{price_format(live_vwap, live_is_usdjpy)}</strong></span><span>Fonte: <strong>{live_config["google_name"] if live_mode == "google" else live_source_label}</strong></span></div><div class="rule"></div><div class="small-row"><span>{live_note}</span><strong>{live_clock}</strong></div></div>''', unsafe_allow_html=True)

    render_spot_card()
with pressure_col:
    def render_pressure_card():
        state = live_operational_state()
        bias_badge = '<span class="badge-red">Viés Vendedor Dominante</span>' if state["bearish"] else '<span class="badge-green">Viés Comprador Dominante</span>'
        components = state["pressure_components"]
        component_text = " · ".join(f"{html.escape(name)}: <b>{value:+.2f}</b>" for name, value in components.items())
        st.markdown(f'''<div class="ui-card"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><div><div class="card-title">⌁ Médias de Volume & Pressão ({state["timeframe"]})</div><div class="card-note">MA9: <b>{state["ma9"]:.1f}</b> &nbsp;|&nbsp; MA21: <b>{state["ma21"]:.1f}</b> &nbsp;|&nbsp; MA200: <b>{state["ma200"]:.1f}</b></div></div>{bias_badge}</div><div class="pressure-label" style="color:#2ee59d">Pressão Compradora <span style="float:right">{state["buy"]}%</span></div><div class="bar-shell"><div class="bar-fill-green" style="width:{state["buy"]}%"></div></div><div class="pressure-label" style="color:#fb7185">Pressão Vendedora <span style="float:right">{state["sell"]}%</span></div><div class="bar-shell"><div class="bar-fill-red" style="width:{state["sell"]}%"></div></div><div class="rule"></div><div class="small-row"><span>Volume Ratio: <strong>{state["ratio"]:.1f}x</strong></span><span>Status: <strong style="color:#f7b718">{state["volume_status"]}</strong></span></div><div class="card-note">{component_text}</div><div class="card-note" style="text-align:right">Pesos: indicadores 60% · POC/VA 25% · volume 15% · atualizado a cada 3s</div></div>''', unsafe_allow_html=True)

    render_pressure_card()

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
st.markdown(render_rating_panel(ratings, asset_label, timeframe), unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(f'<div class="card-title">▧ Desempenho Histórico & Backtest ({asset_label})</div><div class="card-note">Teste rápido nas velas de {timeframe}; regra <b>{html.escape(strategy_profile_label)}</b>. Sharpe anualizado por timeframe e drawdown calculado sobre a curva da estratégia. Não representa garantia de desempenho.</div>', unsafe_allow_html=True)
    bt1, bt2, bt3, bt4 = st.columns(4, gap="small")
    with bt1:
        st.metric("Win Rate", f"{win_rate:.0f}%")
    with bt2:
        st.metric("Média PnL", price_format(mean_pnl, is_usdjpy))
    with bt3:
        st.metric("Índice Sharpe", f"{sharpe_ratio:.2f}", help="Retorno médio da estratégia dividido pela volatilidade, anualizado com base no timeframe selecionado.")
    with bt4:
        st.metric("Drawdown máximo", f"{max_drawdown:.2f}%", help="Maior perda percentual da curva de capital em relação ao pico anterior.")
    action_col, export_col, return_col = st.columns([1, 1, 2], gap="small")
    with action_col:
        if st.button("Rodar", key="run-backtest"):
            st.session_state.backtest_result = {"clock": clock, "asset": asset_label}
    with export_col:
        export_columns = ["time", "open", "high", "low", "close", "volume", "direction", "entry_signal", "exit_signal", "exit_reason", "position", "next_return", "next_return_pct", "strategy_return_pct", "strategy_pnl", "win", "rsi", "macd_hist", "adx", "bb_z", "vwap_20", "ema_fast", "ema_slow"]
        export = backtest[export_columns].to_csv(index=False).encode("utf-8")
        st.download_button("CSV", export, file_name=f"backtest_{asset}_{timeframe}.csv", mime="text/csv", key="csv-backtest")
    with return_col:
        st.markdown(f'<div class="small-row" style="padding:7px 0"><span>Retorno total da estratégia</span><strong style="color:{"#2ee59d" if total_return >= 0 else "#fb7185"}">{total_return:+.2f}%</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="small-row" style="margin-top:8px"><span>Operação atual</span><strong style="color:{"#fb7185" if bearish else "#2ee59d"}">{signal} · EM OBSERVAÇÃO</strong><span>Entrada: <b>{price_format(last, is_usdjpy)}</b></span><span>Confiança: <b style="color:#f7b718">{confidence}%</b></span></div>', unsafe_allow_html=True)

    bt_chart_col1, bt_chart_col2 = st.columns(2, gap="small")
    with bt_chart_col1:
        st.markdown('<div class="eyebrow" style="margin-top:12px">Evolução do patrimônio</div><div class="card-note">Curva de patrimônio normalizada em base 100.</div>', unsafe_allow_html=True)
        equity_fig = go.Figure()
        if len(equity_curve):
            equity_fig.add_trace(go.Scatter(x=valid_backtest["time"], y=equity_curve.to_numpy() * 100, mode="lines", name="Patrimônio", line={"color": "#2ee59d", "width": 2}, fill="tozeroy", fillcolor="rgba(46,229,157,.12)", hovertemplate="%{y:.2f}<extra>Patrimônio</extra>"))
            equity_fig.add_hline(y=100, line_color="rgba(255,255,255,.35)", line_dash="dot", line_width=1)
        equity_fig.update_layout(height=220, margin={"l": 8, "r": 8, "t": 8, "b": 8}, paper_bgcolor="#101d31", plot_bgcolor="#101d31", font={"color": "#dbe8f7", "size": 9}, showlegend=False, hovermode="x unified")
        equity_fig.update_yaxes(title="Base 100", gridcolor="rgba(255,255,255,.06)", zeroline=False, tickformat=".1f")
        equity_fig.update_xaxes(gridcolor="rgba(255,255,255,.035)")
        st.plotly_chart(equity_fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False}, key=f"backtest-equity-{asset}-{timeframe}")
    with bt_chart_col2:
        st.markdown('<div class="eyebrow" style="margin-top:12px">Curva de capital</div><div class="card-note">Retorno acumulado da estratégia ao longo das operações.</div>', unsafe_allow_html=True)
        capital_fig = go.Figure()
        if len(equity_curve):
            capital_values = (equity_curve.to_numpy() - 1) * 100
            capital_fig.add_trace(go.Scatter(x=valid_backtest["time"], y=capital_values, mode="lines", name="Capital", line={"color": "#5799ff", "width": 2}, fill="tozeroy", fillcolor="rgba(87,153,255,.12)", hovertemplate="%{y:.2f}%<extra>Capital</extra>"))
            capital_fig.add_hline(y=0, line_color="rgba(255,255,255,.35)", line_dash="dot", line_width=1)
        capital_fig.update_layout(height=220, margin={"l": 8, "r": 8, "t": 8, "b": 8}, paper_bgcolor="#101d31", plot_bgcolor="#101d31", font={"color": "#dbe8f7", "size": 9}, showlegend=False, hovermode="x unified")
        capital_fig.update_yaxes(title="Retorno (%)", gridcolor="rgba(255,255,255,.06)", zeroline=False, ticksuffix="%", tickformat=".1f")
        capital_fig.update_xaxes(gridcolor="rgba(255,255,255,.035)")
        st.plotly_chart(capital_fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False}, key=f"backtest-capital-{asset}-{timeframe}")

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
    @st.fragment(run_every=3)
    def render_alert_card():
        state = live_operational_state()
        signal_badge = '<span class="badge-red">VENDA</span>' if state["bearish"] else '<span class="badge-green">COMPRA</span>'
        operational_text = "Sinal de baixa: volume atual acima das médias MA9 e MA21 com pressão vendedora." if state["bearish"] else "Sinal de alta: volume atual acima das médias MA9 e MA21 com pressão compradora."
        st.markdown(f'''<div class="ui-card"><div style="display:flex;justify-content:space-between;align-items:center"><div class="card-title">◉ Alerta Operacional ({state["label"]})</div>{signal_badge}</div><div class="rule"></div><div class="card-note">{operational_text}</div><div class="rule"></div><div class="small-row"><span>VAH (Resistência)</span><strong style="color:#fb7185">{price_format(state["vah"], state["is_usdjpy"])}</strong></div><div class="small-row"><span>POC (Control)</span><strong style="color:#f7b718">{price_format(state["poc"], state["is_usdjpy"])}</strong></div><div class="small-row"><span>VAL (Suporte)</span><strong style="color:#2ee59d">{price_format(state["val"], state["is_usdjpy"])}</strong></div><div class="small-row"><span>Confiança do Sinal</span><strong style="color:#2ee59d">{state["confidence"]}%</strong></div><div class="rule"></div><div class="card-note" style="text-align:center;font-style:italic">Painel atualizado isoladamente a cada 3 segundos.</div></div>''', unsafe_allow_html=True)

    render_alert_card()

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# Janela operacional: pivôs clássicos derivados da última vela concluída.
pivot_names = [("R3", "#fb7185"), ("R2", "#f58a71"), ("R1", "#f7b718"), ("P", "#eaf2ff"), ("S1", "#45d6c5"), ("S2", "#49a9e8"), ("S3", "#7d8cff")]
nearest_pivot = min(pivots, key=lambda name: abs(last - pivots[name]))
if last >= pivots["R2"]:
    marking_region = "Extensão acima de R2"
elif last >= pivots["R1"]:
    marking_region = "Zona de resistência R1–R2"
elif last >= pivots["P"]:
    marking_region = "Zona compradora P–R1"
elif last >= pivots["S1"]:
    marking_region = "Zona vendedora S1–P"
else:
    marking_region = "Pressão abaixo de S1"

with st.container(border=True):
    pivot_head, pivot_status = st.columns([2.3, 1], vertical_alignment="center")
    with pivot_head:
        st.markdown(f'<div class="card-title">◇ Regiões de Marcação — Pivot Points ({asset_label})</div><div class="card-note">Pivôs clássicos calculados a partir da última vela concluída de <b>{timeframe}</b>; usar como zonas de contexto, não como ordem automática.</div>', unsafe_allow_html=True)
    with pivot_status:
        status_color = "#2ee59d" if last >= pivots["P"] else "#fb7185"
        st.markdown(f'<div class="ui-card" style="padding:9px 11px"><div class="eyebrow">Região ativa</div><div class="card-title" style="color:{status_color};font-size:12px">{marking_region}</div><div class="card-note">Mais próximo: <b>{nearest_pivot}</b> · {price_format(pivots[nearest_pivot], is_usdjpy)}</div></div>', unsafe_allow_html=True)

    pivot_levels_col, pivot_chart_col = st.columns([1.28, 1], gap="medium")
    with pivot_levels_col:
        top_row = st.columns(4, gap="small")
        for col, label in zip(top_row, ["R3", "R2", "R1", "P"]):
            with col:
                st.metric(label, price_format(pivots[label], is_usdjpy))
        bottom_row = st.columns(3, gap="small")
        for col, label in zip(bottom_row, ["S1", "S2", "S3"]):
            with col:
                st.metric(label, price_format(pivots[label], is_usdjpy))
    with pivot_chart_col:
        pivot_fig = go.Figure()
        for label, color in pivot_names:
            pivot_fig.add_hline(y=pivots[label], line_color=color, line_dash="solid" if label == "P" else "dot", line_width=1.3 if label == "P" else 1, annotation_text=f"{label}  {price_format(pivots[label], is_usdjpy)}", annotation_font_color=color, annotation_position="right")
        pivot_fig.add_trace(go.Scatter(x=[0.2, 0.8], y=[last, last], name="Preço atual", mode="lines+markers", line={"color": "#f7b718", "width": 2.4}, marker={"size": 7, "color": "#f7b718"}))
        pivot_range = max(pivots["R3"] - pivots["S3"], 0.001)
        pivot_fig.update_layout(height=235, margin={"l": 5, "r": 84, "t": 5, "b": 5}, paper_bgcolor="#101d31", plot_bgcolor="#101d31", font={"color": "#dbe8f7", "size": 9}, showlegend=False)
        pivot_fig.update_xaxes(visible=False, range=[0, 1])
        pivot_fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False, range=[pivots["S3"] - pivot_range*.08, pivots["R3"] + pivot_range*.08])
        st.plotly_chart(pivot_fig, use_container_width=True, config={"displaylogo": False, "displayModeBar": False})

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
    "BTCUSD": [("10:00 NY", "BTC", "Fluxo e volatilidade cripto", "Médio"), ("14:00 NY", "USD", "Decisão de juros e liquidez", "Alto"), ("18:00 NY", "BTC", "Vencimento de opções", "Médio")],
    "MINIWIN": [("09:00 BRT", "BRL", "Abertura do pregão B3", "Alto"), ("10:00 BRT", "BRL", "Fluxo e ajuste do Ibovespa", "Médio"), ("14:00 BRT", "BRL", "Vencimento/ajuste de índice", "Médio")],
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

with st.container(border=True):
    st.markdown('<div class="card-title">⚙ Status do Feed & Alertas Sonoros</div><div class="card-note">A credencial é gerida exclusivamente em Manage app → Settings → Secrets.</div>', unsafe_allow_html=True)
    secret_loaded = bool(read_secret("TWELVEDATA_API_KEY"))
    feed_status_col, sound_col = st.columns([1.25, 1], gap="small")
    with feed_status_col:
        feed_color = "#2ee59d" if feed_mode in {"google", "xtb", "hantec"} else ("#f7c948" if feed_mode == "real" else "#fb7185")
        feed_label = f"{source_label} ativo" if feed_mode in {"google", "xtb", "hantec"} else ("Backup TwelveData" if feed_mode == "real" else "Preço real indisponível")
        st.markdown(f'<div class="metric-cell"><span>Estado do feed</span><b style="color:{feed_color}">{feed_label}</b><span style="margin-top:6px;text-transform:none;font-weight:500">{html.escape(feed_note)}</span></div>', unsafe_allow_html=True)
    with sound_col:
        st.session_state.sound_alerts = st.toggle("Alertas sonoros de Compra/Venda", value=st.session_state.sound_alerts, key="sound-toggle")
    st.markdown(f'<div class="card-note">{"Google Finance é consultado sem chave; TwelveData é usado apenas como backup de candles quando disponível." if feed_mode == "google" else ("TwelveData foi usado como backup." if secret_loaded and feed_mode == "real" else "Google Finance não devolveu cotação nesta execução; revise a disponibilidade do provedor.")}</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer-note">Terminal Institucional · {asset_label} · {feed_note} {refresh_footer}</div>', unsafe_allow_html=True)
