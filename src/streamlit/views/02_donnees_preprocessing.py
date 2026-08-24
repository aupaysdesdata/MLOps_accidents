import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="MLOps Accidents - Données & Préprocessing",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-top: 2rem;}
    .highlight-box {background-color: #e8f4fd; border-left: 5px solid #1f77b4; padding: 1rem; border-radius: 4px; margin: 1rem 0;}
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE : VISION GLOBALE (Fusion Objectif + Défi) ---
st.markdown('<p class="main-header">Prédiction de gravité des accidents</p>', unsafe_allow_html=True)
st.markdown("""
**Mission :** Déployer une infrastructure MLOps capable de prédire en temps réel si un accident nécessite une intervention **prioritaire**, afin d'optimiser l'envoi des secours.  
**Enjeu :** Chaque minute compte. Nous automatisons le triage des accidents en exploitant les données déclarées par les forces de l'ordre (Fichier BAAC).
""")

st.divider()

# --- COLONNES : CONTEXTE & SOURCES ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<p class="sub-header">1. Stratégie de Classification</p>', unsafe_allow_html=True)
    st.info("""
    La prédiction détermine la priorité selon le cas le plus grave des personnes impliquées dans l'accident :
    - 🔴 **Classe 1 (Prioritaire)** : **Au moins un** Tué **ou** Hospitalisé.
    - 🟢 **Classe 0 (Non-Prioritaire)** : **Uniquement** Indemnes **et / ou** Blessés légers.
    
    *Pas ou peu d'accidents avec seulement des personnes indemnes, car le jeu de données est biaisé vers les cas graves.*
    Cela signifie que les accidents avec 100% de personnes indemnes ne sont pas complétées entièrement par les forces de l'ordre et sont soit absents du fichier BAAc, soit supprimés par le preprocessing
    """)
    
    st.markdown('<p class="sub-header">2. Source & Qualité</p>', unsafe_allow_html=True)
    st.markdown("""
    - **Source :** Bases de Données Annuelles des Accidents Corporels de la Circulation Routière ([Fichier BAAC - data.gouv.fr - ONISR](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024)).
    - **Période :** 2021-2024 (Uniformité des formats).
    - **Volume Brut :** ~506k usagers, ~220k accidents.
    - **Nettoyage Critique** :
        - Suppression des doublons (fichier 2022) 
        - Suppression cibles inconnues (`grav = -1`)
        - Supression données critiques manquantes (ex : `lat`, `long`) --> Accidents avec 100% indemnes fortement concernés 
    """)

with col2:
    st.markdown('<p class="sub-header">3. Structure des données brutes</p>', unsafe_allow_html=True)
    st.markdown("4 fichiers CSV interconnectés par `Num_Acc` (ID Accident) et `id_vehicule` :")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Caract.", "Lieux", "Véhicules", "Usagers"])
    
    with tab1:
        st.write("**Circonstances**")
        st.write("- Date, Heure, Météo, Lumière")
        st.write("- Département, Commune")
    with tab2:
        st.write("**Géographie**")
        st.write("- Type de route, Profil")
        st.write("- Surface, Intersection")
    with tab3:
        st.write("**Matériel**")
        st.write("- Catégorie véhicule (`catv`)")
        st.write("- Motorisation, Obstacle")
    with tab4:
        st.write("**Victimes**")
        st.write("- Âge, Sexe, Gravité (`grav`)")
        st.write("- Catégorie (Piéton/Conducteur)")

st.divider()

# --- SECTION PREPROCESSING ---
st.markdown('<p class="sub-header">4. Pipeline de Data Engineering (`preprocess.py`)</p>', unsafe_allow_html=True)
st.markdown("Transformation de la donnée brute en dataset ML via 4 étapes clés :")

with st.expander("🔍 Détails techniques du pipeline", expanded=True):
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Étape 1 : Fusion**")
        st.code("""
# 1. Détection auto du délimiteur (';' vs ',')
# 2. Jointure 1:1 (Caract + Lieux) sur 'Num_Acc'
# 3. Jointure 1:N (Véhicules + Usagers) sur 'Num_Acc' + 'id_vehicule'
# 4. Nettoyage IDs : Suppression espaces invisibles
        """, language="python")
        
        st.markdown("**Étape 2 : Feature Engineering**")
        st.code("""
# Temporel : Extraction année/heure
# Agrégation : 'nb_victim', 'nb_vehicules' (par accident)
# Encodage : Regroupement véhicules (38 -> 6 classes)
# Calcul : Âge victime (avec filtre outliers <0 ou >120)
# Variable cible : `replace([1, 2, 3, 4], [0, 0, 1, 1])` pour avoir indemne (0), blessé léger (0), blessé hospitalisé (1), tué (1)
       """, language="python")

    with c2:
        st.markdown("**Étape 3 : Gestion des Doublons**")
        st.warning("""
        **Problème :** 221k lignes pour 165k accidents uniques (Fichier 2022).
        **Solution :** Tri décroissant sur `grav` puis `drop_duplicates`.
        *Note : Le tri est numérique (4 > 2), la sécurité vient du recodage large suivant.*
        """)

        st.markdown("**Étape 4 : Recodage Sémantique**")
        st.code("""
# Conversion Corse : '2A'/'2B' -> '201'/'202'
# Cible Binaire :
#   1 (Indemne) et (Blessé léger) -> 0 (Non Prioritaire)
#   2, 3, 4 (Toute blessure) -> 1
# Drop : Colonnes ID, adresses, NaN critiques
        """, language="python")

st.divider()

# --- STATISTIQUES & EDA ---
st.markdown('<p class="sub-header">5. Résultats de l\'EDA & Dataset Final</p>', unsafe_allow_html=True)

# Métriques
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric(label="Accidents Uniques", value="~165,000", delta="Après nettoyage")
with col_stat2:
    st.metric(label="Features", value="28", delta="Sélectionnées")
with col_stat3:
    st.metric(label="Période", value="2021-2024")
with col_stat4:
    st.metric(label="Cible : Prioritaire", value="~57%", delta="Classe 1 (Large)")

# Graphiques
st.markdown("**Visualisations clés ayant guidé l'architecture :**")
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.markdown("**📊 Distribution de la Cible (Brute)**")
    st.caption("Déséquilibre initial justifiant le recodage large.")
    try:
        st.image("references/figures/output_nb_users_par_gravite.png", use_container_width=True)
    except:
        st.error("Image manquante : `references/figures/output_nb_users_par_gravite.png`")

with col_graph2:
    st.markdown("**🔥 Matrice de Corrélation**")
    st.caption("Validation de l'absence de multicolinéarité forte.")
    try:
        st.image("assets/correlation_matrix.png", use_container_width=True)
    except:
        st.error("Image manquante : `assets/correlation_matrix.png`")

st.success("""
✅ **Synthèse :** Le dataset est prêt. La stratégie de recodage large (57% de classe 1) 
garantit que **tout accident avec blessure** sera traité comme prioritaire par le modèle, 
éliminant virtuellement le risque de faux négatif critique.
""")