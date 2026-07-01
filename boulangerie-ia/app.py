"""
Interface Chainlit pour l'agent boulangerie de Madeleine.
Lancement : chainlit run app.py
"""
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage

from agent import get_agent

WELCOME_MSG = """## 🥐 Bonjour Madeleine !

Je suis ton **assistant boulangerie**, propulsé par AI Sisters.

Voici ce que je peux faire pour toi :

| | |
|---|---|
| 📦 | **Consulter tes stocks** — "Il me reste combien de beurre ?" |
| 📊 | **Analyser tes ventes** — "Combien de croissants j'ai vendus ?" |
| 📧 | **Commander un fournisseur** — "Commande 50kg de farine T65" |
| 🔮 | **Préparer demain** — "Qu'est-ce que je dois préparer ?" |

---
*Que puis-je faire pour toi aujourd'hui ?* ✨"""


@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message(content=WELCOME_MSG, author="Assistant").send()


@cl.on_message
async def main(message: cl.Message):
    history: list = cl.user_session.get("history", [])
    history.append(HumanMessage(content=message.content))

    agent = get_agent()

    # Message "en cours" pendant que l'agent réfléchit / appelle les tools
    thinking_msg = cl.Message(content="", author="Assistant")
    await thinking_msg.send()

    try:
        result = agent.invoke({"messages": history})
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        response_text = ai_messages[-1].content if ai_messages else "Je n'ai pas pu traiter ta demande."

        # Mettre à jour le message avec la réponse finale
        thinking_msg.content = response_text
        await thinking_msg.update()

        # Ajouter la réponse à l'historique
        history.append(AIMessage(content=response_text))
        cl.user_session.set("history", history)

    except Exception as e:
        thinking_msg.content = f"⚠️ Une erreur s'est produite : {e}"
        await thinking_msg.update()
