"""
Découpage (chunking) de texte en segments de taille contrôlée.

Stratégie : découpage récursif par séparateurs, du plus "naturel" au
moins naturel (paragraphe -> phrase -> mot), pour éviter de couper une
idée en plein milieu autant que possible. Implémentation volontairement
"maison" (pas de dépendance à langchain) pour rester simple et lisible.
"""

SEPARATEURS = ["\n\n", "\n", ". ", " "]


def _decouper_avec_separateur(texte: str, separateur: str, taille_max: int) -> list:
    """Découpe le texte au niveau du séparateur donné, en regroupant les
    morceaux tant que la taille_max n'est pas dépassée."""
    morceaux = texte.split(separateur) if separateur else list(texte)
    segments = []
    segment_courant = ""

    for morceau in morceaux:
        candidat = segment_courant + separateur + morceau if segment_courant else morceau
        if len(candidat) <= taille_max:
            segment_courant = candidat
        else:
            if segment_courant:
                segments.append(segment_courant)
            # Le morceau seul dépasse déjà la taille max : on le renverra
            # tel quel, il sera re-découpé récursivement par l'appelant.
            segment_courant = morceau

    if segment_courant:
        segments.append(segment_courant)

    return segments


def decouper_texte(texte: str, taille_chunk: int, chevauchement: int,
                    separateurs: list = None) -> list:
    """
    Découpe un texte en chunks de taille approximative `taille_chunk`
    (en caractères), avec un chevauchement `chevauchement` entre chunks
    consécutifs.

    Retourne une liste de chaînes de caractères (les chunks).
    """
    if not texte or not texte.strip():
        return []

    separateurs = separateurs or SEPARATEURS

    # Étape 1 : découpage récursif par séparateurs successifs
    segments = [texte]
    for separateur in separateurs:
        nouveaux_segments = []
        for segment in segments:
            if len(segment) <= taille_chunk:
                nouveaux_segments.append(segment)
            else:
                nouveaux_segments.extend(
                    _decouper_avec_separateur(segment, separateur, taille_chunk)
                )
        segments = nouveaux_segments

    # Étape 2 : regroupement des segments trop petits + application du
    # chevauchement entre chunks consécutifs
    chunks = []
    chunk_courant = ""

    for segment in segments:
        candidat = f"{chunk_courant} {segment}".strip() if chunk_courant else segment
        if len(candidat) <= taille_chunk:
            chunk_courant = candidat
        else:
            if chunk_courant:
                chunks.append(chunk_courant)
            # on démarre le nouveau chunk avec le chevauchement de la fin
            # du chunk précédent, pour garder du contexte
            queue_chevauchement = chunk_courant[-chevauchement:] if chunk_courant else ""
            chunk_courant = f"{queue_chevauchement} {segment}".strip()

    if chunk_courant:
        chunks.append(chunk_courant)

    return [c for c in chunks if c.strip()]
