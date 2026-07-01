import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DB_IDS = {
    "stocks":    os.getenv("NOTION_DB_STOCKS", ""),
    "catalogue": os.getenv("NOTION_DB_CATALOGUE", ""),
    "ventes":    os.getenv("NOTION_DB_VENTES", ""),
    "commandes": os.getenv("NOTION_DB_COMMANDES", ""),
}

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM    = os.getenv("EMAIL_FROM", SMTP_USER)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BAKERY_CITY         = os.getenv("BAKERY_CITY", "Montpellier")
