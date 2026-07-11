"""
Point d'entrée de la logique de l'agent : combine recherche vectorielle
et génération LLM, avec une protection contre l'hallucination quand le
contexte trouvé n'est pas pertinent (cf. Phase 5 de l'énoncé : "L'agent
sait-il dire 'je ne sais pas' si l'information n'est pas dans les
documents ?").
"""

from config import SEUIL_DISTANCE_MAX
from retriever import rechercher_contexte
from generator import construire_prompt, interroger_llm, MESSAGE_JE_NE_SAIS_PAS
from groq import Groq

def repondre(question: str) -> dict:
    """
    Traite une question utilisateur de bout en bout.

    Retourne un dictionnaire :
    {
        "reponse": str,           -- texte à afficher à l'utilisateur
        "contextes_utilises": [...],  -- chunks récupérés (pour debug/affichage des sources)
        "hors_perimetre": bool,   -- True si on a jugé le contexte non pertinent
    }
    """
    contextes = rechercher_contexte(question)

    if not contextes or contextes[0]["distance"] > SEUIL_DISTANCE_MAX:
        return {
            "reponse": MESSAGE_JE_NE_SAIS_PAS,
            "contextes_utilises": contextes,
            "hors_perimetre": True,
        }

    messages = construire_prompt(question, contextes)
    reponse_llm = interroger_llm(messages)

    return {
        "reponse": reponse_llm,
        "contextes_utilises": contextes,
        "hors_perimetre": False,
    }


def boucle_interactive():
    """Petite boucle en ligne de commande pour tester l'agent avant la Phase 4 (UI)."""
    print("Assistant Guide Touristique Burkina Faso (tape 'quitter/sortir' pour arrêter)\n")
    while True:
        question = input("Question : ").strip()
        if question.lower() in ("quitter", "exit", "quit","sort","sortir"):
            break
        if not question:
            continue

        resultat = repondre(question)
        print(f"\nRéponse : {resultat['reponse']}\n")

        if not resultat["hors_perimetre"]:
            sources = {c["metadata"].get("nom_source") for c in resultat["contextes_utilises"]}
            print(f"(Sources consultées : {', '.join(sources)})\n")


if __name__ == "__main__":
    boucle_interactive()
