import os

RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "liandrodacruz@outlook.pt")
SENDER_EMAIL = "newsletter@resend.dev"

SECTORS = {
    "Tecnologia": {
        "tickers": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMZN", "ASML", "SAP", "TSM", "AVGO"],
        "emoji": "💻",
    },
    "Indústria": {
        "tickers": ["SIE.DE", "CAT", "HON", "GE", "MMM", "ABBN.SW", "SU.PA"],
        "emoji": "🏭",
    },
    "Telecomunicações": {
        "tickers": ["DTE.DE", "VOD", "T", "VZ", "ORA.PA", "TMUS"],
        "emoji": "📡",
    },
    "Serviços": {
        "tickers": ["ACN", "CRM", "UBER", "NOW", "INFY", "WIT"],
        "emoji": "🏢",
    },
    "Banca": {
        "tickers": ["JPM", "GS", "SAN", "BNP.PA", "HSBC", "DB", "MS", "BAC"],
        "emoji": "🏦",
    },
}

INDICES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "FTSE 100": "^FTSE",
    "DAX": "^GDAXI",
    "Euro Stoxx 50": "^STOXX50E",
    "CAC 40": "^FCHI",
    "Nikkei 225": "^N225",
    "PSI": "PSI20.LS",
}

TOP_MOVERS_PER_SECTOR = 3
