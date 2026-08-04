import streamlit as st
import json

# Configuration de la page
st.set_page_config(
    page_title="Grafana - Visualisation & Alerting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #F46800; margin-bottom: 1rem;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-top: 2rem;}
    .alert-box {background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 1rem; margin: 1rem 0; border-radius: 4px;}
    .code-block {background-color: #282c34; color: #abb2bf; padding: 0.8rem; border-radius: 6px; font-size: 0.85rem;}
    .live-link {background-color: #e8f4fd; border: 2px solid #1f77b4; padding: 1.5rem; border-radius: 10px; text-align: center; margin: 2rem 0;}
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE ---
st.markdown('<p class="main-header">Grafana : De la donnée à la décision</p>', unsafe_allow_html=True)
st.markdown("""
Si Prometheus est le système nerveux qui collecte les signaux, **Grafana** est le cerveau qui les interprète.
Il transforme les séries temporelles brutes en **tableaux de bord lisibles** et déclenche des **alertes automatiques** vers notre canal Discord lorsque des seuils critiques sont dépassés.
""")

st.divider()

# --- SECTION 1 : LE DASHBOARD LIVE ---
st.markdown('<p class="sub-header">1. Dashboard de Suivi en Temps Réel</p>', unsafe_allow_html=True)

col_live, col_info = st.columns([1, 1])

with col_live:
    st.markdown("""
    ### 🎯 Accéder au Dashboard Live
    
    Pour la démonstration, nous pouvons accéder directement à l'interface Grafana connectée à notre Prometheus.
    
    **Indicateurs clés suivis :**
    - **Taux d'Erreur (%)** : Santé immédiate de l'API.
    - **Latence p95** : Performance perçue par l'utilisateur.
    - **Trafic (RPS)** : Charge actuelle sur le modèle.
    - **Distribution des Prédictions** : Détection visuelle de la dérive (Drift).
    """)
    
    # Lien direct vers Grafana (adapte le port si nécessaire)
    st.markdown("""
    <div class="live-link">
    <h3>🚀 Ouvrir Grafana en Live</h3>
    <p>Cliquez ci-dessous pour voir les métriques en temps réel :</p>
    <a href="http://localhost:3000/d/adf4qm5" target="_blank" style="text-decoration:none;">
    <button style="background-color:#F46800; color:white; border:none; padding:15px 30px; font-size:1.2rem; border-radius:5px; cursor:pointer;">
    Ouvrir le Dashboard MLOps
    </button>
    </a>
    <p style="font-size:0.9rem; margin-top:10px; color:#555;">(Identifiants : admin / admin)</p>
    </div>
    """, unsafe_allow_html=True)

with col_info:
    st.markdown("""
    ### Architecture du Dashboard
    
    Notre dashboard `MLOps - Suivi Modèle` est structuré pour répondre à deux besoins :
    
    1.  **Vision Opérationnelle (SRE)** :
        *   Est-ce que ça marche ? (Taux d'erreur)
        *   Est-ce que c'est lent ? (Latence)
        *   Est-ce que c'est utilisé ? (Trafic)
        
    2.  **Vision Data Science (MLOps)** :
        *   Que prédit le modèle ? (Pie Chart des classes)
        *   Le volume de prédiction est-il cohérent ? (Cumul sur 24h)
        
    *Les données sont rafraîchies automatiquement toutes les 5 secondes.*
    """)
    
    # Optionnel : Si tu as une capture d'écran propre, tu peux la mettre ici en attendant de cliquer
    # st.image("assets/capture_grafana_dashboard.png", caption="Aperçu du dashboard")

st.divider()

# --- SECTION 2 : LES ALERTES CONFIGURÉES ---
st.markdown('<p class="sub-header">2. Système d\'Alerting Automatisé</p>', unsafe_allow_html=True)
st.markdown("""
Nous ne surveillons pas les graphiques en permanence. Grafana le fait pour nous 24/7 et nous notifie sur **Discord** en cas d'anomalie.
""")

tab_alert1, tab_alert2 = st.tabs(["🚨 Alerte Taux d'Erreur", "🐢 Alerte Latence (Performance)"])

with tab_alert1:
    st.markdown("### Alerte : Taux d'Erreur Critique")
    st.markdown("**Objectif :** Détecter immédiatement si l'API plante ou renvoie des erreurs massives.")
    
    st.code("""
# Requêtes PromQL de l'alerte
(sum(rate(app_requests_total{endpoint="/predict", status="error"}[5m])) 
/ 
sum(rate(app_requests_total{endpoint="/predict"}[5m]))) * 100
    """, language="promql")
    
    st.info("""
    **Configuration :**
    - **Seuil :** `> 5%`
    - **Durée (Pending) :** `5 minutes` (Évite les faux positifs dus à un pic bref).
    - **Gestion "No Data" :** Considéré comme `OK` (Pas d'erreur = bonne nouvelle).
    - **Action :** Notification configuré avec un **Webhook Discord** avec le lien vers le panel concerné.
    """)

with tab_alert2:
    st.markdown("### Alerte : Dérive de Performance (Latence)")
    st.markdown("**Objectif :** Détecter un ralentissement anormal du modèle (saturation CPU, fuite mémoire).")
    
    st.code("""
# Calcul du 95ème percentile de latence sur 5 minutes
histogram_quantile(0.95, rate(model_prediction_latency_seconds_bucket[5m]))
    """, language="promql")
    
    st.warning("""
    **Configuration :**
    - **Seuil :** `> 1.0 seconde`
    - **Durée (Pending) :** `5 minutes`.
    - **Interprétation :** Si 95% des requêtes prennent plus d'1 seconde, le modèle est trop lent pour une production réactive.
    - **Action :** Notification Discord "Alerte MLOps : Dérive de Performance".
    """)

st.divider()

# --- SECTION 3 : CANAL DE NOTIFICATION (DISCORD) ---
st.markdown('<p class="sub-header">3. Canal de Notification : Discord</p>', unsafe_allow_html=True)

col_discord1, col_discord2 = st.columns([1, 1])

with col_discord1:
    st.markdown("""
    ### Intégration Discord
    
    Les alertes ne servent à rien si personne ne les voit. Nous avons configuré un **Contact Point** Grafana vers un serveur Discord dédié.
    
    **Flux de notification :**
    1.  Prometheus détecte le dépassement de seuil.
    2.  Grafana évalue la règle pendant 5 minutes.
    3.  Si l'alerte persiste (état `Firing`), Grafana envoie un webhook à Discord.
    4.  L'équipe reçoit un message formaté avec :
        - Le nom de l'alerte.
        - La valeur actuelle.
        - Un lien direct vers le dashboard pour investiguer.
    """)

with col_discord2:
    # Ici, tu peux mettre ta capture d'écran Discord
    st.markdown("### Exemple de notification reçue")
    st.info("📸 *Insère ici ta capture d'écran du message Discord reçu lors de tes tests.*")
    # st.image("assets/capture_discord_alert.png", caption="Exemple d'alerte reçue sur Discord")
    
    st.success("✅ **Avantage :** Centralisation des alertes techniques dans un outil de communication d'équipe quotidien.")

st.divider()

# --- CONCLUSION ---
st.markdown('<p class="sub-header">Synthèse du Monitoring</p>', unsafe_allow_html=True)
st.success("""
**Grafana clôture la boucle MLOps :**
1.  **Visibilité :** Tout l'état du système est visible en un coup d'œil (Dashboard Live).
2.  **Réactivité :** Les problèmes sont détectés et notifiés automatiquement avant l'impact utilisateur (Alertes Discord).
3.  **Fiabilité :** La configuration des seuils et la gestion du "No Data" assurent que seules les vraies anomalies sont signalées.

👉 **Pour la suite de la soutenance :** Nous allons maintenant voir comment l'utilisateur final interagit avec ce système robuste via l'application de prédiction.
""")