"""
Script principal de collecte de données (Étape 1).

Usage :
    python collect_data.py     (depuis la racine du projet ou depuis ingestion/)

Résultat :
    - Pages web : data/raw/<source_slug>/page_001.txt, page_002.txt, ...
      (une source = potentiellement plusieurs pages grâce au crawl)
    - PDF       : data/raw/<source_slug>.txt (un seul fichier, pas de crawl)
    - Un manifest data/manifest.json qui répertorie CHAQUE page/fichier
      collecté avec ses métadonnées (utilisé ensuite pour le chunking).
"""

import json
import os
import re

from config import (
    SOURCES, PDF_SOURCES, PDF_DIR, RAW_DATA_DIR,
    PROFONDEUR_MAX, MAX_PAGES_PAR_SOURCE,
)
from scraper import crawler_source
from pdf_loader import collecter_pdf


def slugifier(nom: str) -> str:
    """Transforme un nom de source en nom de fichier/dossier sûr."""
    nom = nom.lower()
    remplacements = {
        "é": "e", "è": "e", "ê": "e", "à": "a", "î": "i", "ï": "i",
        "ô": "o", "û": "u", "ù": "u", "ç": "c", "'": "", "-": "_",
    }
    for caractere, remplacement in remplacements.items():
        nom = nom.replace(caractere, remplacement)
    nom = re.sub(r"[^a-z0-9]+", "_", nom)
    return nom.strip("_")


def enregistrer_pages_web(nom_source: str, pages: list, manifest: list) -> None:
    """Sauvegarde chaque page crawlée d'une source dans son propre sous-dossier."""
    slug = slugifier(nom_source)
    dossier_source = os.path.join(RAW_DATA_DIR, slug)
    os.makedirs(dossier_source, exist_ok=True)

    for i, page in enumerate(pages, start=1):
        nom_fichier = f"page_{i:03d}.txt"
        chemin_relatif = os.path.join(slug, nom_fichier)

        if page["statut"] == "ok":
            with open(os.path.join(dossier_source, nom_fichier), "w", encoding="utf-8") as f:
                f.write(page["texte"])

        manifest.append({
            "nom": nom_source,
            "url": page["url"],
            "categorie": page["categorie"],
            "type": "web",
            "statut": page["statut"],
            "fichier": chemin_relatif if page["statut"] == "ok" else None,
        })


def enregistrer_pdf(resultat: dict, manifest: list) -> None:
    """Sauvegarde le texte extrait d'un PDF (un seul fichier, pas de crawl)."""
    nom_fichier = slugifier(resultat["nom"]) + ".txt"

    if resultat["statut"] == "ok":
        with open(os.path.join(RAW_DATA_DIR, nom_fichier), "w", encoding="utf-8") as f:
            f.write(resultat["texte"])

    manifest.append({
        "nom": resultat["nom"],
        "url": resultat["url"],
        "categorie": resultat["categorie"],
        "type": "pdf",
        "statut": resultat["statut"],
        "fichier": nom_fichier if resultat["statut"] == "ok" else None,
    })


def main():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    manifest = []

    print(f"Début de la collecte : {len(SOURCES)} site(s) web à crawler, "
          f"{len(PDF_SOURCES)} PDF à extraire\n")

    # --- Sources web (crawl multi-pages) ---
    for source in SOURCES:
        pages = crawler_source(source, PROFONDEUR_MAX, MAX_PAGES_PAR_SOURCE)
        enregistrer_pages_web(source["nom"], pages, manifest)
        nb_ok = sum(1 for p in pages if p["statut"] == "ok")
        print(f"  => {nb_ok}/{len(pages)} page(s) sauvegardée(s) pour {source['nom']}\n")

    # --- Sources PDF (fichiers locaux dans PDF_DIR) ---
    for source_pdf in PDF_SOURCES:
        resultat = collecter_pdf(source_pdf, PDF_DIR)
        enregistrer_pdf(resultat, manifest)

    chemin_manifest = os.path.join(os.path.dirname(RAW_DATA_DIR), "manifest.json")
    with open(chemin_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    nb_ok = sum(1 for m in manifest if m["statut"] == "ok")
    print(f"Collecte terminée : {nb_ok}/{len(manifest)} page(s)/fichier(s) au total.")
    print(f"Manifeste écrit dans : {chemin_manifest}")


if __name__ == "__main__":
    main()