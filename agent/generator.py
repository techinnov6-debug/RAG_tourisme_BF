"""
Construction du prompt RAG et appel au LLM via l'API Groq.
"""

import requests


from config import (
    GROQ_API_URL, GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS,
    PROMPT_SYSTEME,
)

MESSAGE_JE_NE_SAIS_PAS = (
    "Je ne dispose pas de cette information dans les documents dont je "
    "dispose sur le Burkina Faso. Je mènerai des recherches plus approffondies"
    "afin d'être prêt la prochaine fois. Merci pour votre compréhension."
)


def construire_prompt(question: str, contextes: list) -> list:
    """
    Construit la liste de messages (format OpenAI-compatible, utilisé par
    Groq) à partir de la question et des chunks de contexte récupérés.
    """
    blocs_contexte = []
    for i, ctx in enumerate(contextes, start=1):
        nom_source = ctx["metadata"].get("nom_source", "Source inconnue")
        blocs_contexte.append(f"[Extrait {i} - Source : {nom_source}]\n{ctx['texte']}")

    contexte_complet = "\n\n".join(blocs_contexte)

    message_utilisateur = (
        f"CONTEXTE :\n{contexte_complet}\n\n"
        f"QUESTION :\n{question}"
    )

    return [
        {"role": "system", "content": PROMPT_SYSTEME},
        {"role": "user", "content": message_utilisateur},
    ]


def interroger_llm(messages: list) -> str:
    """
    Envoie les messages au LLM via l'API Groq et retourne le texte de
    réponse. En cas d'échec (clé API manquante, erreur réseau, erreur
    HTTP), retourne un message d'erreur clair plutôt que de faire
    planter l'application -- important pour une interface Streamlit qui
    doit rester utilisable même en cas de souci ponctuel avec l'API.
    """
    if not GROQ_API_KEY:
        return (
            "[ERREUR] La clé d'API Groq n'est pas configurée. "
            "Définis la variable d'environnement GROQ_API_KEY avant de lancer l'application."
        )

    entete = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    corps = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": GROQ_TEMPERATURE,
        "max_completion_tokens": GROQ_MAX_TOKENS,
    }

    try:
        reponse = requests.post(GROQ_API_URL, headers=entete, json=corps, timeout=30)
        reponse.raise_for_status()
    except requests.RequestException as erreur:
        return f"[ERREUR] Échec de l'appel à l'API Groq : {erreur}"

    donnees = reponse.json()
    try:
        return donnees["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return f"[ERREUR] Réponse inattendue de l'API Groq : {donnees}"
