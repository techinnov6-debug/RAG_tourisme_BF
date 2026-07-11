"""
Script principal de la Phase 2 : chunking + vectorisation dans ChromaDB.

Usage :
    python build_vector_store.py

Prérequis : avoir lancé ingestion/collect_data.py au préalable (le
manifeste data/manifest.json et les fichiers data/raw/ doivent exister).

Résultat : une base ChromaDB persistée dans data/chroma_db/, contenant
un vecteur par chunk de texte, avec ses métadonnées (source, url,
catégorie, type).
"""

import json
import os
import uuid

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    RAW_DATA_DIR, MANIFEST_PATH, TAILLE_CHUNK, CHEVAUCHEMENT_CHUNK,
    MODELE_EMBEDDINGS, CHROMA_DB_DIR, NOM_COLLECTION,
)
from chunking import decouper_texte

TAILLE_LOT = 64  # nombre de chunks encodés/ajoutés par lot


def charger_manifest() -> list:
    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(
            f"Manifeste introuvable : {MANIFEST_PATH}\n"
            "Lancez d'abord ingestion/collect_data.py."
        )
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def construire_chunks(manifest: list) -> list:
    """
    Parcourt le manifeste, lit chaque fichier texte associé, le découpe
    en chunks, et retourne une liste de dicts prêts pour ChromaDB :
    {id, texte, metadata}
    """
    tous_les_chunks = []

    for entree in manifest:
        if entree["statut"] != "ok" or not entree.get("fichier"):
            continue

        chemin_fichier = os.path.join(RAW_DATA_DIR, entree["fichier"])
        if not os.path.exists(chemin_fichier):
            print(f"  [IGNORE] fichier manquant : {chemin_fichier}")
            continue

        with open(chemin_fichier, "r", encoding="utf-8") as f:
            texte = f.read()

        chunks_texte = decouper_texte(texte, TAILLE_CHUNK, CHEVAUCHEMENT_CHUNK)

        for i, chunk in enumerate(chunks_texte):
            tous_les_chunks.append({
                "id": str(uuid.uuid4()),
                "texte": chunk,
                "metadata": {
                    "nom_source": entree["nom"],
                    "url": entree["url"],
                    "categorie": entree["categorie"],
                    "type": entree.get("type", "web"),
                    "fichier": entree["fichier"],
                    "chunk_index": i,
                },
            })

    return tous_les_chunks


def main():
    print("Chargement du manifeste...")
    manifest = charger_manifest()

    print("Découpage des textes en chunks...")
    chunks = construire_chunks(manifest)
    print(f"  -> {len(chunks)} chunk(s) généré(s) au total\n")

    if not chunks:
        print("Aucun chunk à vectoriser. Vérifiez que la collecte (Phase 1) "
              "a bien produit des fichiers dans data/raw/.")
        return

    print(f"Chargement du modèle d'embeddings ({MODELE_EMBEDDINGS})...")
    print("  (premier lancement : téléchargement depuis Hugging Face, "
          "peut prendre quelques minutes ; mis en cache ensuite)")
    modele = SentenceTransformer(MODELE_EMBEDDINGS)

    print(f"Initialisation de ChromaDB ({CHROMA_DB_DIR})...")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    # On repart d'une collection vide à chaque exécution : sans ça, relancer
    # ce script plusieurs fois dupliquerait les chunks (nouveaux UUID à
    # chaque appel). Pratique aussi quand on modifie SOURCES/PDF_SOURCES.
    collections_existantes = [c.name for c in client.list_collections()]
    if NOM_COLLECTION in collections_existantes:
        client.delete_collection(NOM_COLLECTION)
    collection = client.get_or_create_collection(name=NOM_COLLECTION)

    print(f"Vectorisation et indexation ({TAILLE_LOT} chunks par lot)...")
    for debut in range(0, len(chunks), TAILLE_LOT):
        lot = chunks[debut:debut + TAILLE_LOT]
        textes_lot = [c["texte"] for c in lot]

        embeddings_lot = modele.encode(textes_lot, show_progress_bar=False).tolist()

        collection.add(
            ids=[c["id"] for c in lot],
            embeddings=embeddings_lot,
            documents=textes_lot,
            metadatas=[c["metadata"] for c in lot],
        )
        print(f"  -> {min(debut + TAILLE_LOT, len(chunks))}/{len(chunks)} chunks indexés")

    print(f"\nTerminé : {collection.count()} chunk(s) dans la collection '{NOM_COLLECTION}'.")


if __name__ == "__main__":
    main()
