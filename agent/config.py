"""
Configuration de l'étape 3 : logique de l'agent (recherche + LLM Groq).

Comme pour vectorisation/config.py, ce fichier recalcule ses propres
chemins plutôt que d'importer depuis les autres dossiers du projet.

IMPORTANT : MODELE_EMBEDDINGS doit être IDENTIQUE à celui utilisé dans
vectorisation/config.py -- sinon les vecteurs de la question et ceux
stockés dans ChromaDB ne seront pas comparables.
"""

import os

RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ChromaDB (doit pointer vers la même base que vectorisation/) ---
CHROMA_DB_DIR = os.path.join(RACINE_PROJET, "data", "chroma_db")
NOM_COLLECTION = "tourisme_burkina"

# --- Embeddings (DOIT rester identique à vectorisation/config.py) ---
MODELE_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# --- Recherche vectorielle ---
TOP_K = 6

# Distance ChromaDB (L2 par défaut) au-delà de laquelle on considère que
# le meilleur résultat trouvé n'est en réalité pas pertinent -- l'agent
# répond alors "je ne sais pas" plutôt que d'halluciner une réponse à
# partir d'un contexte hors-sujet.
# ATTENTION : ce seuil est une valeur de départ. Il doit être calibré
# empiriquement en Phase 5 (évaluation), en observant les distances
# obtenues sur des questions dont on connaît la réponse attendue et sur
# des questions hors-périmètre.
SEUIL_DISTANCE_MAX = 3.0

# --- LLM via Groq ---
# NOTE (juillet 2026) : Groq a annoncé le 17/06/2026 la dépréciation de
# llama-3.3-70b-versatile et llama-3.1-8b-instant au profit des modèles
# openai/gpt-oss-*. L'énoncé du projet recommande "Llama 3 via Groq",
# mais mieux vaut utiliser un modèle activement supporté pour ne pas
# tomber en panne juste avant la soutenance. openai/gpt-oss-20b est
# rapide et gratuit sur le palier developer ; openai/gpt-oss-120b est
# plus capable si le volume de requêtes le permet.
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_API_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # à définir dans l'environnement, jamais en dur dans le code

GROQ_TEMPERATURE = 1  # bas, pour limiter les inventions/hallucinations
GROQ_MAX_TOKENS = 1024

PROMPT_SYSTEME = """Tu es un guide touristique virtuel spécialisé dans le Burkina Faso.

Règles strictes :
- Réponds UNIQUEMENT en français.
- Base ta réponse UNIQUEMENT sur le CONTEXTE fourni ci-dessous, pas sur tes connaissances générales.
- Si le contexte ne permet pas de répondre à la question, réponds explicitement que tu ne disposes pas de cette information, sans inventer.
- Cite la ou les sources utilisées (nom du site) à la fin de ta réponse.
- Reste concis et pratique : l'utilisateur planifie un voyage ou souhaite des informations culturelles sur le Burkina Faso.
"""
