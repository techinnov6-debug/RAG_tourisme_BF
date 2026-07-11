"""
Recherche vectorielle : transforme une question en vecteur, interroge
ChromaDB, et retourne les chunks les plus proches avec leurs métadonnées
et leur distance (utile pour décider si le contexte est pertinent ou non).
"""

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DB_DIR, NOM_COLLECTION, MODELE_EMBEDDINGS, TOP_K

_modele = None
_collection = None


def _charger_modele():
    global _modele
    if _modele is None:
        _modele = SentenceTransformer(MODELE_EMBEDDINGS)
    return _modele


def _charger_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        _collection = client.get_collection(NOM_COLLECTION)
    return _collection


def rechercher_contexte(question: str, top_k: int = None) -> list:
    """
    Retourne une liste de résultats triés par pertinence décroissante :
    [{texte, metadata, distance}, ...]

    Une distance plus PETITE signifie un résultat plus proche/pertinent
    (ChromaDB utilise par défaut la distance L2 au carré).
    """
    top_k = top_k or TOP_K

    modele = _charger_modele()
    collection = _charger_collection()

    vecteur_question = modele.encode([question]).tolist()

    resultat = collection.query(
        query_embeddings=vecteur_question,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    contextes = []
    for texte, metadata, distance in zip(
        resultat["documents"][0], resultat["metadatas"][0], resultat["distances"][0]
    ):
        contextes.append({"texte": texte, "metadata": metadata, "distance": distance})

    return contextes
