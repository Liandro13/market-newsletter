import feedparser
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=pt-PT&gl=PT&ceid=PT:pt"


def fetch_news_for_company(company_name, ticker, max_results=3):
    query = urllib.parse.quote(f"{company_name} stock")
    url = GOOGLE_NEWS_RSS.format(query=query)

    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:max_results]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", ""),
            })
        return {"ticker": ticker, "company": company_name, "articles": articles}
    except Exception:
        return {"ticker": ticker, "company": company_name, "articles": []}


def fetch_news_for_movers(sector_data):
    all_movers = []
    for sector, data in sector_data.items():
        for mover in data.get("top_movers", []):
            all_movers.append((mover["name"], mover["ticker"], sector))

    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_news_for_company, name, ticker): (ticker, sector)
            for name, ticker, sector in all_movers
        }
        for future in as_completed(futures):
            ticker, sector = futures[future]
            try:
                news = future.result()
                if sector not in results:
                    results[sector] = []
                results[sector].append(news)
            except Exception:
                continue

    return results
