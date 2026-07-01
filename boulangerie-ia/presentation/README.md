# Guide de présentation — Chez Madeleine · AI Sisters

Présentation de **10 slides**, durée cible **15–18 minutes**.

---

## Lancer la présentation

```bash
open presentation/index.html   # macOS
# ou double-cliquer sur le fichier
```

Navigation : **← →** ou **Espace** · **F** pour plein écran.

---

## Minutage global

| Slide | Sujet | Durée |
|-------|-------|-------|
| 1 | Titre | 30 s |
| 2 | Présentation | 1 min |
| 3 | Plan | 30 s |
| 4 | Contexte | 1,5 min |
| 5 | Problème | 1,5 min |
| 6 | Solution | 2 min |
| 7 | Diagramme | 2 min |
| 8 | Démo live | 4–5 min |
| 9 | Résultats & limites | 2 min |
| 10 | Conclusion | 30 s |
| **Total** | | **~15–18 min** |

---

## Script slide par slide

---

### Slide 1 — Titre

> Bonjour à toutes et à tous. Je suis [prénom], et aujourd'hui je vous présente **Chez Madeleine** — un assistant IA conversationnel conçu pour aider une boulangère artisanale à gérer son commerce au quotidien. Ce projet a été réalisé dans le cadre d'**AI Sisters**. L'idée en une phrase : moins d'admin, plus de croissants.

*→ passer à la slide suivante*

---

### Slide 2 — Présentation

> Je m'appelle [prénom]. Je travaille sur [votre contexte : alternance / formation / projet perso…]. J'ai choisi ce cas d'usage parce qu'il illustre parfaitement ce qu'un agent IA peut apporter à un artisan : connecter des outils existants, répondre en langage naturel, et automatiser des tâches répétitives — sans que l'utilisatrice ait besoin d'apprendre quoi que ce soit de technique.

*→ passer à la slide suivante*

---

### Slide 3 — Plan

> On va couvrir cinq points : d'abord le contexte — qui est Madeleine et comment elle travaille. Ensuite le problème que j'ai identifié. Puis la solution : l'agent IA et comment il fonctionne. On verra ça en démo live. Et on terminera par un bilan honnête — ce qui marche, les limites, et ce qu'on ferait en production.

*→ passer à la slide suivante*

---

### Slide 4 — Contexte

> Madeleine Croûton tient **Chez Madeleine** à Saint-Germain-des-Croissants depuis 32 ans. C'est une boulangère artisanale, seule aux commandes : elle gère ses stocks, ses commandes fournisseurs, sa production et ses ventes.
>
> Ses données vivent dans **Notion** — elle a quatre bases : Stock Ingrédients, Catalogue Produits, Historique Ventes et Commandes Fournisseurs. Tout est là, mais rien n'est connecté. Pour commander un fournisseur, elle rédige un email à la main. Pour décider combien produire le lendemain matin, elle s'appuie sur son expérience — ce qui marche, mais c'est chronophage.

*→ passer à la slide suivante*

---

### Slide 5 — Problème

> Le problème c'est que Madeleine passe un temps précieux sur des tâches qui pourraient être automatisées.
>
> Quatre frictions concrètes :
> - **Temps perdu** sur les emails de commande — un email par fournisseur, rédigé à la main à chaque fois
> - **Données éparpillées** — ses quatre bases Notion ne se parlent pas entre elles
> - **Production à l'intuition** — elle risque de gaspiller ou de manquer
> - **Alertes manquées** — elle découvre parfois la rupture de stock le matin même au fournil
>
> La question centrale : comment connecter tout ça en langage naturel, sans lui imposer une nouvelle interface complexe ?

*→ passer à la slide suivante*

---

### Slide 6 — Solution

> La réponse, c'est un **agent IA conversationnel**. Madeleine lui parle comme à un collègue — l'agent interroge ses données et agit.
>
> On a développé **cinq outils** — en Python, que l'agent peut appeler :
> - **consulter_stocks** : lit la base Notion, renvoie les niveaux, les alertes, les fournisseurs
> - **consulter_ventes** : historique des ventes sur 14 jours, tendances, best-sellers
> - **envoyer_commande** : c'est le tool clé — il envoie un email SMTP au fournisseur *et* enregistre la commande dans Notion en une seule action
> - **prevoir_production** : croise l'historique avec le jour de la semaine et la météo pour recommander les quantités à préparer demain
>
> Côté tech : l'orchestration est assurée par **LangGraph**, le LLM est **Llama 3.3 70B via Groq** — choisi pour sa vitesse d'inférence — et l'interface est **Chainlit**, qui donne un chat web professionnel en quelques lignes.

*→ passer à la slide suivante*

---

### Slide 7 — Diagramme

> Regardons l'architecture en détail.
>
> En haut, **Madeleine** — elle interagit via Chainlit (interface web) ou le CLI en terminal.
>
> Au centre, le cœur du système : l'**agent LangGraph** qui tourne en boucle **ReAct**. C'est quoi ReAct ? À chaque message, l'agent fait trois choses : il **réfléchit** (*Think*) pour comprendre l'intention, il **agit** (*Act*) en appelant le bon outil, et il **observe** (*Observe*) le résultat avant de décider s'il a besoin d'un autre outil ou s'il peut répondre. Cette boucle peut se répéter plusieurs fois dans une même conversation.
>
> En bas, les **cinq tools**. Les trois de gauche lisent Notion — stocks, catalogue, ventes. Le quatrième — encadré en rose — est le tool clé : `envoyer_commande`, qui fait une double action : email SMTP *et* trace dans Notion. Le cinquième calcule les prévisions de production.
>
> Ce qui est important ici : **le LLM ne code pas la logique métier**. Il choisit quel outil appeler en lisant les docstrings Python de chaque outil. C'est ça la puissance du tool calling.

*→ passer à la slide suivante*

---

### Slide 8 — Démo live

> On passe à la démo. J'ai Chainlit ouvert sur http://localhost:8000.

**Scénario 1 — Stock bas**

> *Tapez :* `Il me reste combien de beurre ?`
>
> Vous voyez l'agent appeler `consulter_stocks`. Il lit Notion, détecte que le stock de beurre est sous le seuil d'alerte, et propose proactivement de passer une commande. Ce comportement proactif vient du system prompt — on lui a dit de signaler clairement les alertes.

**Scénario 2 — Commande fournisseur**

> *Tapez :* `Oui, commande 30 kg`
>
> L'agent résume la commande et demande confirmation avant d'agir — règle absolue du system prompt. Quand on valide, il appelle `envoyer_commande_fournisseur` : email envoyé, et si vous avez Notion ouvert dans un autre onglet, vous verrez la nouvelle ligne apparaître dans la table Commandes avec le statut "Envoyée".

**Scénario 3 — Analyse ventes**

> *Tapez :* `Combien de croissants j'ai vendus la semaine dernière ?`
>
> L'agent appelle `consulter_ventes`, agrège les données par produit, et répond en langage naturel avec totaux et meilleur jour. Aucun calcul côté utilisatrice.

**Scénario 4 — Prévision production**

> *Tapez :* `Qu'est-ce que je dois préparer demain matin ?`
>
> `prevoir_production` entre en jeu : il analyse les 14 derniers jours, applique un coefficient jour de semaine — le dimanche c'est ×1,45 — et si on a configuré OpenWeatherMap, il ajuste aussi selon la météo. Madeleine reçoit un tableau par produit avec les quantités recommandées.

*→ passer à la slide suivante*

---

### Slide 9 — Résultats & limites

> Bilan honnête.
>
> **Ce qui marche bien** : les réponses sont toujours fondées sur les données Notion — l'agent ne devine jamais, c'est inscrit dans le system prompt. La double action email + Notion fonctionne. Les prévisions sont lisibles et actionnables. Et le mode simulation SMTP permet de faire une démo sans configurer de vrai compte email.
>
> **Les limites du MVP** : l'historique de conversation est en mémoire vive — si Madeleine ferme l'onglet, tout disparaît. Pas d'authentification. Les prévisions ne tiennent pas compte des jours fériés ou d'événements locaux comme un marché ou une fête de quartier. Et pas encore d'alertes proactives.
>
> **Ce qu'on ferait en production** : persistance de l'historique en Redis ou SQLite, un cron quotidien qui envoie un SMS si un stock est bas, intégration multimodale pour que Madeleine puisse envoyer une photo de son tableau de bord, et potentiellement migrer vers Claude Sonnet pour des raisonnements plus complexes.

*→ passer à la slide suivante*

---

### Slide 10 — Conclusion / Merci

> Pour résumer : **Chez Madeleine**, c'est un agent IA qui connecte Notion, email et prévisions météo dans une interface conversationnelle simple, conçue pour une artisanale qui n'a pas de temps à perdre.
>
> La leçon principale : un bon agent IA, ce n'est pas un LLM seul. C'est un LLM + des tools fiables + un prompt bien calibré + une UX adaptée à l'utilisatrice finale.
>
> Merci. Je suis disponible pour vos questions.

---

## Questions & réponses préparées

### Sur l'architecture et le code

**Q : C'est quoi exactement LangGraph ? C'est différent de LangChain ?**

> LangGraph est une librairie construite au-dessus de LangChain, mais qui représente le raisonnement de l'agent comme un **graphe d'état** plutôt qu'une simple chaîne linéaire. L'avantage : chaque étape Think → Act → Observe est explicite et traçable. C'est beaucoup plus facile à déboguer et à faire évoluer qu'un `AgentExecutor` classique, et c'est la direction que prend l'écosystème LangChain pour la production.

**Q : Comment l'agent sait quel outil appeler ?**

> Chaque outil a une **docstring** — une description en français de son rôle, de ses paramètres et de quand l'utiliser. Le LLM reçoit toutes ces descriptions dans son contexte. Grâce au **function calling** natif, il retourne un JSON structuré avec le nom de l'outil et les arguments. LangGraph exécute l'outil, renvoie le résultat au LLM, qui décide s'il a besoin d'un autre outil ou s'il peut répondre.

**Q : Pourquoi Groq et Llama plutôt que GPT-4 ou Claude ?**

> Trois raisons : **vitesse** (inférence quasi instantanée — crucial en démo live), **coût** (gratuit en développement avec Groq), et **suffisance** — Llama 3.3 70B gère bien le tool calling multi-étapes pour nos cas d'usage. En production, on migrerait vers **Claude Sonnet** ou **GPT-4o** pour des raisonnements plus complexes et une meilleure robustesse en français.

**Q : Que se passe-t-il si Notion ou Groq est down ?**

> Chaque tool gère ses erreurs et retourne un message lisible : `Erreur Notion : 503`, etc. L'agent transmet l'information à Madeleine en langage clair. Il n'invente jamais de données — c'est une règle du system prompt : *"Ne devine jamais"*.

**Q : L'agent peut-il envoyer un email sans que Madeleine valide ?**

> Non. Le system prompt impose explicitement : *"Avant d'envoyer un email de commande, résume et demande confirmation."* C'est un garde-fou applicatif. L'agent résume toujours la commande et attend un "oui" explicite avant d'agir.

**Q : C'est quoi le mode simulation email ?**

> Si `SMTP_USER` et `SMTP_PASSWORD` ne sont pas dans le `.env`, le tool n'envoie pas d'email réel. Il affiche à la place le contenu exact de l'email qui aurait été envoyé. Pratique pour les démos et les tests sans risquer de spammer un vrai fournisseur.

---

### Sur les choix techniques

**Q : Pourquoi Notion et pas une vraie base de données ?**

> Madeleine l'utilise déjà — zéro migration, zéro formation. Notion expose une API REST mature via le SDK Python officiel. Limite : pas adapté à des volumes massifs ou des requêtes analytiques lourdes. Pour une boulangerie artisanale, c'est largement suffisant. En production, on pourrait ajouter une couche PostgreSQL pour les analyses historiques.

**Q : Pourquoi Chainlit et pas une app React custom ?**

> Rapidité de développement. Chainlit donne en quelques heures : interface chat, streaming des réponses, gestion de session, et personnalisation CSS complète. Pour une app métier avec dashboard, on consommerait la même logique agent via une API REST et on construirait une UI sur mesure.

**Q : Pourquoi Python ?**

> L'écosystème LangChain / LangGraph est en Python, le SDK Notion officiel est en Python, et c'est le langage de choix pour le prototypage rapide d'agents IA. En production, on envelopperait la logique dans une API FastAPI.

**Q : Les clés API sont-elles sécurisées ?**

> Elles sont dans un fichier `.env` qui ne doit pas être commité (à ajouter dans `.gitignore`). Les valeurs par défaut dans `config.py` ont été vidées pour éviter de les exposer dans le code. En production : gestionnaire de secrets (Vault, variables d'environnement CI/CD).

---

### Sur les fonctionnalités

**Q : Comment fonctionnent exactement les prévisions de production ?**

> Cinq étapes : 1) récupérer les ventes des 14 derniers jours depuis Notion. 2) Pour chaque produit, calculer la moyenne vendue le même jour de la semaine que demain — si pas assez de données, fallback sur la moyenne globale. 3) Multiplier par un coefficient jour : samedi ×1,30, dimanche ×1,45, etc. 4) Si OpenWeatherMap est configuré et qu'il pleut demain, multiplier par 0,85. 5) Arrondir et afficher. C'est une heuristique transparente — pas de machine learning, explication immédiate.

**Q : Pourquoi réduire de 15 % quand il pleut ?**

> Hypothèse métier : moins de passage en boutique par mauvais temps. Le coefficient est ajustable dans `forecast_tool.py`. On pourrait affiner par produit — le pain se vend peut-être autant, les viennoiseries moins.

**Q : Peut-on facilement ajouter un sixième outil ?**

> Oui, en trois étapes : créer une fonction Python décorée `@tool`, lui écrire une docstring descriptive, et l'ajouter à `ALL_TOOLS` dans `tools/__init__.py`. L'agent l'utilisera automatiquement dès le prochain démarrage.

---

### Questions pièges

| Question | Réponse courte |
|---|---|
| « C'est du RAG ? » | Non — pas de recherche vectorielle. On appelle des APIs structurées (Notion), pas un vector store. |
| « Vous avez entraîné un modèle ? » | Non — on utilise Llama 3.3 70B pré-entraîné via Groq, avec du prompt engineering et du tool calling. |
| « L'agent peut halluciner des chiffres ? » | Non, tant que le tool est appelé. Le system prompt interdit de deviner. Les données viennent de Notion, pas du LLM. |
| « Et si Madeleine pose une question hors sujet ? » | Le system prompt la recadre comme assistante boulangerie. Elle répond poliment qu'elle n'est pas outillée pour ça. |
| « C'est open source ? » | Le code projet oui ; les clés API et données Notion restent privées. |
| « Combien ça coûte en prod ? » | Groq : compétitif ; Notion API : inclus dans les plans Notion ; SMTP Gmail : gratuit ; OpenWeatherMap : tier gratuit 1000 req/jour. Coût principal = tokens LLM, ~quelques euros/mois pour l'usage d'une boulangerie. |

---

## Checklist avant la présentation

- [ ] `.env` configuré avec `GROQ_API_KEY` et les IDs Notion
- [ ] `chainlit run app.py` testé — interface accessible sur http://localhost:8000
- [ ] Notion ouvert sur la table **Commandes Fournisseurs** (pour montrer l'enregistrement live)
- [ ] Slides ouvertes dans le navigateur, en plein écran (touche **F**)
- [ ] Les 4 scénarios de démo répétés au moins une fois
- [ ] Chrono : viser 16 min pour garder 2 min de marge pour les questions

## Si vous manquez de temps

| Gain | Action |
|---|---|
| −1 min | Fusionner slides 4 et 5 à l'oral |
| −1 min | Diagramme : 1 min au lieu de 2 — juste nommer les couches |
| −2 min | Démo : 2 scénarios au lieu de 4 (stock + commande) |
| −1 min | Slide 9 : limites seulement, axes d'amélioration à l'oral si question |

**Ne jamais couper :** slide 7 (diagramme ReAct), au moins 2 scénarios de démo.
