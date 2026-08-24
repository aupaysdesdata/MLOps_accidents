import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="MLOps Accidents - Prometheus - Collecte & Métriques",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-top: 2rem;}
    .metric-card {background-color: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #E6522C; height: 100%;}
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE : LE RÔLE STRATÉGIQUE ---
st.markdown('<p class="main-header">Prometheus : Le système nerveux de l\'achitecture</p>', unsafe_allow_html=True)
st.markdown("""
Dans une architecture MLOps, les logs textuels ne suffisent pas : ils sont réactifs, pas proactifs.
**Prometheus** agit comme notre cerveau analytique : il interroge nos services toutes les **15 secondes**, transforme les événements bruts en **séries temporelles** et permet de détecter les anomalies avant qu'elles n'impactent les utilisateurs.
""")

st.divider()

# --- SECTION 1 : LE MÉCANISME DE COLLECTE (SIMPLIFIÉ) ---
st.markdown('<p class="sub-header">1. Collecte : Le Modèle "Pull"</p>', unsafe_allow_html=True)

col_meca, col_code = st.columns([1, 1])

with col_meca:
    st.markdown("""
    Contrairement aux agents qui "poussent" des données, Prometheus vient les **chercher** (Pull).
    
    **Notre Configuration :**
    - **Fréquence :** Scrapping toutes les **15 secondes**.
    - **Cibles :** 
      1. **BentoML (`ml-api:3000`)** : Pour les métriques métier et perf.
      2. **Lui-même** : Pour l'auto-surveillance.
    
    **Avantage Critique :** Si un service tombe, Prometheus ne reçoit plus de données. Cette **absence de signal** déclenche immédiatement une alerte "Down", contrairement à un agent qui pourrait continuer d'envoyer des logs d'erreur sans fin.
    """)

with col_code:
    st.markdown("**Extrait de configuration (`prometheus.yml`)**")
    st.code("""
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "bentoml-api"
    static_configs:
      - targets: ["ml-api:3000"]
    """, language="yaml")

st.divider()

# --- SECTION 2 : LES DEUX FAMILLES DE MÉTRIQUES (CŒUR DU SUJET) ---
st.markdown('<p class="sub-header">2. Deux Dimensions de Surveillance</p>', unsafe_allow_html=True)
st.markdown("""
Nous n'avons pas instrumenté le code au hasard. Chaque métrique répond à une question précise, divisée en deux catégories :
""")

tab_sre, tab_mlops = st.tabs(["🏥 Santé Infrastructure (SRE)", "🧠 Santé du Modèle (MLOps)"])

with tab_sre:
    st.markdown("""
    ### Objectif : "L'API est-elle disponible et rapide ?"
    Ces métriques sont critiques pour les équipes Ops.
    
    | Métrique | Type | Usage & KPI |
    | :--- | :--- | :--- |
    | **`app_requests_total`** | Counter | Mesure le trafic et le **taux d'erreur**. <br>🚨 *Alerte si erreur > 5%.* |
    | **`app_request_latency`** | Histogram | Mesure le temps de réponse global (Réseau + Code). <br>🚨 *Alerte si p95 > 1s.* |
    
    💡 **Pourquoi ?** Une latence qui explose signale souvent un problème d'infrastructure (CPU, mémoire) avant même que le modèle ne rate une prédiction.
    """)

with tab_mlops:
    st.markdown("""
    ### Objectif : "Le modèle dérive-t-il ?"
    Ces métriques sont spécifiques au Data Science et distinguent notre projet d'un site web classique.
    
    | Métrique | Type | Usage & KPI |
    | :--- | :--- | :--- |
    | **`model_predictions_total`** | Counter (Label: `class`) | Compte les prédictions par classe (0 ou 1). <br>🚨 *Alerte si la distribution change brusquement (Data Drift).* |
    | **`model_prediction_latency`** | Histogram | Temps d'exécution **pur** du modèle (sans réseau). <br>🚨 *Surveille la complexité algorithmique.* |
    
    💡 **Pourquoi ?** Si le modèle se met à prédire "Prioritaire" 80% du temps (contre 30% d'habitude) sans raison, c'est un signe de **Concept Drift**. Prometheus le détecte en temps réel.
    """)

st.divider()

# --- SECTION 3 : DU BRUT À L'INDICATEUR (PROMQL) ---
st.markdown('<p class="sub-header">3. La Valeur Ajoutée : Le Langage PromQL</p>', unsafe_allow_html=True)
st.markdown("""
Prometheus stocke des données brutes. C'est le langage **PromQL** qui les transforme en **KPI actionnables** pour Grafana.
Voici les deux requêtes clés qui alimentent nos dashboards :
""")

col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown("**📉 KPI 1 : Taux d'Erreur (En %)**")
    st.code("""
# Ratio des erreurs sur les 5 dernières minutes
(
  sum(rate(app_requests_total{status="error"}[5m]))
  /
  sum(rate(app_requests_total[5m]))
) * 100
    """, language="promql")
    st.caption("Traduit des milliers de logs en un seul pourcentage lisible.")

with col_q2:
    st.markdown("**🧠 KPI 2 : Ratio de Dérive (Classe 1)**")
    st.code("""
# % de prédictions 'Prioritaires' sur la dernière heure
sum(rate(model_predictions_total{class="1"}[1h]))
/
sum(rate(model_predictions_total[1h]))
    """, language="promql")
    st.caption("Permet de visualiser l'évolution de la gravité des accidents en temps réel.")

st.divider()

# --- SECTION 4 : FLUX DE DONNÉES VERS GRAFANA ---
st.markdown('<p class="sub-header">4. Intégration dans la Chaîne de Monitoring</p>', unsafe_allow_html=True)

col_flux, col_explication = st.columns([1, 1])

with col_flux:
    st.graphviz_chart("""
    digraph Flux {
        rankdir=LR;
        node [shape=box, style=filled, fontname="Arial", penwidth=2];
        edge [fontsize=10];
        
        BentoML [label="🟡 BentoML\\n(Source)", fillcolor="#f1c232"];
        Prometheus [label="🟣 Prometheus\\n(Stockage & Calcul)", fillcolor="#E6522C", fontcolor="white"];
        Grafana [label="📊 Grafana\\n(Visualisation)", fillcolor="#F46800", fontcolor="white"];
        AlertMgr [label="🔔 AlertManager\\n(Notification)", fillcolor="#6a5acd", fontcolor="white"];
        
        BentoML -> Prometheus [label="Scrape /metrics\\n(15s)"];
        Prometheus -> Grafana [label="Requêtes PromQL"];
        Prometheus -> AlertMgr [label="Règles d'alerte"];
    }
    """)

with col_explication:
    st.markdown("""
    ### Le Rôle de Chaque Brique
    
    1.  **BentoML** expose les métriques brutes (compteurs, histogrammes).
    2.  **Prometheus** les stocke et permet de les **agréger** (moyenne, taux, percentiles) via PromQL.
    3.  **Grafana** (page suivante) interroge Prometheus pour afficher des graphiques lisibles.
    4.  **AlertManager** surveille les seuils critiques et notifie l'équipe sur Discord.
    
    ✅ **Résultat :** Nous ne surveillons pas seulement *si* le service tourne, mais *comment* il se comporte et *quelle qualité* de prédiction il délivre.
    """)

st.success("""
✅ **Synthèse :** 
Prometheus transforme notre API "muette" en un système intelligent. 
Grâce à l'instrumentation fine (labels, histograms), nous détectons les problèmes d'infrastructure **et** les dérives de modèle en temps réel.
""")