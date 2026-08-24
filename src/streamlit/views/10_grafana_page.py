import streamlit as st
import json

# Configuration de la page
st.set_page_config(
    page_title="MLOps Accidents - Grafana - Visualisation & Alerting",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem;}
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
Dans ce projet MLOps, Grafana ne se contente pas d'afficher des graphiques : il est **provisionné automatiquement** via une API Python personnalisée, garantissant une configuration reproductible, versionnée et exempte d'erreurs manuelles.
""")

st.divider()

# --- SECTION 1 : L'ARCHITECTURE D'AUTOMATISATION
st.markdown('<p class="sub-header">1. Infrastructure as Code : Provisioning Automatisé</p>', unsafe_allow_html=True)

st.markdown("""
Contrairement à une configuration manuelle via l'interface, notre stack utilise une approche **Infrastructure as Code (IaC)** avancée.
Un script Python dédié (`init_grafana_alerts.py`) s'exécute au démarrage du conteneur pour configurer Grafana automatiquement.
""")

col_arch1, col_arch2 = st.columns([1, 1])

with col_arch1:
    st.markdown("### Le Script d'Initialisation Python")
    st.markdown("""
    Ce script, lancé via Docker Compose, effectue les opérations suivantes dans l'ordre :
    1.  **Attente intelligente** : Il poll l'API de santé de Grafana jusqu'à ce qu'elle soit prête (`healthcheck`).
    2.  **Authentification sécurisée** : Utilisation des identifiants injectés via variables d'environnement.
    3.  **Création du contexte** : Création du dossier `MLOps_Alerts` si inexistant.
    4.  **Gestion des doublons** : Vérification idempotente des Contact Points pour éviter les notifications en spam.
    5.  **Déploiement des règles** : Injection des fichiers JSON de définition des alertes.
    
    **Avantages MLOps :**
    *   ✅ **Reproductibilité** : Un `docker-compose up` suffit pour recréer tout le monitoring.
    *   ✅ **Versioning** : La configuration des alertes est dans des fichiers JSON suivis par Git.
    *   ✅ **Sécurité** : Aucun mot de passe en dur dans le code (utilisation de `.env`).
    """)

with col_arch2:
    st.markdown("### Extrait du Script Python (`init_grafana_alerts.py`)")
    st.code("""
def configure_contact_point(session):
    # 1. Chargement de la config depuis un fichier JSON externe
    config = load_json_config("/config/contact-points.json")
    
    # 2. Vérification d'existence pour éviter les doublons (Idempotence)
    existing = session.get("/api/v1/provisioning/contact-points").json()
    if any(c['name'] == config['name'] for c in existing):
        return True # Déjà configuré
        
    # 3. Création via l'API de provisioning
    response = session.post("/api/v1/provisioning/contact-points", json=config)
    return response.status_code in [200, 201]
    """, language="python")
    
    st.markdown("### Intégration Docker Compose")
    st.code("""
services:
  grafana-init:
    build:
      context: .
      dockerfile: Dockerfile.grafana-init
    depends_on:
      grafana:
        condition: service_healthy # Attend que Grafana soit prêt
    command: python /app/init_grafana_alerts.py
    """, language="yaml")

st.divider()

# --- SECTION 2 : LE DASHBOARD LIVE ---
st.markdown('<p class="sub-header">2. Dashboard de Suivi en Temps Réel</p>', unsafe_allow_html=True)

col_live, col_info = st.columns([1, 1])

with col_live:
    st.markdown("""
    ### Accéder au Dashboard Live
    
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

# --- SECTION 3 : LES ALERTES CONFIGURÉES ---
st.markdown('<p class="sub-header">3. Système d\'Alerting Automatisé</p>', unsafe_allow_html=True)
st.markdown("""
Nous ne surveillons pas les graphiques en permanence. Grafana le fait pour nous 24/7 et nous notifie sur **Discord** en cas d'anomalie.
Les règles d'alerte ne sont pas cliquées dans l'interface, mais définies dans des fichiers JSON structurés (`alert-error-rate.json`, `alert-latency.json`).
Cela permet de définir précisément la logique de requête, de réduction et de seuil.
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

# --- SECTION 4 : CANAL DE NOTIFICATION (DISCORD) ---
st.markdown('<p class="sub-header">4. Canal de Notification : Discord</p>', unsafe_allow_html=True)

col_discord1, col_discord2 = st.columns([1, 1])

with col_discord1:
    st.markdown("""
    ### Intégration Discord via Webhook
    
    Les alertes sont routées vers un serveur Discord dédié grâce à un **Contact Point** configuré dynamiquement.
    
    **Flux de notification complet :**
    1.  **Détection** : Prometheus scrape les métriques de l'API BentoML.
    2.  **Évaluation** : Grafana évalue les règles JSON toutes les minutes.
    3.  **Confirmation** : Si le seuil est dépassé pendant 5 min (`for: 5m`), l'état passe à `Firing`.
    4.  **Routage** : La Notification Policy lit le label `severity` et cible le contact `Discord-MLOps`.
    5.  **Action** : Un webhook HTTPS est envoyé à Discord avec un message formaté.
    
    **Contenu du message Discord :**
    - 🚨 Nom de l'alerte et sévérité.
    - 📊 Valeur actuelle vs Seuil.
    - 🔗 Lien direct vers le panel Grafana pour investigation immédiate.
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