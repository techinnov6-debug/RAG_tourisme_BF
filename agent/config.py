"""
Configuration de l'étape 3 : logique de l'agent (recherche + LLM Groq).

Comme pour vectorisation/config.py, ce fichier recalcule ses propres
chemins plutôt que d'importer depuis les autres dossiers du projet.

IMPORTANT : MODELE_EMBEDDINGS doit être IDENTIQUE à celui utilisé dans
vectorisation/config.py -- sinon les vecteurs de la question et ceux
stockés dans ChromaDB ne seront pas comparables.
"""

import os

from dotenv import load_dotenv

# Charge automatiquement les variables définies dans un fichier .env à la
# racine du projet (ex: GROQ_API_KEY=...), s'il existe. Sans ce chargement,
# un .env rempli mais jamais "exporté" dans le shell reste invisible pour
# Python -- cause fréquente de "j'ai bien mis ma clé mais ça ne marche pas".
RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(RACINE_PROJET, ".env"))

# --- ChromaDB (doit pointer vers la même base que vectorisation/) ---
CHROMA_DB_DIR = os.path.join(RACINE_PROJET, "data", "chroma_db")
NOM_COLLECTION = "tourisme_burkina"

# --- Embeddings (DOIT rester identique à vectorisation/config.py) ---
MODELE_EMBEDDINGS = "all-MiniLM-L6-v2"

# --- Recherche vectorielle ---
TOP_K = 5

# Distance ChromaDB (L2 au carré par défaut) au-delà de laquelle on
# considère que le meilleur résultat trouvé n'est en réalité pas
# pertinent -- l'agent répond alors "je ne sais pas" plutôt que
# d'halluciner une réponse à partir d'un contexte hors-sujet.
#
# Avec des embeddings NORMALISÉS (voir normalize_embeddings=True dans
# retriever.py et build_vector_store.py), cette distance est bornée entre
# 0 (vecteurs identiques) et 4 (vecteurs opposés), et se relie à la
# similarité cosinus par : distance = 2 - 2 * cosinus.
#   cosinus 0.8 -> distance 0.4   (très pertinent)
#   cosinus 0.5 -> distance 1.0   (pertinent)
#   cosinus 0.3 -> distance 1.4   (limite)
#   cosinus 0.0 -> distance 2.0   (aucun rapport)
#
# ATTENTION : reste une valeur de départ. À calibrer empiriquement avec
# evaluation/evaluer.py, qui affiche les distances observées sur des
# questions dont on connaît la réponse et sur des questions hors-périmètre.
SEUIL_DISTANCE_MAX = 1.3

# --- LLM via Groq ---
# NOTE (juillet 2026) : Groq a annoncé le 17/06/2026 la dépréciation de
# llama-3.3-70b-versatile et llama-3.1-8b-instant au profit des modèles
# openai/gpt-oss-*. L'énoncé du projet recommande "Llama 3 via Groq",
# mais mieux vaut utiliser un modèle activement supporté pour ne pas
# tomber en panne juste avant la soutenance. openai/gpt-oss-20b est
# rapide et gratuit sur le palier developer ; openai/gpt-oss-120b est
# plus capable si le volume de requêtes le permet (modèle retenu ici).
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_API_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = "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"  # à définir dans l'environnement

GROQ_TEMPERATURE = 0.2  # bas, pour limiter les inventions/hallucinations
GROQ_MAX_TOKENS = 700

PROMPT_SYSTEME = """Tu es un guide touristique virtuel spécialisé dans le Burkina Faso.

Règles strictes :
- Réponds UNIQUEMENT en français.
- Base ta réponse UNIQUEMENT sur le CONTEXTE fourni ci-dessous, pas sur tes connaissances générales.
- Si le contexte ne permet pas de répondre à la question, réponds explicitement que tu ne disposes pas de cette information, sans inventer.
- Cite la ou les sources utilisées (nom du site) à la fin de ta réponse.
- Reste concis et pratique : l'utilisateur planifie un voyage ou souhaite des informations culturelles sur le Burkina Faso.
"""
