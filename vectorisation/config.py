"""
Configuration de l'étape 2 : chunking et vectorisation (ChromaDB).

Fichier volontairement indépendant de ingestion/config.py (pas d'import
croisé entre dossiers) -- seuls RACINE_PROJET, RAW_DATA_DIR et le chemin
du manifeste sont recalculés ici, à l'identique.
"""

import os

RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_DIR = os.path.join(RACINE_PROJET, "data", "raw")
MANIFEST_PATH = os.path.join(RACINE_PROJET, "data", "manifest.json")

# --- Chunking ---
# Taille cible d'un chunk, en caractères (pas en tokens -- plus simple à
# régler et suffisant pour un modèle d'embeddings de type MiniLM).
TAILLE_CHUNK = 500

# Chevauchement entre deux chunks consécutifs, pour ne pas couper une idée
# en plein milieu à la frontière de deux segments.
CHEVAUCHEMENT_CHUNK = 80

# --- Embeddings ---
# Modèle open source, léger et multilingue -- gère bien le français.
# Téléchargé automatiquement depuis Hugging Face au premier lancement
# (nécessite une connexion internet la première fois seulement, le modèle
# est ensuite mis en cache localement).
MODELE_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# --- ChromaDB ---
# Dossier où ChromaDB persiste sa base (créé automatiquement)
CHROMA_DB_DIR = os.path.join(RACINE_PROJET, "data", "chroma_db")

# Nom de la collection Chroma qui contiendra tous les chunks
NOM_COLLECTION = "tourisme_burkina"
