import sys
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from market_data import (
    fetch_sector_data,
    fetch_index_data,
    fetch_weekly_data,
    fetch_weekly_index_data,
)
from news_fetcher import fetch_news_for_movers
from analyzer import generate_newsletter
from email_sender import send_newsletter


def build_email_html(content, weekly=False):
    template_path = Path(__file__).parent.parent / "templates" / "newsletter.html"
    template = Template(template_path.read_text(encoding="utf-8"))

    today = datetime.now()
    if weekly:
        subtitle = "Resumo Semanal de Mercados"
        date = f"Semana de {today.strftime('%d/%m/%Y')}"
        title = f"📊 Market Pulse — Resumo Semanal"
    else:
        subtitle = "Análise Diária de Mercados"
        date = today.strftime("%A, %d de %B de %Y")
        title = f"📊 Market Pulse — {today.strftime('%d/%m/%Y')}"

    return template.render(
        title=title,
        subtitle=subtitle,
        date=date,
        content=content,
    )


def run_daily():
    print("📈 A recolher dados de mercado...")
    sector_data = fetch_sector_data()
    index_data = fetch_index_data()

    print("📰 A procurar notícias dos top movers...")
    news_data = fetch_news_for_movers(sector_data)

    print("🤖 A gerar newsletter com Claude...")
    content = generate_newsletter(sector_data, index_data, news_data, weekly=False)

    print("✉️  A enviar email...")
    html = build_email_html(content, weekly=False)
    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"📊 Market Pulse — {today}"
    result = send_newsletter(html, subject)

    print(f"✅ Newsletter enviada! ID: {result}")


def run_weekly():
    print("📈 A recolher dados semanais...")
    sector_data = fetch_weekly_data()
    index_data = fetch_weekly_index_data()

    print("📰 A procurar notícias dos top movers...")
    news_data = fetch_news_for_movers(sector_data)

    print("🤖 A gerar resumo semanal com Claude...")
    content = generate_newsletter(sector_data, index_data, news_data, weekly=True)

    print("✉️  A enviar email...")
    html = build_email_html(content, weekly=True)
    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"📊 Market Pulse — Resumo Semanal {today}"
    result = send_newsletter(html, subject)

    print(f"✅ Resumo semanal enviado! ID: {result}")


if __name__ == "__main__":
    weekly = "--weekly" in sys.argv
    if weekly:
        run_weekly()
    else:
        run_daily()
