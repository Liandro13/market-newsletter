import feedparser
import urllib.parse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
YAHOO_NEWS_RSS = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def _extract_snippet(url, timeout=5):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        paragraphs = soup.find_all("p")
        text_parts = []
        for p in paragraphs[:5]:
            text = p.get_text(strip=True)
            if len(text) > 40:
                text_parts.append(text)
        return " ".join(text_parts)[:500]
    except Exception:
        return ""


def fetch_news_for_company(company_name, ticker, max_results=3):
    articles = []

    query = urllib.parse.quote(f"{company_name} stock market")
    google_url = GOOGLE_NEWS_RSS.format(query=query)
    try:
        feed = feedparser.parse(google_url)
        for entry in feed.entries[:max_results]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", ""),
                "snippet": "",
            })
    except Exception:
        pass

    yahoo_url = YAHOO_NEWS_RSS.format(ticker=ticker)
    try:
        feed = feedparser.parse(yahoo_url)
        seen_titles = {a["title"].lower() for a in articles}
        for entry in feed.entries[:2]:
            title = entry.get("title", "")
            if title.lower() not in seen_titles:
                articles.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": "Yahoo Finance",
                    "snippet": entry.get("summary", "")[:300],
                })
    except Exception:
        pass

    for article in articles[:2]:
        if not article["snippet"] and article["link"]:
            article["snippet"] = _extract_snippet(article["link"])

    return {"ticker": ticker, "company": company_name, "articles": articles[:4]}


def fetch_news_for_movers(sector_data):
    all_stocks = []
    for sector, data in sector_data.items():
        for stock in data.get("stocks", []):
            all_stocks.append((stock["name"], stock["ticker"], sector))

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_news_for_company, name, ticker): (ticker, sector)
            for name, ticker, sector in all_stocks
        }
        for future in as_completed(futures):
            ticker, sector = futures[future]
            try:
                news = future.result()
                if news["articles"]:
                    if sector not in results:
                        results[sector] = []
                    results[sector].append(news)
            except Exception:
                continue

    return results
