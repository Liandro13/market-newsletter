import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from groq import Groq

TODAY = datetime.now().strftime("%d/%m/%Y")

SYSTEM_MSG = f"""Ès um analista financeiro sénior. Hoje é {TODAY}.

LINGUAGEM: Português de PORTUGAL (PT-PT). Usa "procura" (não "demanda"), "económica" (não "econômica"), "registou" (não "registrou").

REGRAS:
- As tabelas mostram OS DADOS. O texto explica O PORQUÊ. NUNCA repitas variações ou preços no texto.
- Liga notícias a movimentos: "SAP caiu após resultados Q1 abaixo das expectativas (Reuters)."
- Se não há notícia, diz "sem catalisador identificado" — NUNCA inventes.
- PROIBIDO: "queda na procura por serviços de X", "concorrência no setor", "dia misto", "volatilidade" sem causa.
- No OUTLOOK, menciona APENAS eventos que tens a certeza que existem. Se não sabes a data exacta, diz "próximos dias" — NUNCA inventes datas."""

SECTOR_PROMPT = """Gera a secção HTML para o setor {sector_name}.

Gera APENAS:
1. <h2>{emoji} {sector_name}</h2>
2. Tabela com colunas: Nome | Ticker | Preço | Dia % | Sem % | Mês % | Ano %
   - Variações com cor: verde (#10b981) positivas, vermelho (#ef4444) negativas
   - Tabela compacta, font-size: 13px, borders: #e2e8f0
3. Análise ({num_sentences} frases): Só causas baseadas nas notícias. Cita fontes entre parênteses. Não repitas dados da tabela.

Retorna APENAS HTML, sem markdown code blocks.

DADOS:
{data}"""

AGGREGATE_PROMPT = """Combina as secções abaixo numa newsletter final.

ESTRUTURA:
1. ABERTURA (2-3 frases): Tema dominante. Usa números dos índices.
2. ÍNDICES: Tabela (Nome | Valor | Dia % | Sem % | Mês % | Ano %). 1 frase sobre o driver.
3. SETORES: Coloca as secções pela ordem fornecida. NÃO alteres tabelas nem análises.
4. DESTAQUES ({highlight_title}): {highlight_count} movimentos mais significativos cross-sector. Lista HTML (<ul><li>). Formato: "<strong>TICKER</strong> (variação dia%): razão em 1 frase."
5. {outlook_title}: {outlook_desc}. USA LISTA HTML (<ul><li>).

Retorna APENAS HTML, sem markdown code blocks.

ÍNDICES:
{indices}

SECÇÕES:
{sections}"""


GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]


def _call_gemini(prompt, system_msg, max_tokens=2500):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    client = genai.Client(api_key=api_key)
    full_prompt = f"{system_msg}\n\n{prompt}"
    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
            )
            return response.text
        except Exception as e:
            err = str(e)[:80]
            if "503" in err or "429" in err or "UNAVAILABLE" in err or "EXHAUSTED" in err:
                print(f"   Gemini {model} indisponível, tentando próximo...")
                continue
            raise
    raise RuntimeError("Gemini models all unavailable")


def _call_groq(prompt, system_msg, max_tokens=2500):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    client = Groq(api_key=api_key)
    for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.15,
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                continue
            raise
    raise RuntimeError("Groq models all rate limited")


def _call_llm(prompt, max_tokens=2500):
    providers = [
        ("Gemini", _call_gemini),
        ("Groq", _call_groq),
    ]
    for name, fn in providers:
        try:
            return fn(prompt, SYSTEM_MSG, max_tokens)
        except Exception as e:
            print(f"   {name} falhou: {type(e).__name__}: {str(e)[:80]}")
            continue
    raise RuntimeError("Todos os providers falharam.")


def _clean(text):
    for prefix in ["```html", "```"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def generate_newsletter(sector_data, index_data, news_data, weekly=False):
    def _analyze_sector(sector, data):
        sector_text = _build_sector_data(sector, data, news_data.get(sector, []))
        num_sentences = "3-4" if weekly else "2-3"
        prompt = SECTOR_PROMPT.format(
            sector_name=sector,
            emoji=data["emoji"],
            num_sentences=num_sentences,
            data=sector_text,
        )
        print(f"   Analisando {data['emoji']} {sector}...")
        return sector, _clean(_call_llm(prompt, max_tokens=2500))

    sector_order = list(sector_data.keys())
    sector_results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(_analyze_sector, sector, data): sector
            for sector, data in sector_data.items()
        }
        for future in as_completed(futures):
            try:
                sector, html = future.result()
                sector_results[sector] = html
            except Exception as e:
                sector = futures[future]
                print(f"   {sector} falhou: {e}")
                sector_results[sector] = ""

    sector_htmls = [sector_results[s] for s in sector_order if sector_results.get(s)]
    index_text = _build_index_data(index_data)

    if weekly:
        highlight_title = "VENCEDORES E PERDEDORES"
        highlight_count = "Top 5 melhores e Top 5 piores"
        outlook_title = "PERSPETIVA SEMANAL"
        outlook_desc = "Eventos concretos da próxima semana. Só eventos que tens a certeza. NUNCA inventes datas"
    else:
        highlight_title = "DESTAQUES DO DIA"
        highlight_count = "3-5"
        outlook_title = "OUTLOOK"
        outlook_desc = "3-4 eventos a monitorizar. Só eventos reais que conheças. NUNCA inventes datas"

    agg_prompt = AGGREGATE_PROMPT.format(
        highlight_title=highlight_title,
        highlight_count=highlight_count,
        outlook_title=outlook_title,
        outlook_desc=outlook_desc,
        indices=index_text,
        sections="\n\n".join(sector_htmls),
    )

    print("   Agregando newsletter final...")
    return _clean(_call_llm(agg_prompt, max_tokens=5000))


def _build_sector_data(sector, data, news_list):
    lines = []
    lines.append("Ações (preço | dia% | sem% | mês% | ano%):")
    for stock in data["stocks"]:
        line = (
            f"  {stock['name']} ({stock['ticker']}): "
            f"${stock['price']} | "
            f"Dia: {stock.get('change_1d', 0):+.2f}% | "
            f"Sem: {stock.get('change_5d', 0):+.2f}% | "
            f"Mês: {stock.get('change_1m', 0):+.2f}% | "
            f"Ano: {stock.get('change_1y', 0):+.2f}%"
        )
        lines.append(line)

    if news_list:
        lines.append("\nNotícias:")
        for company_news in news_list:
            for article in company_news["articles"]:
                source = f" — {article['source']}" if article["source"] else ""
                lines.append(f"  [{company_news['ticker']}] {article['title']}{source}")
                snippet = article.get("snippet", "")
                if snippet:
                    lines.append(f"    {snippet[:300]}")

    return "\n".join(lines)


def _build_index_data(index_data):
    lines = []
    for idx in index_data:
        lines.append(
            f"{idx['name']}: {idx.get('price', idx.get('value', 0))} | "
            f"Dia: {idx.get('change_1d', 0):+.2f}% | "
            f"Sem: {idx.get('change_5d', 0):+.2f}% | "
            f"Mês: {idx.get('change_1m', 0):+.2f}% | "
            f"Ano: {idx.get('change_1y', 0):+.2f}%"
        )
    return "\n".join(lines)
