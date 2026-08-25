import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="MLOps Accidents - Dashboarding Grafana",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-top: 2rem;}
    .query-box {background-color: #2b2b2b; color: #f8f8f2; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.9em; border-left: 4px solid #e6522c;}
    .alert-badge {display: inline-block; background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; margin-right: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE ---
st.markdown('<p class="main-header">Visualisation & Alerting avec Grafana</p>', unsafe_allow_html=True)

st.markdown("""
Grafana est l'interface de pilotage de notre architecture. Il transforme les métriques brutes de Prometheus en indicateurs actionnables et déclenche des alertes automatiques en cas d'anomalie. Toute la configuration est déployée **"as code"** au démarrage.
""")

st.markdown(
    "<div style='text-align:center; margin: 1rem 0;'>"
    "<a href='http://localhost:3000' target='_blank'>"
    "<button style='background-color:#28a745; color:white; border:none; padding:15px 30px; font-size:1.2rem; border-radius:5px; cursor:pointer;'>"
    "Ouvrir Grafana</button></a>"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()

# --- 1. DASHBOARD "MLOPS - SUIVI MODÈLE" ---
st.markdown('<p class="sub-header">1. Dashboard de Supervision</p>', unsafe_allow_html=True)

st.markdown("""
Nous avons conçu un dashboard centralisé (`mlops-dashboard.json`) répondant à 4 questions critiques pour l'opération du modèle :
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Indicateurs de Santé (SLA)")
    st.markdown("""
    1.  **Taux d'Erreur (`/predict`)** :
        - *Cible :* < 1% (Warning), > 5% (Critique).
        - *Interprétation :* Un pic indique un bug dans le code, un problème de mémoire ou des données d'entrée malformées.
    
    2.  **Latence p95 (Temps de réponse)** :
        - *Métrique :* `histogram_quantile(0.95, ...)`
        - *Interprétation :* 95% des requêtes doivent répondre en moins de X secondes. Une augmentation signale un modèle trop lourd ou une saturation du serveur.
    """)

with col2:
    st.markdown("### 🤖 Indicateurs Métier & Drift")
    st.markdown("""
    3.  **Distribution des Prédictions** :
        - *Visuel :* Camembet (Classe 0 vs Classe 1).
        - *Interprétation :* Une dérive soudaine (ex: 90% de Classe 1) peut indiquer un **Data Drift** (changement de distribution des données entrantes) ou un événement majeur réel.
    
    4.  **Trafic Global (RPS)** :
        - *Métrique :* Requêtes par seconde.
        - *Interprétation :* Permet de dimensionner l'infrastructure et de corréler les erreurs avec les pics de charge.
    """)

st.info("💡 **Configuration as Code :** Le dashboard est provisionné automatiquement via `dashboards.yml` au lancement du container Grafana. Aucune configuration manuelle n'est requise.")

st.divider()

# --- 2. ALERTING & NOTIFICATION ---
st.markdown('<p class="sub-header">2. Système d\'Alerte Automatisé</p>', unsafe_allow_html=True)

st.markdown("""
Pour réagir proactivement, nous avons déployé deux règles d'alerte critiques via l'API de provisioning (`init_grafana_alerts.py`) :
""")

c_alert1, c_alert2 = st.columns(2)

with c_alert1:
    st.markdown("### 🚨 Alerte 1 : Taux d'Erreur Élevé")
    st.markdown("""
    - **Condition :** Taux d'erreur > 5% sur 5 minutes.
    - **Signification :** Le service est instable ou les données sont invalides.
    - **Action :** Notification immédiate à l'équipe de garde.
    """)
    st.code("""
// Extrait logique d'alerte
sum(rate(app_requests_total{status="error"}[5m])) 
/ 
sum(rate(app_requests_total[5m])) > 0.05
    """, language="text")

with c_alert2:
    st.markdown("### 🐢 Alerte 2 : Latence Excessive")
    st.markdown("""
    - **Condition :** Latence p95 > 2 secondes.
    - **Signification :** Le modèle est trop lent pour la production, risque de timeout.
    - **Action :** Investigation sur la performance du modèle ou de l'infrastructure.
    """)
    st.code("""
// Extrait logique d'alerte
histogram_quantile(0.95, rate(model_prediction_latency_seconds_bucket[5m])) > 2.0
    """, language="text")

st.markdown("""
**Canal de Notification :**
Les alertes sont routées vers un **Webhook Discord** configuré dynamiquement via variable d'environnement (`DISCORD_WEBHOOK_URL`). Cela permet une réception instantanée sur mobile ou desktop par l'équipe technique.
""")

st.divider()

# --- 3. ARCHITECTURE DE DÉPLOIEMENT (PROVISIONING) ---
st.markdown('<p class="sub-header">3. Déploiement "As Code"</p>', unsafe_allow_html=True)

st.markdown("""
Contrairement à une configuration manuelle ("click-ops"), notre instance Grafana est entièrement pilotée par le code :
1.  **Datasource :** `datasources.yml` configure automatiquement la connexion à Prometheus.
2.  **Dashboards :** `dashboards.yml` scanne le dossier `/etc/grafana/provisioning/dashboards` et importe le JSON.
3.  **Alertes & Contacts :** Un script Python (`init_grafana_alerts.py`) s'exécute au démarrage (`grafana-init`) pour :
    - Créer le dossier "MLOps_Alerts".
    - Configurer le point de contact Discord (en injectant le secret).
    - Pousser les règles d'alertes via l'API de provisioning.
""")

st.success("""
✅ **Grafana est opérationnel.** 
Il fournit une visibilité temps réel sur la santé du modèle et garantit qu'aucune anomalie critique (erreur, latence) ne passe inaperçue grâce aux notifications Discord automatisées.
""")