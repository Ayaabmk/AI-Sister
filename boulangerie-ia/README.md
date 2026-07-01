# 🥐 Chez Madeleine — Assistant Boulangerie IA

> Agent conversationnel IA pour aider Madeleine Croûton à gérer sa boulangerie artisanale au quotidien — stocks, commandes fournisseurs, analyse des ventes et prévisions de production — en langage naturel.

Projet réalisé dans le cadre de **AI Sisters · 2026**.

---

## Sommaire

- [Démo rapide](#démo-rapide)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Les 5 outils (tools)](#les-5-outils-tools)
- [Stack technique & choix](#stack-technique--choix)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancer l'application](#lancer-lapplication)
- [Exemples de conversation](#exemples-de-conversation)
- [Limites & améliorations](#limites--améliorations)

---

## Démo rapide

```bash
git clone <repo-url>
cd boulangerie-ia
pip install -r requirements.txt
cp .env.example .env        # puis renseigner GROQ_API_KEY + NOTION_TOKEN
chainlit run app.py         # → http://localhost:8000
```

---

## Fonctionnalités

| | Commande naturelle | Action de l'agent |
|---|---|---|
| 📦 | « Il me reste combien de beurre ? » | Consulte les stocks Notion, signale les alertes |
| 📊 | « Combien de croissants la semaine dernière ? » | Agrège l'historique des ventes Notion |
| 📧 | « Commande 30 kg de beurre chez Laiterie Martin » | Envoie un email SMTP **et** enregistre dans Notion |
| 🔮 | « Qu'est-ce que je dois préparer demain ? » | Calcule les prévisions de production (historique + météo) |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Interface utilisateur                  │
│      Chainlit (web)  ·  CLI (terminal)           │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│           Agent LangGraph — Pattern ReAct        │
│           Llama 3.3 70B · Groq                   │
│                                                  │
│   Think ──► Act ──► Observe ──► (boucle)         │
│                                                  │
│   System prompt : personnalité assistante        │
│   boulangerie · tutoiement · pas de jargon       │
└───┬──────┬──────┬──────────┬─────────────────────┘
    │      │      │          │
    ▼      ▼      ▼          ▼
 Stocks  Ventes  Catalogue  Commande       Prévisions
 Notion  Notion  Notion     Email SMTP     production
                            + Notion       (hist. + météo)
```

### Flux d'une requête

1. Madeleine envoie un message en langage naturel
2. Le LLM analyse l'intention (**Think**)
3. Il choisit l'outil adapté via son `@tool` descriptor et l'appelle (**Act**)
4. Il lit le résultat et décide de continuer ou de répondre (**Observe**)
5. La réponse est rendue dans Chainlit ou le terminal

La boucle peut enchaîner plusieurs outils dans la même conversation (ex : consulter stock → identifier fournisseur → envoyer commande → confirmer Notion).

---

## Les 5 outils (tools)

Chaque tool est une fonction Python décorée `@tool` (LangChain). Le LLM choisit quel outil appeler en lisant la **docstring** — pas de logique de routing codée en dur.

### 1. `consulter_stocks` — [`tools/notion_tools.py`](tools/notion_tools.py)

Lit la base **Stock Ingrédients** dans Notion.  
Retourne : ingrédient, quantité, unité, seuil d'alerte, fournisseur, email fournisseur, prix unitaire.  
Utilisé pour toute question sur les niveaux de stock ou les alertes.

### 2. `consulter_catalogue` — [`tools/notion_tools.py`](tools/notion_tools.py)

Lit la base **Catalogue Produits** dans Notion.  
Retourne : produit, catégorie, prix de vente TTC, coût de revient, marge (%).  
Utilisé pour les questions sur les prix, marges ou rentabilité.

### 3. `consulter_ventes` — [`tools/notion_tools.py`](tools/notion_tools.py)

Lit la base **Historique Ventes** dans Notion (tri décroissant par date).  
Retourne : date, produit, quantité vendue, CA (€).  
Utilisé pour l'analyse des tendances, comparaisons semaine, best-sellers.

### 4. `envoyer_commande_fournisseur` — [`tools/email_tool.py`](tools/email_tool.py)

**Double action :**
1. Envoie un email SMTP formaté (HTML + texte brut) au fournisseur
2. Crée une ligne dans la base **Commandes Fournisseurs** Notion (statut : "Envoyée")

Si `SMTP_USER` / `SMTP_PASSWORD` sont absents → **mode simulation** : l'email s'affiche sans être envoyé.  
Le system prompt impose une confirmation explicite de Madeleine avant tout appel à ce tool.

### 5. `prevoir_production` — [`tools/forecast_tool.py`](tools/forecast_tool.py)

Analyse l'historique des ventes (14 derniers jours) et calcule les quantités à produire pour le lendemain :

| Facteur | Détail |
|---|---|
| **Historique** | Moyenne par produit, priorité au même jour de semaine |
| **Coefficient jour** | Lundi 1,0 · Vendredi 1,05 · Samedi 1,30 · Dimanche 1,45 |
| **Météo** (optionnel) | Pluie → ×0,85 via OpenWeatherMap |

Retourne un tableau ASCII produit par produit avec moyenne historique et quantité recommandée.

---

## Stack technique & choix

| Composant | Choix | Justification |
|---|---|---|
| **Orchestration agent** | [LangGraph](https://github.com/langchain-ai/langgraph) `create_react_agent` | Graphe d'état explicite (Think→Act→Observe), historique de conversation natif, plus inspectable qu'AgentExecutor, direction prod de l'écosystème LangChain |
| **LLM** | Llama 3.3 70B Versatile via [Groq](https://groq.com) | Inférence quasi instantanée (crucial en démo chat), gratuit en dev, tool calling fiable sur des chaînes multi-étapes |
| **Base de données** | [Notion](https://notion.so) SDK Python officiel | Outil déjà utilisé par Madeleine — zéro migration, zéro formation ; 4 bases connectées via l'API REST |
| **Email** | `smtplib` (stdlib Python) | Pas de dépendance externe, compatible Gmail / Mailtrap ; mode simulation intégré |
| **Interface web** | [Chainlit](https://chainlit.io) | Interface chat complète (streaming, sessions, tool calls visibles) en quelques lignes ; thème AI Sisters via CSS custom |
| **Interface CLI** | `cli.py` maison | Tests rapides en développement sans serveur |

### Pourquoi LangGraph plutôt qu'un simple script ?

Un script linéaire ne peut pas gérer les conversations multi-tours, enchaîner plusieurs tools dynamiquement, ou inspecter l'état à chaque étape. LangGraph représente le raisonnement comme un graphe d'état : chaque nœud (Think / Act / Observe) est traçable et testable indépendamment. C'est aussi la base pour ajouter des fonctionnalités avancées (interruption humaine, persistance d'état, multi-agents).

### Pourquoi Groq + Llama 3.3 et pas Claude ou GPT-4 ?

- **Vitesse** : l'inférence Groq est 5 à 10× plus rapide que les autres providers — essentiel pour un chat fluide en démo
- **Coût** : gratuit en développement, pricing compétitif en production
- **Suffisance** : Llama 3.3 70B gère correctement le tool calling multi-étapes pour nos cas d'usage

En production à plus grande échelle, on migrerait vers **Claude Sonnet** (meilleur raisonnement en français, tool calling plus robuste sur des chaînes longues) ou **Mistral Large** (alternative EU, 100 % open source).

### Pourquoi Notion et pas une vraie BDD ?

Madeleine utilise déjà Notion. Zéro migration, zéro courbe d'apprentissage. Le SDK Python officiel expose une API REST complète avec pagination automatique. Limite : pas adapté à des requêtes analytiques lourdes ou à des volumes > 100 k entrées — pour une boulangerie artisanale, c'est largement suffisant.

---

## Installation

### Prérequis

- Python 3.11+
- Un compte [Groq](https://console.groq.com) (clé API gratuite)
- Un espace de travail Notion avec les 4 bases de données configurées

### Étapes

```bash
# 1. Cloner le repo
git clone <repo-url>
cd boulangerie-ia

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
```

---

## Configuration

Éditer `.env` et renseigner :

```env
# ── Obligatoire ──────────────────────────────────────
GROQ_API_KEY=gsk_...               # Clé API Groq (console.groq.com)

NOTION_TOKEN=ntn_...               # Token d'intégration Notion
NOTION_DB_STOCKS=...               # ID de la base Stock Ingrédients
NOTION_DB_CATALOGUE=...            # ID de la base Catalogue Produits
NOTION_DB_VENTES=...               # ID de la base Historique Ventes
NOTION_DB_COMMANDES=...            # ID de la base Commandes Fournisseurs

# ── Email (optionnel — mode simulation si absent) ────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Mot de passe d'application Gmail
EMAIL_FROM=Chez Madeleine <votre.email@gmail.com>

# ── Météo (optionnel) ────────────────────────────────
OPENWEATHER_API_KEY=...            # openweathermap.org (tier gratuit)
BAKERY_CITY=Montpellier
```

> **Trouver les IDs Notion :** ouvrir la base dans Notion → copier l'URL → l'ID est la suite de 32 caractères après le dernier `/` et avant le `?`.

---

## Lancer l'application

### Interface Chainlit (recommandée)

```bash
chainlit run app.py
# → http://localhost:8000
```

### Interface CLI (tests rapides)

```bash
python cli.py
```

---

## Exemples de conversation

```
Madeleine : Il me reste combien de beurre ?
Assistant : Tu as encore 8 kg de beurre — ton seuil d'alerte est à 15 kg,
            donc il faudrait commander ! Je peux préparer l'email pour
            Laiterie Martin ?

Madeleine : Oui, commande 30 kg.
Assistant : Voici ce que je vais envoyer à contact@laiterie-martin.fr :
            [résumé commande]
            Je confirme ?

Madeleine : Oui.
Assistant : ✅ Email envoyé à contact@laiterie-martin.fr
            ✅ Commande CMD-20260701-1042 enregistrée dans Notion (statut : Envoyée)

Madeleine : Combien de croissants j'ai vendus la semaine dernière ?
Assistant : La semaine dernière tu as vendu 312 croissants au total,
            soit en moyenne 45 par jour. Ton meilleur jour : samedi avec 78 !

Madeleine : Qu'est-ce que je dois préparer demain matin ?
Assistant : 📅 Prévisions pour dimanche 02/07/2026 (coeff ×1,45)
            ┌──────────────────┬──────────┬─────────────┐
            │ Produit          │ Moy. hist│ Recommandé  │
            ├──────────────────┼──────────┼─────────────┤
            │ Baguette         │     62,4 │          90 │
            │ Croissant        │     45,1 │          65 │
            │ Pain au chocolat │     38,7 │          56 │
            └──────────────────┴──────────┴─────────────┘
```

---

## Structure du projet

```
boulangerie-ia/
├── agent.py              # Définition de l'agent LangGraph (singleton)
├── app.py                # Interface Chainlit
├── cli.py                # Interface ligne de commande
├── config.py             # Chargement des variables d'environnement
├── requirements.txt      # Dépendances Python
├── .env.example          # Template de configuration
├── tools/
│   ├── __init__.py       # Export ALL_TOOLS
│   ├── notion_tools.py   # Tools 1–3 : stocks, catalogue, ventes
│   ├── email_tool.py     # Tool 4 : commande fournisseur (SMTP + Notion)
│   └── forecast_tool.py  # Tool 5 : prévisions de production
├── public/
│   ├── custom.css        # Thème AI Sisters pour Chainlit
│   ├── custom.js         # Personnalisations JS
│   ├── logo.svg          # Logo AI Sisters (clair)
│   └── logo_dark.svg     # Logo AI Sisters (sombre)
├── .chainlit/
│   └── config.toml       # Configuration Chainlit (UI, CoT, thème)
├── chainlit.md           # Message de bienvenue Chainlit
└── presentation/
    ├── index.html        # Slides de présentation (HTML autonome)
    └── README.md         # Script de présentation + Q&A
```

---

## Limites & améliorations

### Limites actuelles (MVP)

| Limite | Impact |
|---|---|
| Historique de conversation en mémoire vive | Perdu si l'onglet est fermé |
| Pas d'authentification | Une seule utilisatrice possible |
| Prévisions sans jours fériés / événements locaux | Coefficients parfois sous-estimés |
| Pas d'alertes proactives | Madeleine doit penser à demander |

### Axes d'amélioration pour la production

- **Persistance** : historique de conversation en Redis ou SQLite
- **Authentification** : login par utilisatrice, accès multi-boulangeries
- **Alertes proactives** : tâche cron quotidienne → SMS/email si stock bas
- **Multimodal** : Madeleine envoie une photo de son tableau de bord, l'agent lit les chiffres (modèle vision)
- **LLM plus robuste** : migration vers Claude Sonnet pour les raisonnements complexes
- **Prévisions enrichies** : jours fériés, événements locaux (marché, fête de quartier)

---

## Licence

Projet pédagogique — AI Sisters 2026.
