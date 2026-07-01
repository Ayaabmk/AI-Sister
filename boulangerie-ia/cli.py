"""
Interface CLI simple pour l'agent boulangerie.
Lancement : python cli.py
"""
import sys
from langchain_core.messages import HumanMessage, AIMessage

from agent import get_agent

BANNER = """
╔══════════════════════════════════════════════════════════╗
║   🥐  Chez Madeleine – Assistant Boulangerie IA  🥐     ║
╚══════════════════════════════════════════════════════════╝
Bonjour Madeleine ! Tape ta question et appuie sur Entrée.
(tape 'quitter' ou Ctrl+C pour sortir)
"""

def run():
    print(BANNER)
    agent = get_agent()
    history = []

    while True:
        try:
            user_input = input("\nMadeleine : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nBonne journée Madeleine ! À demain ! 🥐")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("quitter", "quit", "exit", "q"):
            print("\nBonne journée Madeleine ! À demain ! 🥐")
            break

        history.append(HumanMessage(content=user_input))
        print("\nAssistant : (je cherche…)")

        try:
            result = agent.invoke({"messages": history})
            ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
            response = ai_messages[-1].content if ai_messages else "Désolé, je n'ai pas pu traiter ta demande."
        except Exception as e:
            response = f"⚠️ Erreur : {e}"

        print(f"\nAssistant : {response}")
        history.append(AIMessage(content=response))


if __name__ == "__main__":
    run()
