"""
Fonctions de collecte et de nettoyage de pages web pour le projet RAG.

Nouveauté : le scraper ne se limite plus à une seule page par source.
Il explore (crawle) les liens internes du même site, en largeur (BFS),
jusqu'à une profondeur et un nombre de pages maximum définis dans config.py.
"""

import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

from config import (
    HEADERS, DELAI_ENTRE_REQUETES, RESPECTER_ROBOTS_TXT, EXCLURE_SEGMENTS_URL,
    LANGUE_CIBLE, FILTRER_PAR_CONTENU, LONGUEUR_MIN_DETECTION,
)
from utils import nettoyer_texte

# Extensions de fichiers à ignorer lors du crawl (pas des pages HTML utiles)
EXTENSIONS_IGNOREES = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".mp4",
    ".mp3", ".css", ".js", ".ico", ".woff", ".woff2", ".xml",
)

_CACHE_ROBOTS = {}


def telecharger_page(url: str) -> str | None:
    """
    Télécharge le HTML brut d'une page. Retourne None en cas d'échec
    (site indisponible, timeout, erreur HTTP), sans faire planter le script.
    """
    try:
        reponse = requests.get(url, headers=HEADERS, timeout=15)
        reponse.raise_for_status()
        return reponse.text
    except requests.RequestException as erreur:
        print(f"  [ECHEC] {url} -> {erreur}")
        return None


def autorise_par_robots(url: str) -> bool:
    """
    Vérifie le fichier robots.txt du domaine avant de scraper une page.
    En cas de doute (robots.txt inaccessible), on autorise par défaut
    plutôt que de bloquer tout le crawl.
    """
    if not RESPECTER_ROBOTS_TXT:
        return True

    domaine = urlparse(url).netloc
    if domaine not in _CACHE_ROBOTS:
        parseur = urllib.robotparser.RobotFileParser()
        parseur.set_url(f"https://{domaine}/robots.txt")
        try:
            parseur.read()
        except Exception:
            _CACHE_ROBOTS[domaine] = None  # inconnu -> tolérant
            return True
        _CACHE_ROBOTS[domaine] = parseur

    parseur = _CACHE_ROBOTS[domaine]
    if parseur is None:
        return True
    return parseur.can_fetch(HEADERS["User-Agent"], url)


def detecter_langue(texte: str) -> str | None:
    """
    Détecte la langue dominante d'un texte. Retourne None si le texte est
    trop court pour une détection fiable (on garde alors la page par
    défaut plutôt que de la rejeter à tort).
    """
    if len(texte.strip()) < LONGUEUR_MIN_DETECTION:
        return None
    try:
        return detect(texte)
    except LangDetectException:
        return None


def nettoyer_html(html: str) -> str:
    """
    Extrait le texte utile d'une page HTML :
    - retire les balises non textuelles (script, style, nav, footer, header)
    - normalise les espaces et sauts de ligne multiples
    """
    soup = BeautifulSoup(html, "html.parser")

    for balise in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        balise.decompose()

    texte = soup.get_text(separator="\n")
    return nettoyer_texte(texte)


def extraire_liens_internes(html: str, url_page: str, domaine_racine: str) -> set:
    """
    Extrait tous les liens <a href="..."> qui pointent vers le même domaine
    que la source de départ, en ignorant ancres, fichiers non-HTML et liens externes.
    """
    soup = BeautifulSoup(html, "html.parser")
    liens = set()

    for balise_a in soup.find_all("a", href=True):
        href = balise_a["href"].split("#")[0].strip()
        if not href or href.startswith("mailto:") or href.startswith("tel:"):
            continue

        url_absolue = urljoin(url_page, href)
        parsed = urlparse(url_absolue)

        if parsed.netloc != domaine_racine:
            continue
        if url_absolue.lower().endswith(EXTENSIONS_IGNOREES):
            continue

        # on retire les paramètres de requête pour éviter les doublons type ?page=1&sort=x
        url_normalisee = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        liens.add(url_normalisee)

    return liens


def crawler_source(source: dict, profondeur_max: int, max_pages: int) -> list:
    """
    Explore un site en largeur (BFS) à partir de source["url"], en restant
    sur le même domaine, jusqu'à profondeur_max ou max_pages atteint(e).

    Les valeurs profondeur_max / max_pages peuvent être surchargées par
    source via les clés optionnelles "profondeur" et "max_pages" dans
    config.SOURCES.

    Retourne une liste de dictionnaires, un par page réellement collectée :
    {nom, url, categorie, statut, texte}
    """
    profondeur_max = source.get("profondeur", profondeur_max)
    max_pages = source.get("max_pages", max_pages)

    url_depart = source["url"]
    domaine_racine = urlparse(url_depart).netloc

    a_visiter = [(url_depart, 0)]
    deja_vues = {url_depart}
    resultats = []

    print(f"Crawl : {source['nom']} (domaine {domaine_racine}, "
          f"profondeur max {profondeur_max}, {max_pages} pages max)")

    filtre_mots_cles = source.get("filtre_url")  # ex: ["burkina"], None = pas de filtre

    while a_visiter and len(resultats) < max_pages:
        url_courante, profondeur = a_visiter.pop(0)

        if not autorise_par_robots(url_courante):
            print(f"  [IGNORE] robots.txt interdit : {url_courante}")
            continue

        html = telecharger_page(url_courante)
        time.sleep(DELAI_ENTRE_REQUETES)

        if html is None:
            resultats.append({
                "nom": source["nom"], "url": url_courante,
                "categorie": source["categorie"], "statut": "echec", "texte": "",
            })
            continue

        texte = nettoyer_html(html)

        langue_detectee = detecter_langue(texte) if FILTRER_PAR_CONTENU else None
        if langue_detectee is not None and langue_detectee != LANGUE_CIBLE:
            print(f"  [IGNORE langue={langue_detectee}] {url_courante}")
        else:
            resultats.append({
                "nom": source["nom"], "url": url_courante,
                "categorie": source["categorie"], "statut": "ok", "texte": texte,
            })
            print(f"  -> ({len(resultats)}/{max_pages}) {url_courante} "
                  f"[{len(texte)} caractères, profondeur {profondeur}]")

        if profondeur < profondeur_max:
            for lien in extraire_liens_internes(html, url_courante, domaine_racine):
                if lien in deja_vues:
                    continue
                if any(segment in lien.lower() for segment in EXCLURE_SEGMENTS_URL):
                    continue
                if filtre_mots_cles and not any(mot in lien.lower() for mot in filtre_mots_cles):
                    continue
                deja_vues.add(lien)
                a_visiter.append((lien, profondeur + 1))

    return resultats