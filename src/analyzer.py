import os
from groq import Groq


def generate_newsletter(sector_data, index_data, news_data, weekly=False):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    market_summary = _build_market_summary(sector_data, index_data, news_data, weekly)

    if weekly:
        prompt = f"""Ès um analista financeiro sénior que escreve uma newsletter semanal de mercados.
Com base nos dados abaixo, gera o CONTEÚDO da newsletter semanal em HTML (apenas o conteúdo, sem <html>, <head> ou <body>).

A newsletter deve ter:
1. Um parágrafo de abertura com o resumo geral da semana (tom profissional mas acessível)
2. Para cada setor, uma secção com:
   - Título do setor com emoji
   - Tabela com todas as ações (nome, ticker, preço atual, variação semanal %)
   - Análise de 2-3 frases sobre o setor esta semana
   - Destaques: os maiores movimentos com contexto das notícias
3. Secção de Índices com tabela (nome, valor, variação semanal %)
4. Secção "Perspetiva Semanal" com tendências e o que esperar na próxima semana

Usa cores: verde (#10b981) para subidas, vermelho (#ef4444) para descidas.
Estilo clean e profissional. Tabelas com borders subtis.
Escreve em Português de Portugal.
Retorna APENAS o HTML, sem markdown code blocks.

DADOS DA SEMANA:
{market_summary}"""
    else:
        prompt = f"""Ès um analista financeiro sénior que escreve uma newsletter diária de mercados.
Com base nos dados abaixo, gera o CONTEÚDO da newsletter em HTML (apenas o conteúdo, sem <html>, <head> ou <body>).

A newsletter deve ter:
1. Um parágrafo de abertura com o resumo do dia (tom profissional mas acessível)
2. Para cada setor, uma secção com:
   - Título do setor com emoji
   - Tabela com todas as ações (nome, ticker, preço, variação %)
   - Análise de 2-3 frases sobre o setor
   - Destaques: os maiores movimentos e porquê (usa as notícias como contexto)
3. Secção de Índices com tabela (nome, valor, variação %)
4. Secção "Outlook" com o que observar amanhã

Usa cores: verde (#10b981) para subidas, vermelho (#ef4444) para descidas.
Estilo clean e profissional. Tabelas com borders subtis.
Escreve em Português de Portugal.
Retorna APENAS o HTML, sem markdown code blocks.

DADOS DO DIA:
{market_summary}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.3,
    )

    text = response.choices[0].message.content
    if text.startswith("```html"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _build_market_summary(sector_data, index_data, news_data, weekly=False):
    lines = []

    lines.append("=== ÍNDICES ===")
    for idx in index_data:
        period = "semanal" if weekly else "diária"
        lines.append(f"{idx['name']}: {idx['value']} ({idx['change_pct']:+.2f}% variação {period})")

    for sector, data in sector_data.items():
        lines.append(f"\n=== {data['emoji']} {sector.upper()} ===")
        for stock in data["stocks"]:
            change_label = "semanal" if weekly else "diária"
            line = f"{stock['name']} ({stock['ticker']}): ${stock['price']} ({stock['change_pct']:+.2f}% {change_label})"
            if weekly and "week_high" in stock:
                line += f" | Máx: ${stock['week_high']} Mín: ${stock['week_low']}"
            lines.append(line)

        lines.append(f"\nTop Movers {sector}:")
        for mover in data["top_movers"]:
            lines.append(f"  → {mover['name']} ({mover['ticker']}): {mover['change_pct']:+.2f}%")

        if sector in news_data:
            lines.append(f"\nNotícias {sector}:")
            for company_news in news_data[sector]:
                for article in company_news["articles"]:
                    source = f" ({article['source']})" if article["source"] else ""
                    lines.append(f"  - [{company_news['ticker']}] {article['title']}{source}")

    return "\n".join(lines)
