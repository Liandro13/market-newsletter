from datetime import datetime, timedelta
import yfinance as yf
from config import SECTORS, INDICES, TOP_MOVERS_PER_SECTOR


def fetch_sector_data(period="1d"):
    results = {}
    all_tickers = []
    for sector, info in SECTORS.items():
        all_tickers.extend(info["tickers"])

    data = yf.download(all_tickers, period="5d", group_by="ticker", progress=False)

    for sector, info in SECTORS.items():
        sector_data = []
        for ticker in info["tickers"]:
            try:
                if len(all_tickers) == 1:
                    ticker_data = data
                else:
                    ticker_data = data[ticker]

                closes = ticker_data["Close"].dropna()
                if len(closes) < 2:
                    continue

                current = closes.iloc[-1]
                previous = closes.iloc[-2]
                change_pct = ((current - previous) / previous) * 100
                volume = ticker_data["Volume"].iloc[-1]

                stock = yf.Ticker(ticker)
                name = stock.info.get("shortName", ticker)

                sector_data.append({
                    "ticker": ticker,
                    "name": name,
                    "price": round(current, 2),
                    "change_pct": round(change_pct, 2),
                    "volume": int(volume) if volume == volume else 0,
                    "previous_close": round(previous, 2),
                })
            except Exception:
                continue

        sector_data.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        results[sector] = {
            "emoji": info["emoji"],
            "stocks": sector_data,
            "top_movers": sector_data[:TOP_MOVERS_PER_SECTOR],
        }

    return results


def fetch_index_data():
    tickers = list(INDICES.values())
    data = yf.download(tickers, period="5d", group_by="ticker", progress=False)

    results = []
    for name, ticker in INDICES.items():
        try:
            if len(tickers) == 1:
                ticker_data = data
            else:
                ticker_data = data[ticker]

            closes = ticker_data["Close"].dropna()
            if len(closes) < 2:
                continue

            current = closes.iloc[-1]
            previous = closes.iloc[-2]
            change_pct = ((current - previous) / previous) * 100

            results.append({
                "name": name,
                "ticker": ticker,
                "value": round(current, 2),
                "change_pct": round(change_pct, 2),
                "previous_close": round(previous, 2),
            })
        except Exception:
            continue

    return results


def fetch_weekly_data():
    results = {}
    all_tickers = []
    for sector, info in SECTORS.items():
        all_tickers.extend(info["tickers"])

    data = yf.download(all_tickers, period="5d", group_by="ticker", progress=False)

    for sector, info in SECTORS.items():
        sector_data = []
        for ticker in info["tickers"]:
            try:
                if len(all_tickers) == 1:
                    ticker_data = data
                else:
                    ticker_data = data[ticker]

                closes = ticker_data["Close"].dropna()
                if len(closes) < 2:
                    continue

                current = closes.iloc[-1]
                week_start = closes.iloc[0]
                change_pct = ((current - week_start) / week_start) * 100
                high = ticker_data["High"].max()
                low = ticker_data["Low"].min()

                stock = yf.Ticker(ticker)
                name = stock.info.get("shortName", ticker)

                sector_data.append({
                    "ticker": ticker,
                    "name": name,
                    "price": round(current, 2),
                    "change_pct": round(change_pct, 2),
                    "week_high": round(float(high), 2),
                    "week_low": round(float(low), 2),
                    "week_start": round(float(week_start), 2),
                })
            except Exception:
                continue

        sector_data.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        results[sector] = {
            "emoji": info["emoji"],
            "stocks": sector_data,
            "top_movers": sector_data[:TOP_MOVERS_PER_SECTOR],
        }

    return results


def fetch_weekly_index_data():
    tickers = list(INDICES.values())
    data = yf.download(tickers, period="5d", group_by="ticker", progress=False)

    results = []
    for name, ticker in INDICES.items():
        try:
            if len(tickers) == 1:
                ticker_data = data
            else:
                ticker_data = data[ticker]

            closes = ticker_data["Close"].dropna()
            if len(closes) < 2:
                continue

            current = closes.iloc[-1]
            week_start = closes.iloc[0]
            change_pct = ((current - week_start) / week_start) * 100

            results.append({
                "name": name,
                "ticker": ticker,
                "value": round(current, 2),
                "change_pct": round(change_pct, 2),
                "week_start": round(float(week_start), 2),
            })
        except Exception:
            continue

    return results
