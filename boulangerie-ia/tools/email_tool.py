"""
Tool 4 (obligatoire) — Envoi d'email + enregistrement dans Notion.
Génère un email de commande fournisseur, l'envoie via SMTP,
et enregistre la commande dans la table "Commandes Fournisseurs" Notion.
"""
import json
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from langchain_core.tools import tool
from notion_client import Client
from notion_client.errors import APIResponseError

from config import (
    NOTION_TOKEN, NOTION_DB_IDS,
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM,
)

_notion = Client(auth=NOTION_TOKEN)


def _send_smtp(to_email: str, subject: str, body_html: str, body_text: str) -> tuple[bool, str]:
    """Envoie un email via SMTP. Retourne (succès, message)."""
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, (
            "⚠️  Simulation : aucune config SMTP trouvée dans .env. "
            f"L'email AURAIT été envoyé à {to_email} avec le sujet : '{subject}'.\n\n"
            f"Contenu :\n{body_text}"
        )
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = EMAIL_FROM or SMTP_USER
        msg["To"]      = to_email
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True, f"Email envoyé avec succès à {to_email}"
    except Exception as e:
        return False, f"Erreur SMTP : {e}"


def _enregistrer_notion(
    fournisseur: str,
    produit: str,
    quantite: str,
    prix_unitaire: float,
    email_fournisseur: str,
    notes: str,
) -> str:
    """Crée une entrée dans la table Commandes Fournisseurs de Notion.
    Colonnes réelles : Référence commande (title), Fournisseur (select),
    Produits commandés (rich_text), Montant estimé (€) (number),
    Email envoyé à (email), Date commande (date), Statut (select), Notes (rich_text).
    """
    try:
        montant_str = quantite.split()[0].replace(",", ".")
        try:
            montant = round(float(montant_str) * prix_unitaire, 2)
        except ValueError:
            montant = 0.0

        ref = f"CMD-{datetime.now().strftime('%Y%m%d-%H%M')}"
        detail = f"{produit} – {quantite} × {prix_unitaire} €"
        if notes:
            detail += f" | {notes}"

        props: dict = {
            "Référence commande": {
                "title": [{"text": {"content": ref}}]
            },
            "Fournisseur": {
                "select": {"name": fournisseur}
            },
            "Produits commandés": {
                "rich_text": [{"text": {"content": detail}}]
            },
            "Montant estimé (€)": {"number": montant},
            "Email envoyé à":     {"email": email_fournisseur},
            "Date commande":      {"date": {"start": datetime.now().date().isoformat()}},
            "Statut":             {"select": {"name": "Envoyée"}},
        }
        if notes:
            props["Notes"] = {"rich_text": [{"text": {"content": notes}}]}

        page = _notion.pages.create(
            parent={"database_id": NOTION_DB_IDS["commandes"]},
            properties=props,
        )
        return f"✅ Commande {ref} enregistrée dans Notion (ID : {page['id'][:8]}…)"
    except APIResponseError as e:
        return f"⚠️  Notion error {e.status} : {e.message}"
    except Exception as e:
        return f"⚠️  Erreur Notion : {e}"


@tool
def envoyer_commande_fournisseur(
    fournisseur: str,
    email_fournisseur: str,
    produit: str,
    quantite: str,
    prix_unitaire: float,
    notes: str = "",
) -> str:
    """Envoie un email de commande à un fournisseur ET enregistre la commande dans Notion.

    Args:
        fournisseur:      Nom du fournisseur (ex: "Minoterie Dupont")
        email_fournisseur: Email du fournisseur (ex: "contact@minoterie-dupont.fr")
        produit:          Produit commandé (ex: "Farine T65")
        quantite:         Quantité avec unité (ex: "50 kg", "200 unités")
        prix_unitaire:    Prix unitaire en euros (ex: 0.85 pour 0,85 €/kg)
        notes:            Instructions ou précisions supplémentaires (optionnel)

    Retourne un résumé de l'envoi et de l'enregistrement Notion.
    """
    today = datetime.now().strftime("%d/%m/%Y")

    body_text = f"""Bonjour,

Suite à notre échange, nous souhaitons passer la commande suivante :

  Produit   : {produit}
  Quantité  : {quantite}
  Prix unit.: {prix_unitaire} €
  Date      : {today}

{("Précisions : " + notes) if notes else ""}

Merci de bien vouloir confirmer la réception de cette commande et nous indiquer le délai de livraison.

Cordialement,
Madeleine Croûton
Chez Madeleine – Boulangerie Artisanale
Saint-Germain-des-Croissants
"""

    body_html = f"""<html><body>
<p>Bonjour,</p>
<p>Suite à notre échange, nous souhaitons passer la commande suivante :</p>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">
  <tr><th>Produit</th><td>{produit}</td></tr>
  <tr><th>Quantité</th><td>{quantite}</td></tr>
  <tr><th>Prix unitaire</th><td>{prix_unitaire} €</td></tr>
  <tr><th>Date</th><td>{today}</td></tr>
  {"<tr><th>Précisions</th><td>" + notes + "</td></tr>" if notes else ""}
</table>
<p>Merci de bien vouloir confirmer la réception de cette commande et nous indiquer le délai de livraison.</p>
<p>Cordialement,<br>
<strong>Madeleine Croûton</strong><br>
Chez Madeleine – Boulangerie Artisanale<br>
Saint-Germain-des-Croissants</p>
</body></html>"""

    subject = f"Commande – {produit} – {quantite} – {fournisseur}"

    email_ok, email_msg = _send_smtp(email_fournisseur, subject, body_html, body_text)
    notion_msg = _enregistrer_notion(
        fournisseur, produit, quantite, prix_unitaire, email_fournisseur, notes
    )

    status = "✅" if email_ok else "⚠️"
    return f"{status} Email : {email_msg}\n{notion_msg}"
