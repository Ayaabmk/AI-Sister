---
marp: true
theme: default
paginate: true
header: 'Chez Madeleine – Assistant Boulangerie IA'
footer: 'AI Sisters · 2026'
style: |
  section {
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  h1 { color: #c45c26; }
  h2 { color: #8b4513; }
  table { font-size: 0.85em; }
  .columns { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# 🥐 Chez Madeleine
## Assistant Boulangerie IA

**Agent conversationnel pour artisans boulangers**

*Votre nom · AI Sisters · 2026*

---

## Le contexte

- **Madeleine Croûton** — boulangère depuis 32 ans à Saint-Germain-des-Croissants
- Gère seule : stocks, commandes fournisseurs, production, ventes
- Données éparpillées dans **Notion**, emails manuels, intuition pour la production

> **Problème :** trop de tâches admin, pas assez de temps pour le fournil

---

## Notre proposition

Un **assistant IA conversationnel** qui :

| 📦 | Consulte les stocks en temps réel |
| 📊 | Analyse les ventes et les marges |
| 📧 | Envoie des commandes fournisseurs |
| 🔮 | Prévoit la production du lendemain |

**En langage naturel** — Madeleine parle, l'agent agit.

---

## Architecture globale

```
┌─────────────────────────────────────┐
│   Chainlit (web)  ·  CLI (terminal) │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│   Agent LangGraph (ReAct)           │
│   Llama 3.3 70B via Groq            │
└──┬────────┬────────┬────────┬───────┘
   │        │        │        │
 Stocks  Catalogue Ventes  Commande
 Notion   Notion   Notion  Email + Notion
                              │
                    Prévisions production
                    (historique + météo)
```

---

## Stack technique

| Composant | Choix | Pourquoi |
|-----------|-------|----------|
| **Orchestration** | LangGraph | Tool calling, historique, ReAct |
| **LLM** | Llama 3.3 70B (Groq) | Rapide, gratuit en dev, fiable |
| **Données** | Notion (4 BDD) | Déjà utilisé par Madeleine |
| **Email** | SMTP (stdlib) | Pas de dépendance externe |
| **UI** | Chainlit + CLI | Démo fluide + tests rapides |

---

## Les 5 outils de l'agent

| # | Outil | Rôle |
|---|-------|------|
| 1 | `consulter_stocks` | Niveaux, alertes, fournisseurs |
| 2 | `consulter_catalogue` | Prix, coûts, marges |
| 3 | `consulter_ventes` | Tendances, best-sellers |
| 4 | `envoyer_commande_fournisseur` | Email SMTP + trace Notion |
| 5 | `prevoir_production` | Quantités à préparer demain |

**Règle d'or :** l'agent ne devine jamais — il appelle toujours un outil.

---

## Comment ça marche : le cycle ReAct

```
Madeleine : "Il me reste combien de beurre ?"
        │
        ▼
   [Think]  →  Comprendre l'intention
        │
        ▼
   [Act]    →  consulter_stocks()
        │
        ▼
   [Observe]→  8 kg, seuil 15 kg → ALERTE
        │
        ▼
   Réponse chaleureuse + proposition de commande
```

Confirmation obligatoire **avant** tout envoi d'email.

---

## Démo live — scénarios clés

1. **Stock bas** — *« Il me reste combien de beurre ? »*
2. **Commande** — *« Commande 30 kg chez Laiterie Martin »*
3. **Analyse** — *« Combien de croissants la semaine dernière ? »*
4. **Production** — *« Qu'est-ce que je dois préparer demain ? »*

```bash
chainlit run app.py   # → http://localhost:8000
```

---

## Tool créatif : prévisions de production

- **Historique** : moyennes sur 14 jours, par jour de semaine
- **Coefficients** : samedi ×1,30 · dimanche ×1,45
- **Météo** (OpenWeatherMap) : pluie → −15 % de production
- **Sortie** : tableau produit par produit avec recommandations chiffrées

*Exemple : dimanche pluvieux → moins de baguettes, plus de viennoiseries ?*

---

## Choix techniques & limites

**Choix**
- LangGraph > AgentExecutor : contrôle, inspectabilité, prod-ready
- Groq : latence faible = chat naturel en démo
- Notion : zéro migration pour Madeleine

**Limites actuelles**
- Historique en mémoire (pas de persistance)
- Pas d'authentification multi-utilisateur
- Prévisions sans jours fériés / événements locaux

---

<!-- _class: lead -->

## Merci !

### Questions ?

**Repo :** `boulangerie-ia`  
**Lancer :** `chainlit run app.py`

🥐 *« Moins d'admin, plus de croissants. »*
