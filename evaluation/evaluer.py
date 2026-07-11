"""
Script d'évaluation du système (Phase 5), conformément à l'énoncé :
- Mesurer la pertinence des documents récupérés.
- Évaluer le taux d'hallucination (l'agent sait-il dire "je ne sais pas" ?).

Usage :
    python evaluation/evaluer.py

Résultat :
    - Un résumé affiché dans le terminal.
    - Un fichier evaluation/resultats_evaluation.csv (réutilisable
      directement dans le rapport technique, section "Limites et
      perspectives").
"""

import csv
import os
import sys
import time

RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Pont vers agent/ (mêmes imports "plats" que dans app.py -- cf. note de
# dette technique à nettoyer en Phase 6)
sys.path.insert(0, os.path.join(RACINE_PROJET, "agent"))

from assistant import repondre  # noqa: E402

from questions_test import QUESTIONS_TEST

CHEMIN_RESULTATS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultats_evaluation.csv")


def evaluer_question(item: dict) -> dict:
    """Exécute une question de test à travers l'agent et calcule les métriques associées."""
    debut = time.perf_counter()
    resultat = repondre(item["question"])
    duree = time.perf_counter() - debut

    contextes = resultat["contextes_utilises"]
    distance_top1 = contextes[0]["distance"] if contextes else None

    ligne = {
        "question": item["question"],
        "type": item["type"],
        "distance_top1": round(distance_top1, 4) if distance_top1 is not None else "",
        "hors_perimetre_declare": resultat["hors_perimetre"],
        "duree_secondes": round(duree, 2),
        "reponse": resultat["reponse"].replace("\n", " ")[:200],
    }

    if item["type"] == "dans_perimetre":
        categories_trouvees = {c["metadata"].get("categorie") for c in contextes}
        ligne["pertinent"] = item["categorie_attendue"] in categories_trouvees
        ligne["hallucination"] = None  # non applicable pour ce type de question
    else:
        # Pour une question hors périmètre, le "bon" comportement est que
        # l'agent déclare hors_perimetre=True. Sinon, il a probablement halluciné.
        ligne["pertinent"] = None  # non applicable
        ligne["hallucination"] = not resultat["hors_perimetre"]

    return ligne


def main():
    print(f"Évaluation de {len(QUESTIONS_TEST)} question(s) de test...\n")

    resultats = []
    for item in QUESTIONS_TEST:
        print(f"  - [{item['type']}] {item['question']}")
        resultats.append(evaluer_question(item))

    # --- Écriture du CSV ---
    with open(CHEMIN_RESULTATS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(resultats[0].keys()))
        writer.writeheader()
        writer.writerows(resultats)

    # --- Calcul des métriques agrégées ---
    dans_perimetre = [r for r in resultats if r["pertinent"] is not None]
    hors_perimetre = [r for r in resultats if r["hallucination"] is not None]

    nb_pertinents = sum(1 for r in dans_perimetre if r["pertinent"])
    nb_hallucinations = sum(1 for r in hors_perimetre if r["hallucination"])

    print("\n" + "=" * 60)
    print("RÉSUMÉ DE L'ÉVALUATION")
    print("=" * 60)

    if dans_perimetre:
        taux_pertinence = 100 * nb_pertinents / len(dans_perimetre)
        print(f"Pertinence de la recherche : {nb_pertinents}/{len(dans_perimetre)} "
              f"({taux_pertinence:.0f}%) -- catégorie attendue trouvée dans le top-k")

    if hors_perimetre:
        taux_hallucination = 100 * nb_hallucinations / len(hors_perimetre)
        print(f"Taux d'hallucination : {nb_hallucinations}/{len(hors_perimetre)} "
              f"({taux_hallucination:.0f}%) -- l'agent a répondu au lieu de dire "
              f"'je ne sais pas' sur une question hors périmètre")

    print(f"\nRésultats détaillés écrits dans : {CHEMIN_RESULTATS}")

    # --- Aide à la calibration du seuil (cf. agent/config.py SEUIL_DISTANCE_MAX) ---
    distances_dans = [r["distance_top1"] for r in dans_perimetre if r["distance_top1"] != ""]
    distances_hors = [r["distance_top1"] for r in hors_perimetre if r["distance_top1"] != ""]
    if distances_dans and distances_hors:
        print("\nAide à la calibration de SEUIL_DISTANCE_MAX (agent/config.py) :")
        print(f"  - distances (dans périmètre)  : min={min(distances_dans):.3f}  max={max(distances_dans):.3f}")
        print(f"  - distances (hors périmètre)  : min={min(distances_hors):.3f}  max={max(distances_hors):.3f}")
        print("  Un bon seuil se situe entre les deux plages ci-dessus, si elles ne se chevauchent pas trop.")


if __name__ == "__main__":
    main()
