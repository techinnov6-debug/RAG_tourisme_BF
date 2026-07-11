"""
Fonctions utilitaires partagées par les différentes sources de collecte
(pages web ET fichiers PDF), pour éviter de dupliquer la logique de
nettoyage à deux endroits.
"""

import re


def nettoyer_texte(texte_brut: str) -> str:
    """
    Normalise un texte brut (issu du HTML ou d'un PDF) :
    - retire les lignes vides et les espaces superflus
    - fusionne les sauts de ligne multiples
    """
    lignes = [ligne.strip() for ligne in texte_brut.split("\n")]
    lignes = [ligne for ligne in lignes if ligne]
    texte_propre = "\n".join(lignes)
    texte_propre = re.sub(r"\n{2,}", "\n", texte_propre)
    return texte_propre
