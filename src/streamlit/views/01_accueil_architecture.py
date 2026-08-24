import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="MLOps Accidents",
    layout="wide",
    initial_sidebar_state="collapsed" # On commence en plein écran pour l'impact
)

# --- STYLE ---
st.markdown("""
    <style>
    .main-header {font-size: 3rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem; text-align: center;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-top: 2rem;}
    .arch-box {background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #e9ecef; height: 100%;}
    .nav-button {display: block; width: 100%; padding: 1rem; margin: 0.5rem 0; background-color: #1f77b4; color: white; text-align: center; text-decoration: none; border-radius: 8px; font-weight: bold; transition: background 0.3s;}
    .nav-button:hover {background-color: #155a8a; color: white;}
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE : MISSION & CONTEXTE ---
st.markdown('<p class="main-header">🇫🇷 Prédiction de gravité des accidents</p>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-size: 1.2rem; color: #555; margin-bottom: 2rem;">
    Déploiement d'une infrastructure MLOps complète pour l'aide à la décision en temps réel.
</div>
""", unsafe_allow_html=True)

st.divider()

# --- SECTION 1 : L'ARCHITECTURE GLOBALE (LE CŒUR) ---
st.markdown('<p class="sub-header">1. Architecture du Pipeline MLOps</p>', unsafe_allow_html=True)
st.markdown("""
Notre solution ne se limite pas à un modèle : c'est un **système autonome** qui ingère, entraîne, déploie et surveille en continu.
Voici le flux de données complet, de l'orchestration à l'utilisateur final :
""")

# Affichage du diagramme Mermaid (ou une image statique si tu l'as exportée)
# Ici, on utilise le code Mermaid directement si Streamlit le supporte, sinon on décrit
st.graphviz_chart("""
digraph Architecture {
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", penwidth=2, color="#333"];
    edge [fontsize=10, color="#555"];
    
    % Styles
    Airflow [label="🟠 Airflow\\n(Orchestrateur)", fillcolor="#e69138"];
    MLflow [label="🟡 MLflow\\n(Registry & Tracking)", fillcolor="#f1c232"];
    BentoML [label="🟡 BentoML\\n(API de Prédiction)", fillcolor="#f1c232"];
    Nginx [label="🟢 Nginx\\n(Sécurité & Proxy)", fillcolor="#009639", fontcolor="white"];
    Streamlit [label="🔵 Streamlit\\n(Interface Utilisateur)", fillcolor="#2986cc", fontcolor="white"];
    Prometheus [label="🟣 Prometheus\\n(Monitoring)", fillcolor="#9900ff", fontcolor="white"];
    Grafana [label="🟣 Grafana\\n(Dashboards)", fillcolor="#F46800", fontcolor="white"];
    Data [label="🗄️ Data Gouv\\n(Source BAAC)", fillcolor="#dddddd", shape="cylinder"];
    
    % Flux
    Data -> Airflow [label="1. Ingestion"];
    Airflow -> MLflow [label="2. Train & Register"];
    Airflow -> BentoML [label="5. Reload (Hot-Swap)"];
    MLflow -> BentoML [label="3. Load Champion"];
    Nginx -> Streamlit [label="4. UI Access"];
    Nginx -> BentoML [label="4. Predict API"];
    BentoML -> Prometheus [label="6. Métriques"];
    Prometheus -> Grafana [label="7. Visualisation"];
    
    { rank=same; Streamlit; BentoML; }
    { rank=same; Prometheus; Grafana; }
}
""")

st.info("""
**Les 5 étapes clés du cycle de vie :**
1.  **Orchestration (Airflow) :** Planifie l'ingestion et l'entraînement.
2.  **Tracking (MLflow) :** Enregistre les modèles et les métriques de performance.
3.  **Serving (BentoML) :** Expose le modèle "Champion" via une API sécurisée.
4.  **Accès (Nginx + Streamlit) :** Fournit une interface utilisateur HTTPS protégée.
5.  **Monitoring (Prometheus + Grafana) :** Surveille la santé du service et la dérive du modèle.
""")

st.divider()

# --- PIED DE PAGE : ACCÈS RAPIDE ---
st.markdown("""
<div style="text-align: center; margin-top: 2rem;">
    <p><strong>Accédez directement à l'application de prédiction ?</strong>  :</p>
    <a href="https://localhost" target="_blank" style="text-decoration:none;">
        <button style="background-color:#28a745; color:white; border:none; padding:15px 30px; font-size:1.2rem; border-radius:5px; cursor:pointer;">
        🚀 Lancer l'Application Streamlit
        </button>
    </a>
</div>
""", unsafe_allow_html=True)