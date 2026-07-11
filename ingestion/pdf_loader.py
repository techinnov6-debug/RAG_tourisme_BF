"""
Extraction de texte à partir de fichiers PDF locaux (Étape 1 - sources PDF).

Les PDF doivent être placés dans le dossier data/pdfs/ (voir config.PDF_DIR).
Ce module ne fait AUCUN scraping : il lit des fichiers déjà présents sur disque.
"""

import os
from pypdf import PdfReader
from utils import nettoyer_texte


def extraire_texte_pdf(chemin_pdf: str) -> str:
    """
    Extrait le texte de toutes les pages d'un PDF et le nettoie.
    Retourne une chaîne vide si le PDF est scanné (image) sans couche de
    texte, ou si le fichier est corrompu/protégé -- ce cas doit être signalé
    à l'utilisateur pour un traitement OCR complémentaire (Ne sera pas pris en compte pour le moment dans
    de ce module).
    """
    lecteur = PdfReader(chemin_pdf)

    if lecteur.is_encrypted:
        print(f"  [ATTENTION] PDF protégé, tentative de déverrouillage : {chemin_pdf}")
        lecteur.decrypt("")  # tente un mot de passe vide, cas fréquent des PDF publics

    morceaux_par_page = []
    for numero_page, page in enumerate(lecteur.pages, start=1):
        texte_page = page.extract_text() or ""
        if not texte_page.strip():
            print(f"  [AVERTISSEMENT] Page {numero_page} sans texte extractible "
                  f"(probablement un PDF scanné/image) : {chemin_pdf}")
        morceaux_par_page.append(texte_page)

    texte_brut = "\n".join(morceaux_par_page)
    return nettoyer_texte(texte_brut)


def collecter_pdf(source_pdf: dict, dossier_pdfs: str) -> dict:
    """
    Traite une entrée de config.PDF_SOURCES.
    Retourne un dictionnaire au même format que scraper.collecter_source,
    pour pouvoir être fusionné dans le même manifeste.
    """
    chemin_complet = os.path.join(dossier_pdfs, source_pdf["fichier"])
    print(f"Extraction PDF : {source_pdf['nom']} ({chemin_complet})")

    if not os.path.exists(chemin_complet):
        print(f"  [ECHEC] Fichier introuvable : {chemin_complet}")
        return {
            "nom": source_pdf["nom"],
            "url": chemin_complet,
            "categorie": source_pdf["categorie"],
            "statut": "echec",
            "type": "pdf",
            "texte": "",
        }

    try:
        texte = extraire_texte_pdf(chemin_complet)
    except Exception as erreur:
        print(f"  [ECHEC] Erreur de lecture PDF : {erreur}")
        return {
            "nom": source_pdf["nom"],
            "url": chemin_complet,
            "categorie": source_pdf["categorie"],
            "statut": "echec",
            "type": "pdf",
            "texte": "",
        }

    return {
        "nom": source_pdf["nom"],
        "url": chemin_complet,
        "categorie": source_pdf["categorie"],
        "statut": "ok",
        "type": "pdf",
        "texte": texte,
    }
