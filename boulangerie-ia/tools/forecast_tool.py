"""
Tool 5 (créatif) — Prévision de production pour le lendemain.
Croise l'historique des ventes (Notion) avec le jour de la semaine
et (optionnellement) la météo locale pour recommander les quantités à préparer.
"""
import json
from collections import defaultdict
from datetime import datetime, timedelta
from langchain_core.tools import tool
from notion_client import Client
from notion_client.errors import APIResponseError

try:
    import requests
    _requests_ok = True
except ImportError:
    _requests_ok = False

from config import NOTION_TOKEN, NOTION_DB_IDS, OPENWEATHER_API_KEY, BAKERY_CITY

_notion = Client(auth=NOTION_TOKEN)

# Coefficients par jour de semaine (lundi=0 … dimanche=6)
# Les boulangers vendent plus le week-end, et le dimanche matin est souvent le pic.
DAY_COEFFICIENTS = {0: 1.0, 1: 0.95, 2: 0.95, 3: 1.0, 4: 1.05, 5: 1.30, 6: 1.45}
DAY_NAMES = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def _extract_prop(prop: dict):
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
    if t == "date":
        d = prop.get("date")
        return d["start"] if d else ""
    return None


def _get_sales_data() -> list[dict]:
    results = []
    has_more = True
    cursor = None
    while has_more:
        kwargs: dict = {
            "database_id": NOTION_DB_IDS["ventes"],
            "sorts": [{"property": "Date", "direction": "descending"}],
        }
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = _notion.databases.query(**kwargs)
        for page in resp.get("results", []):
            row: dict = {}
            for key, val in page.get("properties", {}).items():
                row[key] = _extract_prop(val)
            results.append(row)
        has_more = resp.get("has_more", False)
        cursor = resp.get("next_cursor")
    return results


def _get_weather() -> dict:
    """Appel OpenWeatherMap pour la météo de demain. Retourne un dict simplifié."""
    if not _requests_ok or not OPENWEATHER_API_KEY:
        return {"available": False}
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?q={BAKERY_CITY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr&cnt=8"
        )
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if resp.status_code != 200 or "list" not in data:
            return {"available": False}

        # Prendre la prévision pour demain matin (~8h)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        forecast = next(
            (f for f in data["list"] if f["dt_txt"].startswith(tomorrow)),
            data["list"][0],
        )
        weather_main = forecast["weather"][0]["main"].lower()
        temp = forecast["main"]["temp"]
        desc = forecast["weather"][0]["description"]

        rain = weather_main in ("rain", "drizzle", "thunderstorm", "snow")
        coeff = 0.85 if rain else 1.0

        return {
            "available": True,
            "city": BAKERY_CITY,
            "description": desc,
            "temperature": round(temp, 1),
            "rain": rain,
            "production_coeff": coeff,
        }
    except Exception:
        return {"available": False}


@tool
def prevoir_production() -> str:
    """Analyse l'historique des ventes et prédit les quantités à produire pour demain.
    Tient compte du jour de la semaine (week-end = plus de ventes) et,
    si la clé API météo est configurée, de la météo locale.
    Retourne un plan de production chiffré pour chaque produit.
    Utiliser quand Madeleine demande ce qu'elle doit préparer ou produire."""
    jours_historique = 14
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_weekday = tomorrow.weekday()
    day_coeff = DAY_COEFFICIENTS[tomorrow_weekday]

    try:
        rows = _get_sales_data()
    except APIResponseError as e:
        return f"Erreur Notion : {e.status} – {e.message}"
    except Exception as e:
        return f"Erreur inattendue : {e}"

    if not rows:
        return "Aucune donnée de vente disponible pour établir une prévision."

    # Chaque ligne = (date, produit, quantité_vendue)
    # On utilise toutes les données disponibles (la BDD de test a des données figées)
    # en limitant au nombre de jours demandé si les données sont suffisantes.
    sorted_rows = sorted(
        [r for r in rows if r.get("Date")],
        key=lambda r: r["Date"],
        reverse=True,
    )
    # Garder uniquement les N derniers jours distincts
    seen_dates: set = set()
    recent_rows = []
    for r in sorted_rows:
        seen_dates.add(r["Date"])
        recent_rows.append(r)
        if len(seen_dates) >= jours_historique:
            break

    # by_weekday[weekday][produit] = [qty, qty, …]
    by_weekday: dict[int, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    global_by_product: dict[str, list] = defaultdict(list)

    for row in recent_rows:
        date_val = row.get("Date", "")
        produit = row.get("Produit", "")
        qty = row.get("Quantité vendue")
        if not date_val or not produit or qty is None:
            continue
        try:
            row_date = datetime.fromisoformat(str(date_val)).date()
        except ValueError:
            continue
        wd = row_date.weekday()
        by_weekday[wd][produit].append(qty)
        global_by_product[produit].append(qty)

    if not global_by_product:
        return "Impossible de calculer des prévisions : données de vente insuffisantes ou mal formatées."

    # Prévisions
    weather = _get_weather()
    weather_coeff = weather.get("production_coeff", 1.0)
    total_coeff = day_coeff * weather_coeff

    plan = {}
    for produit, global_vals in sorted(global_by_product.items()):
        wd_vals = by_weekday.get(tomorrow_weekday, {}).get(produit, [])
        base = sum(wd_vals) / len(wd_vals) if wd_vals else sum(global_vals) / len(global_vals)
        recommended = max(1, round(base * total_coeff))
        plan[produit] = {
            "moyenne_historique": round(base, 1),
            "recommandé": recommended,
        }

    if not plan:
        return "Impossible de calculer des prévisions : données de vente insuffisantes ou mal formatées."

    lines = [
        f"📅 Prévisions de production pour {DAY_NAMES[tomorrow_weekday]} {tomorrow.strftime('%d/%m/%Y')}",
        "",
        f"Coefficient jour ({DAY_NAMES[tomorrow_weekday]}) : ×{day_coeff}",
    ]
    if weather.get("available"):
        lines.append(
            f"Météo {weather['city']} : {weather['description']}, {weather['temperature']}°C "
            + ("🌧️ (coeff ×0.85)" if weather["rain"] else "☀️ (pas d'impact)")
        )
    lines += ["", "┌────────────────────────────────┬──────────┬─────────────┐",
              "│ Produit                        │ Moy. hist│ Recommandé  │",
              "├────────────────────────────────┼──────────┼─────────────┤"]
    for product, data in sorted(plan.items()):
        lines.append(
            f"│ {product:<30} │ {data['moyenne_historique']:>8.1f} │ {data['recommandé']:>11} │"
        )
    lines.append("└────────────────────────────────┴──────────┴─────────────┘")

    if weather.get("rain"):
        lines.append("\n⚠️  Météo pluvieuse prévue → production réduite de 15 %.")

    return "\n".join(lines)
