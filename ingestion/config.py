"""
Configuration des sources de données pour l'agent RAG
Guide Touristique et Culturel Intelligent - Destination Burkina Faso

Chaque source est décrite par :
- nom       : nom lisible de la source
- url       : URL de départ à scraper
- categorie : type d'information (institution, evenement, site_culturel, formalites)
- notes     : précisions utiles pour l'ingestion (ex : pages à privilégier)

IMPORTANT : ces URLs ont été vérifiées via une recherche web au moment de la
rédaction de ce projet (juillet 2026). Il est recommandé de revérifier leur
disponibilité avant de lancer le scraping, certains sites institutionnels
burkinabè changeant régulièrement de structure ou d'hébergement.
"""

import os

# Racine du projet = dossier parent de ce fichier ingestion/config.py.
# Ainsi les chemins fonctionnent qu'on lance le script depuis la racine
# du projet ou depuis le dossier ingestion/.
RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SOURCES = [
    {
        "nom": "Discover Burkina",
        "url": "https://discover-burkinafaso.com/",
        "categorie": "institution",
        "notes": (
            "Site de reference qui regroupe la majeur partie des sites du Burkina Faso"
            "Site principal pour les destinations, "
            "hébergements et informations pratiques générales (culture,langue,ethnie,.)"
        ),
    },
    {
        "nom": "Booking.com",
        "url": "https://www.booking.com/",
        "categorie": "formalites",
        "filtre_url": ["burkina"],
        "max_pages": 40,
        "notes": (
            "site internet pour réserver des voyages. ATTENTION : les listes "
            "d'hébergements sont chargées en JavaScript, requests/BeautifulSoup "
            "ne récupèrera que la coquille statique de la page, pas les offres."
        ),
    },
    {
        "nom": "Partir.com",
        "url": "https://www.partir.com/Burkina-faso/lieux-d-interet.html#modal-312029219",
        "categorie": "formalites",
        "filtre_url": ["burkina"],
        "max_pages": 40,
        "notes": ("Site internet permettant de voir quelques sites touristiques du Burkina et d'y réserver un billet"
                  "Se renseigner sur les tarifs des vols, des prix du déplacement, l'essence et bien d'autres"
                  "Faire une proposition des agences de voyage"),
    },
    {
        "nom": "Evaneos.com",
        "url": "https://www.evaneos.fr/burkina-faso/#Breadcrumb",
        "categorie": "formalites",
        "filtre_url": ["burkina"],
        "max_pages": 40,
        "notes": "Agence de voyage pour internationaux",
    },
    {
        "nom": "FESPACO - Festival Panafricain du Cinéma de Ouagadougou",
        "url": "https://fespaco.bf/",
        "categorie": "evenement",
        "notes": (
            "Informations sur les dates d'édition, le programme et les "
            "conditions d'accès au festival."
        ),
    },
    {
        "nom": "SIAO - Salon International de l'Artisanat de Ouagadougou",
        "url": "https://siao.bf/",
        "categorie": "evenement",
        "notes": "Dates du salon, thème de l'édition, informations pratiques.",
    },
    {
        "nom": "Discover - Burkina Faso (formalités administrative)",
        "url": "https://discover-burkinafaso.com/visa-sante-securite/",
        "categorie": "formalites",
        "notes": "Utile pour les formalités de visa précises ainsi que les conditions d'accès",
    },
    {
        "nom": "Wikipedia - Patrimoine mondial du Burkina",
        "url": "https://fr.wikipedia.org/wiki/Liste_du_patrimoine_mondial_au_Burkina_Faso",
        "categorie": "site_culturel",
        "notes": "Vue d'ensemble des sites inscrits au patrimoine mondial au Burkina Faso",
    },
    {
        "nom": "Wikipedia - Ruines de Loropéni",
        "url": "https://fr.wikipedia.org/wiki/Ruines_de_Loropéni",
        "categorie": "site_culturel",
        "notes": "Site classé au patrimoine mondial de l'UNESCO.",
    },
    {
        "nom": "Wikipedia - Cascades de Karfiguéla",
        "url": "https://fr.wikipedia.org/wiki/Cascades_de_Karfiguéla",
        "categorie": "site_culturel",
        "notes": "Site naturel près de Banfora.",
    },
    {
        "nom": "Wikipedia - Pics de Sindou",
        "url": "https://fr.wikipedia.org/wiki/Pics_de_Sindou",
        "categorie": "site_culturel",
        "notes": "Formations rocheuses, randonnée.",
    },
    {
        "nom": "Wikipedia - Parc national d'Arly",
        "url": "https://fr.wikipedia.org/wiki/Parc_national_d%27Arly",
        "categorie": "site_culturel",
        "notes": "Parc national, faune (éléphants, lions, hippopotames).",
    },
    {
        "nom": "Wikipedia - Tourisme au Burkina Faso",
        "url": "https://fr.wikipedia.org/wiki/Tourisme_au_Burkina_Faso",
        "categorie": "site_culturel",
        "notes": "Vue d'ensemble générale du secteur touristique national.",
    },
    
]

# Dossier où DÉPOSER MANUELLEMENT les fichiers PDF officiels avant de lancer
# la collecte (ex : brochures Faso Tourisme, programme FESPACO en PDF,
# fiches pratiques consulaires, etc.)
PDF_DIR = os.path.join(RACINE_PROJET, "data", "pdfs")

# Métadonnées des PDF à traiter. Le champ "fichier" doit correspondre
# exactement au nom du fichier déposé dans PDF_DIR.
# Cette liste est à compléter au fur et à mesure que des PDF sont ajoutés.

PDF_SOURCES = [
    # Exemple à adapter/compléter :
    # {
    #     "nom": "Guide pratique du voyageur - Faso Tourisme",
    #     "fichier": "guide_voyageur_faso_tourisme.pdf",
    #     "categorie": "formalites",
    #     "notes": "Brochure officielle téléchargée manuellement depuis ontb.bf",
    # },
]

# Dossier de sortie pour les données brutes collectées (web ET pdf, mêmes format)
RAW_DATA_DIR = os.path.join(RACINE_PROJET, "data", "raw")

# --- Paramètres du crawl multi-pages ---
# Profondeur par défaut : 0 = uniquement l'URL donnée, 1 = + ses liens directs,
# 2 = + les liens des pages de niveau 1, etc.
PROFONDEUR_MAX = 2

# Nombre maximum de pages collectées par source (protection contre un crawl
# qui partirait sur un site immense comme booking.com ou evaneos.fr)
# Nombre maximum de pages collectées par source, PAR DÉFAUT (peut être
# surchargé par source via la clé "max_pages" dans SOURCES). Relevé car la
# plupart de nos sources sont des sites 100% Burkina Faso, sans risque de
# crawl infini -- seule exception : les plateformes mondiales (Booking,
# Evaneos, Partir), bridées individuellement plus bas via "filtre_url".
MAX_PAGES_PAR_SOURCE = 80

# Si True, vérifie le robots.txt de chaque domaine avant de scraper une page
RESPECTER_ROBOTS_TXT = True

# Délai (en secondes) entre deux requêtes, pour rester respectueux des serveurs
DELAI_ENTRE_REQUETES = 3

# En-tête HTTP identifiant clairement le scraper (bonne pratique académique)
# + Accept-Language pour indiquer au serveur qu'on préfère la version française
# (utile sur les sites qui servent une langue différente selon cet en-tête).
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ProjetIFOAD-RAG-Tourisme/1.0; "
        "usage academique; contact: etudiant-ifoad@example.com)"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.3",
}

# Segments d'URL trahissant une langue autre que le français (souvent codés
# en dur dans l'URL, indépendamment de l'en-tête Accept-Language ci-dessus).
# Toute URL contenant un de ces segments est ignorée pendant le crawl.
EXCLURE_SEGMENTS_URL = [
    "/en/", "/en-us/", "/en-gb/", "/english/",
    "/es/", "/es-es/", "/espanol/",
    "/de/", "/deutsch/",
    "/pt/", "/pt-br/", "/portugues/",
    "/it/", "/italiano/",
    "?lang=en", "?lang=es", "?lang=de", "?lang=pt", "?lang=it",
    "/zh/", "/ar/", "/nl/",
]

# --- Détection de langue par contenu (en complément du filtre par URL) ---
# Certains sites servent du contenu en anglais (ou autre) sans que ce soit
# visible dans l'URL ou malgré l'en-tête Accept-Language. On vérifie donc
# aussi la langue réelle du texte extrait de chaque page.
LANGUE_CIBLE = "fr"
FILTRER_PAR_CONTENU = True

# Longueur minimale (caractères) en dessous de laquelle la détection de
# langue n'est pas fiable -- on garde alors la page par défaut plutôt que
# de la rejeter à tort.
LONGUEUR_MIN_DETECTION = 40