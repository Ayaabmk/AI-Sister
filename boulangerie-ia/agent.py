"""
Agent conversationnel pour la boulangerie de Madeleine Croûton.
Architecture : LangGraph ReAct agent + Llama 3.3 70B (Groq) + 5 tools Notion/email/forecast.
"""
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

from config import GROQ_API_KEY
from tools import ALL_TOOLS

SYSTEM_PROMPT = """Tu es l'assistant IA de la boulangerie "Chez Madeleine" à Saint-Germain-des-Croissants.
Tu aides Madeleine Croûton, boulangère depuis 32 ans, à gérer son commerce.

Règles :
- Toujours utiliser un outil pour répondre aux questions sur les stocks, les ventes ou les prix. Ne devine jamais.
- Avant d'envoyer un email de commande, résume et demande confirmation.
- Si un stock est sous le seuil d'alerte, signale-le clairement.
- Réponds en français, de façon courte et pratique. Pas de jargon technique.
- Tutoie Madeleine chaleureusement.
"""


def build_agent():
    """Construit et retourne l'agent LangGraph."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.3,
    )
    return create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )


# Singleton utilisé par app.py
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent
