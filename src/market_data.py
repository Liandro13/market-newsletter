import yfinance as yf
import numpy as np
from config import SECTORS, INDICES, TOP_MOVERS_PER_SECTOR


def _pct_change(current, reference):
    if reference == 0 or np.isnan(reference) or np.isnan(current):
        return 0.0
    return round(((current - reference) / reference) * 100, 2)


def _get_reference_close(closes, days_back):
    if len(closes) <= days_back:
        return closes.iloc[0]
    return closes.iloc[-(days_back + 1)]


def _compute_variations(closes):
    if len(closes) < 2:
        return {}
    current = closes.iloc[-1]
    return {
        "price": round(current, 2),
        "change_1d": _pct_change(current, closes.iloc[-2]) if len(closes) >= 2 else 0,
        "change_5d": _pct_change(current, _get_reference_close(closes, 5)),
        "change_1m": _pct_change(current, _get_reference_close(closes, 22)),
        "change_1y": _pct_change(current, closes.iloc[0]),
    }


def fetch_sector_data(period="1d"):
    all_tickers = []
    for sector, info in SECTORS.items():
        all_tickers.extend(info["tickers"])

    data = yf.download(all_tickers, period="1y", group_by="ticker", progress=False)

    names_cache = {}
    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            names_cache[ticker] = stock.info.get("shortName", ticker)
        except Exception:
            names_cache[ticker] = ticker

    results = {}
    for sector, info in SECTORS.items():
        sector_data = []
        for ticker in info["tickers"]:
            try:
                ticker_data = data[ticker] if len(all_tickers) > 1 else data
                closes = ticker_data["Close"].dropna()
                if len(closes) < 2:
                    continue

                variations = _compute_variations(closes)
                volume = ticker_data["Volume"].iloc[-1]

                sector_data.append({
                    "ticker": ticker,
                    "name": names_cache.get(ticker, ticker),
                    "volume": int(volume) if volume == volume else 0,
                    **variations,
                })
            except Exception:
                continue

        sector_data.sort(key=lambda x: abs(x.get("change_1d", 0)), reverse=True)
        results[sector] = {
            "emoji": info["emoji"],
            "stocks": sector_data,
            "top_movers": sector_data[:TOP_MOVERS_PER_SECTOR],
        }

    return results


def fetch_index_data():
    tickers = list(INDICES.values())
    data = yf.download(tickers, period="1y", group_by="ticker", progress=False)

    results = []
    for name, ticker in INDICES.items():
        try:
            ticker_data = data[ticker] if len(tickers) > 1 else data
            closes = ticker_data["Close"].dropna()
            if len(closes) < 2:
                continue

            variations = _compute_variations(closes)
            results.append({"name": name, "ticker": ticker, **variations})
        except Exception:
            continue

    return results


def fetch_weekly_data():
    return fetch_sector_data()


def fetch_weekly_index_data():
    return fetch_index_data()
