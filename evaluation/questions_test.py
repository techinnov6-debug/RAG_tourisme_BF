"""
Jeu de questions de test pour l'évaluation du système (Phase 5).

Deux catégories, conformément à l'énoncé :
- "dans_perimetre"  : questions dont la réponse DOIT se trouver dans la
                      base documentaire (Burkina Faso). Sert à mesurer la
                      pertinence de la recherche vectorielle.
- "hors_perimetre"  : questions sans rapport avec le corpus. Sert à
                      mesurer le taux d'hallucination -- l'agent doit
                      répondre "je ne sais pas", pas inventer.

Pour les questions "dans_perimetre", `categorie_attendue` doit correspondre
à une valeur du champ "categorie" utilisé dans ingestion/config.py
(institution, evenement, site_culturel, formalites).

À COMPLÉTER/AJUSTER par le groupe selon le contenu réellement collecté.
"""

QUESTIONS_TEST = [
    # --- Dans le périmètre (Burkina Faso) ---
    {
        "question": "Où se trouvent les cascades de Banfora ?",
        "type": "dans_perimetre",
        "categorie_attendue": "site_culturel",
    },
    {
        "question": "Qu'est-ce que le FESPACO et quand a-t-il lieu ?",
        "type": "dans_perimetre",
        "categorie_attendue": "evenement",
    },
    {
        "question": "Qu'est-ce que le SIAO ?",
        "type": "dans_perimetre",
        "categorie_attendue": "evenement",
    },
    {
        "question": "Quels sont les sites classés au patrimoine mondial de l'UNESCO au Burkina Faso ?",
        "type": "dans_perimetre",
        "categorie_attendue": "site_culturel",
    },
    {
        "question": "Que peut-on visiter dans le parc national d'Arly ?",
        "type": "dans_perimetre",
        "categorie_attendue": "site_culturel",
    },
    {
        "question": "Quelles sont les formalités de visa pour se rendre au Burkina Faso ?",
        "type": "dans_perimetre",
        "categorie_attendue": "formalites",
    },
    {
        "question": "Que peut-on trouver à Loropéni ?",
        "type": "dans_perimetre",
        "categorie_attendue": "site_culturel",
    },
    {
        "question": "Quelle agence gère le tourisme au Burkina Faso ?",
        "type": "dans_perimetre",
        "categorie_attendue": "institution",
    },

    # --- Hors périmètre (doit déclencher "je ne sais pas") ---
    {
        "question": "Quelle est la meilleure période pour visiter le Japon ?",
        "type": "hors_perimetre",
    },
    {
        "question": "Comment obtenir un visa pour les États-Unis ?",
        "type": "hors_perimetre",
    },
    {
        "question": "Quels sont les meilleurs restaurants à Paris ?",
        "type": "hors_perimetre",
    },
    {
        "question": "Explique-moi la théorie de la relativité d'Einstein.",
        "type": "hors_perimetre",
    },
    {
        "question": "Quel est le prix d'un billet pour la tour Eiffel ?",
        "type": "hors_perimetre",
    },
]
