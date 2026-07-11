"""
Interface utilisateur Streamlit de l'assistant guide touristique
Burkina Faso (Phase 4).

Usage :
    streamlit run app.py

Prérequis : avoir exécuté, dans l'ordre, ingestion/collect_data.py puis
vectorisation/build_vector_store.py, et avoir défini la variable
d'environnement GROQ_API_KEY.
"""

import os
import sys

import streamlit as st

# Pont temporaire : les modules de agent/ utilisent des imports "plats"
# (ex. "from config import ..."), donc le dossier agent/ doit être sur
# sys.path pour être importable depuis la racine. 

RACINE_PROJET = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RACINE_PROJET, "agent"))

from assistant import repondre  # noqa: E402
from config import GROQ_API_KEY, GROQ_MODEL  # noqa: E402


st.set_page_config(page_title="Guide Touristique Burkina Faso", layout="centered")

st.title("Guide Touristique et Culturel Intelligent - Burkina Faso")
st.caption(
    "Assistant basé sur un système RAG (recherche documentaire + LLM). "
    "Posez une question sur les destinations, événements ou formalités de voyage au Burkina Faso."
)

with st.sidebar:
    st.header("À propos")
    st.markdown(
        "Ce projet a été réalisé dans le cadre du cours de Data Science "
        "(Master 1 IFOAD)"
    )
    st.divider()
    st.subheader("État du système")
    if GROQ_API_KEY:
        st.success("Clé API Groq détectée")
    else:
        st.error(
            "Clé API Groq manquante. Définissez GROQ_API_KEY dans votre "
            "environnement (voir .env) avant de poursuivre."
        )
    st.caption(f"Modèle LLM : {GROQ_MODEL}")
    st.divider()
    if st.button("Réinitialiser la conversation"):
        st.session_state.messages = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("Sources consultées"):
                for source in message["sources"]:
                    st.markdown(f"- [{source['nom']}]({source['url']})")

question = st.chat_input("Votre question sur le Burkina Faso...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Recherche dans la base de connaissances..."):
            try:
                resultat = repondre(question)
            except Exception as erreur:
                resultat = {
                    "reponse": (
                        "Une erreur technique empêche de répondre pour le moment. "
                        "Vérifiez que les Phases 1 et 2 ont bien été exécutées "
                        f"(base ChromaDB introuvable ou invalide). Détail : {erreur}"
                    ),
                    "contextes_utilises": [],
                    "hors_perimetre": True,
                }

        st.markdown(resultat["reponse"])

        sources = []
        if not resultat["hors_perimetre"]:
            noms_vus = set()
            for ctx in resultat["contextes_utilises"]:
                nom = ctx["metadata"].get("nom_source", "Source inconnue")
                if nom not in noms_vus:
                    noms_vus.add(nom)
                    sources.append({"nom": nom, "url": ctx["metadata"].get("url", "")})

            if sources:
                with st.expander("Sources consultées"):
                    for source in sources:
                        st.markdown(f"- [{source['nom']}]({source['url']})")

    st.session_state.messages.append({
        "role": "assistant",
        "content": resultat["reponse"],
        "sources": sources,
    })
