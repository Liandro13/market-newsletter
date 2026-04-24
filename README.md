<h1 align="center">📈 Market Newsletter</h1>
<p align="center">
  Newsletter diária automática com análise dos mercados financeiros
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>
  <img src="https://img.shields.io/badge/Resend-000000?style=for-the-badge&logoColor=white"/>
</p>

---

## 📋 Sobre o Projeto

O **Market Newsletter** é um pipeline automatizado que corre diariamente via GitHub Actions, recolhe dados de mercados financeiros (ações, índices, cripto) com `yfinance`, analisa-os com um LLM via Groq API, e envia o resultado por email com Resend.

## ⚙️ Como Funciona

```
⏰ GitHub Actions (schedule diário)
    ↓
📊 yfinance — recolha de dados de mercado
    ↓
🤖 Groq API (LLM) — análise e redação da newsletter
    ↓
📧 Resend — envio por email
```

## ✨ Funcionalidades

- **Automático** — corre todos os dias sem intervenção manual
- **Dados em tempo real** — cotações, variações, volumes via yfinance
- **Análise com IA** — narrativa gerada por LLM (Groq)
- **Envio de email** — entregue diretamente na caixa de entrada via Resend
- **100% gratuito** — ferramentas no plano free tier

## 🛠️ Tecnologias

| Ferramenta | Função |
|---|---|
| `yfinance` | Recolha de dados financeiros (Yahoo Finance) |
| `Groq API` | Inferência LLM de alta velocidade |
| `Resend` | Envio transacional de emails |
| `GitHub Actions` | Agendamento e execução automática |

## 🔑 Configuração

Adiciona os seguintes **Secrets** ao repositório GitHub (`Settings → Secrets → Actions`):

| Secret | Descrição |
|---|---|
| `GROQ_API_KEY` | Chave da API Groq |
| `RESEND_API_KEY` | Chave da API Resend |
| `EMAIL_TO` | Email de destino da newsletter |

## 🚀 Como Executar Localmente

```bash
# Clonar o repositório
git clone https://github.com/Liandro13/market-newsletter.git
cd market-newsletter

# Instalar dependências
pip install yfinance groq resend

# Configurar variáveis de ambiente
export GROQ_API_KEY="..."
export RESEND_API_KEY="..."
export EMAIL_TO="..."

# Correr
python main.py
```

## ⏰ Agendamento

O workflow GitHub Actions está configurado para correr automaticamente todos os dias úteis. Podes ajustar o cron em `.github/workflows/newsletter.yml`.
