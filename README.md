# Guide Touristique et Culturel Intelligent - Burkina Faso

Assistant conversationnel basé sur un système RAG (Retrieval-Augmented
Generation) pour répondre à des questions sur le tourisme, la culture et
les formalités de voyage au Burkina Faso.

Projet réalisé dans le cadre du cours de Data Science (Master 1 IFOAD-UJKZ,
édition 2026) — Option 4 : Guide Touristique et Culturel Intelligent.

## Fonctionnement général

1. Des pages web et des PDF officiels sont collectés et nettoyés (Phase 1).
2. Les textes sont découpés en segments et transformés en vecteurs, stockés
   dans une base vectorielle ChromaDB (Phase 2).
3. Une question posée par l'utilisateur est comparée à ces vecteurs pour
   retrouver les passages les plus pertinents, puis un LLM (via l'API Groq)
   génère une réponse à partir de ce contexte (Phase 3).
4. Une interface Streamlit permet d'interagir avec l'assistant (Phase 4).
5. Un script d'évaluation mesure la pertinence des réponses et le taux
   d'hallucination du système (Phase 5).

## Structure du projet

```
rag-tourisme-bf/
├── ingestion/            Phase 1 - collecte (scraping web + PDF)
│   ├── config.py           sources à scraper, paramètres de crawl
│   ├── scraper.py          crawl multi-pages, filtre de langue, robots.txt
│   ├── pdf_loader.py       extraction de texte depuis des PDF locaux
│   ├── utils.py            nettoyage de texte partagé
│   └── collect_data.py     script principal (point d'entrée)
│
├── vectorisation/        Phase 2 - chunking + vectorisation
│   ├── config.py           taille de chunk, modèle d'embeddings, ChromaDB
│   ├── chunking.py         découpage récursif avec chevauchement
│   └── build_vector_store.py  script principal (point d'entrée)
│
├── agent/                Phase 3 - logique RAG + LLM
│   ├── config.py           seuil de pertinence, modèle Groq, prompt système
│   ├── retriever.py        recherche vectorielle dans ChromaDB
│   ├── generator.py        construction du prompt + appel à l'API Groq
│   └── assistant.py        orchestrateur (+ boucle de test en ligne de commande)
│
├── evaluation/            Phase 5 - évaluation du système
│   ├── questions_test.py   jeu de questions (dans/hors périmètre)
│   └── evaluer.py          script principal (point d'entrée)
│
├── data/
│   ├── pdfs/               PDF à déposer manuellement avant la collecte
│   ├── raw/                 textes bruts collectés (générés automatiquement)
│   ├── chroma_db/           base vectorielle (générée automatiquement)
│   ├── manifest.json        index des pages/PDF collectés (généré automatiquement)
│   └── sources.md           documentation des sources utilisées
│
├── app.py                 Phase 4 - interface Streamlit (point d'entrée)
├── requirements.txt
└── .env.example            modèle du fichier .env à créer
```

## Installation

```bash
pip install -r requirements.txt
```

Copier `.env` à la racine du projet, puis renseigner votre
clé API Groq :

```
GROQ_API_KEY=votre_cle_ici
```

(Clé obtenue gratuitement sur https://console.groq.com)

## Exécution (dans l'ordre)

Chaque étape doit être lancée une fois, dans cet ordre, avant de passer à
la suivante. Toutes les commandes ci-dessous s'exécutent depuis la racine
du projet (`rag-tourisme-bf/`).

### 1. Collecte des données
```bash
python ingestion/collect_data.py
```
Déposer au préalable d'éventuels PDF dans `data/pdfs/` et les déclarer dans
`ingestion/config.py` (`PDF_SOURCES`). Génère `data/raw/` et `data/manifest.json`.

### 2. Vectorisation
```bash
python vectorisation/build_vector_store.py
```
Génère `data/chroma_db/`. Peut être relancé sans risque de doublon (la
collection est réinitialisée à chaque exécution).

### 3. Test rapide de l'agent (optionnel, avant l'interface)
```bash
python agent/assistant.py
```
Boucle de questions/réponses en ligne de commande.

### 4. Interface web
```bash
streamlit run app.py
```
Ouvre l'application dans le navigateur (`http://localhost:8501` par défaut).

### 5. Évaluation du système
```bash
python evaluation/evaluer.py
```
Génère `evaluation/resultats_evaluation.csv` et affiche un résumé des
métriques (pertinence, taux d'hallucination, aide à la calibration du seuil).

## Points d'attention connus

- **Modèle d'embeddings** : `all-MiniLM-L6-v2` est majoritairement anglophone
  alors que le corpus est en français — voir la section Limites du rapport
  technique.
- **Sites en JavaScript** (Booking.com, Evaneos.fr, Partir.com) : le scraper
  ne récupère que le HTML statique, pas le contenu chargé dynamiquement.
- **Dette technique assumée** : chaque phase a son propre `config.py` et son
  propre script principal, pour rester compréhensible étape par étape durant
  le développement. Une consolidation est prévue en fin de projet.


## Auteurs

ZERBO Soukrane Zanhiro, SANA Ali, SAWADOGO Aboubacary — Master 1 IFOAD-UJKZ

Encadrement : Dr Delwende D. Arthur Sawadogo
