"""
Tool 1 (obligatoire) — Lecture de la base de données Notion.
Permet à l'agent de consulter stocks, catalogue et historique des ventes.
"""
import json
from typing import Optional
from langchain_core.tools import tool
from notion_client import Client
from notion_client.errors import APIResponseError

from config import NOTION_TOKEN, NOTION_DB_IDS

_notion = Client(auth=NOTION_TOKEN)


def _extract_prop(prop: dict):
    """Convertit une propriété Notion en valeur Python simple."""
    t = prop.get("type", "")
    if t == "title":
        items = prop.get("title", [])
        return items[0]["plain_text"] if items else ""
    if t == "rich_text":
        items = prop.get("rich_text", [])
        return items[0]["plain_text"] if items else ""
    if t == "number":
        return prop.get("number")
    if t == "select":
        sel = prop.get("select")
        return sel["name"] if sel else ""
    if t == "multi_select":
        return [o["name"] for o in prop.get("multi_select", [])]
    if t == "date":
        d = prop.get("date")
        return d["start"] if d else ""
    if t == "email":
        return prop.get("email") or ""
    if t == "url":
        return prop.get("url") or ""
    if t == "checkbox":
        return prop.get("checkbox", False)
    if t == "formula":
        f = prop.get("formula", {})
        ft = f.get("type", "")
        return f.get(ft)
    if t == "rollup":
        r = prop.get("rollup", {})
        rt = r.get("type", "")
        if rt == "number":
            return r.get("number")
        if rt == "array":
            return [_extract_prop(item) for item in r.get("array", [])]
    return None


def _page_to_dict(page: dict) -> dict:
    row = {"_id": page["id"]}
    for key, val in page.get("properties", {}).items():
        row[key] = _extract_prop(val)
    return row


def _query_db(db_id: str, sorts: Optional[list] = None, filter_: Optional[dict] = None) -> list[dict]:
    kwargs: dict = {"database_id": db_id}
    if sorts:
        kwargs["sorts"] = sorts
    if filter_:
        kwargs["filter"] = filter_
    results = []
    has_more = True
    cursor = None
    while has_more:
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = _notion.databases.query(**kwargs)
        results.extend(resp.get("results", []))
        has_more = resp.get("has_more", False)
        cursor = resp.get("next_cursor")
    return [_page_to_dict(p) for p in results]


@tool
def consulter_stocks() -> str:
    """Consulte le stock actuel de tous les ingrédients de la boulangerie.
    Retourne : ingrédient, quantité en stock, unité, seuil d'alerte, fournisseur, email fournisseur, prix unitaire.
    Utiliser pour répondre aux questions sur les stocks, les niveaux d'alerte, ce qu'il faut commander."""
    try:
        rows = _query_db(NOTION_DB_IDS["stocks"])
        compact = [
            {
                "ingredient": r.get("Ingrédient", ""),
                "quantite": r.get("Quantité en stock"),
                "unite": r.get("Unité", ""),
                "seuil_alerte": r.get("Seuil alerte"),
                "fournisseur": r.get("Fournisseur", ""),
                "email": r.get("Email fournisseur", ""),
                "prix_unitaire": r.get("Prix unitaire (€)"),
            }
            for r in rows
        ]
        return json.dumps(compact, ensure_ascii=False)
    except APIResponseError as e:
        return f"Erreur Notion : {e.status} – {e.message}"
    except Exception as e:
        return f"Erreur inattendue : {e}"


@tool
def consulter_catalogue() -> str:
    """Consulte le catalogue des produits de la boulangerie.
    Retourne : produit, catégorie, prix de vente, coût de revient, marge.
    Utiliser pour les questions sur les prix, la rentabilité ou les marges."""
    try:
        rows = _query_db(NOTION_DB_IDS["catalogue"])
        compact = [
            {
                "produit": r.get("Produit", ""),
                "categorie": r.get("Catégorie", ""),
                "prix_vente": r.get("Prix de vente TTC (€)"),
                "cout_revient": r.get("Coût de revient (€)"),
                "marge_pct": r.get("Marge (%)"),
            }
            for r in rows
        ]
        return json.dumps(compact, ensure_ascii=False)
    except APIResponseError as e:
        return f"Erreur Notion : {e.status} – {e.message}"
    except Exception as e:
        return f"Erreur inattendue : {e}"


@tool
def consulter_ventes() -> str:
    """Consulte l'historique des ventes de la boulangerie (14 derniers jours).
    Retourne les ventes journalières par produit : date, produit, quantité vendue, CA.
    Utiliser pour les questions sur les ventes passées, les tendances, les meilleures ventes,
    les produits les plus vendus, les chiffres de la semaine, etc."""
    try:
        rows = _query_db(
            NOTION_DB_IDS["ventes"],
            sorts=[{"property": "Date", "direction": "descending"}],
        )
        # Format compact : garder uniquement les champs utiles
        compact = [
            {
                "date": r.get("Date", ""),
                "produit": r.get("Produit", ""),
                "quantite": r.get("Quantité vendue"),
                "ca_eur": r.get("CA (€)"),
            }
            for r in rows
        ]
        return json.dumps(compact, ensure_ascii=False)
    except APIResponseError as e:
        return f"Erreur Notion : {e.status} – {e.message}"
    except Exception as e:
        return f"Erreur inattendue : {e}"
