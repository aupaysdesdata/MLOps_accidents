import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="BentoML - Serving Industriel",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #FF5A5F; margin-bottom: 1rem;}
    .sub-header {font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-top: 2rem;}
    .value-card {background-color: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #FF5A5F; height: 100%;}
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE : LA PROMESSE DE VALEUR ---
st.markdown('<p class="main-header">BentoML : L\'industrialisation du modèle</p>', unsafe_allow_html=True)
st.markdown("""
Le modèle entraîné sur MLflow ne suffit pas : il doit devenir un **service de production fiable**.
BentoML est le moteur qui encapsule notre modèle pour lui offrir trois capacités critiques : **Valider**, **Évoluer**, et **S'Observer**.
""")

st.divider()

# --- SECTION 1 : LES 3 CAPACITÉS CLÉS (NARRATIVE MÉTIER) ---
st.markdown('<p class="sub-header">1. Les 3 Capacités Critiques pour la Production</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="value-card">', unsafe_allow_html=True)
    st.markdown("### 🛡️ 1. Validation & Robustesse")
    st.markdown("""
    **Problème :** Une API ouverte reçoit n'importe quelle donnée.
    **Solution BentoML + Pydantic :** Un contrat de données strict.
    - Rejet automatique des formats incorrects (Erreur 422).
    - Typage fort des 28 features attendues.
    - *Gain :* L'API ne plante jamais à cause d'une entrée utilisateur.
    """)
    st.code("""
class InputModel(BaseModel):
    victim_age: int
    lat: float
    # ... 28 features typées
    """, language="python")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="value-card">', unsafe_allow_html=True)
    st.markdown("### 🔄 2. Mise à Jour Continue")
    st.markdown("""
    **Problème :** Redémarrer un service pour changer de modèle crée des interruptions.
    **Solution BentoML :** Rechargement à chaud en mémoire.
    - Endpoint `/reload_model` déclenché par **Airflow**.
    - **Mécanisme de Sécurité (Fallback) :** Si le nouveau modèle 'Champion' échoue, on garde l'ancien 'Latest'.
    - *Gain :* Mise à jour limitant les interruptions de service.
    """)
    st.code("""
@bentoml.api(route="/reload_model")
def reload_model(self):
    try:
        self.model = mlflow.load_model("...@champion")
    except Exception:
        # Fallback de sécurité
        self.model = mlflow.load_model("...@latest")
    return {"status": "ok"}
    """, language="python")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="value-card">', unsafe_allow_html=True)
    st.markdown("### 📊 3. Observabilité Native")
    st.markdown("""
    **Problème :** Une API "muette" est impossible à maintenir.
    **Solution BentoML :** Instrumentation automatique pour **Prometheus**.
    - Métriques de trafic, latence et distribution des classes.
    - Endpoint `/metrics` exposé uniquement au réseau interne.
    - *Gain :* Détection immédiate des dérives (Drift) ou ralentissements.
    """)
    st.code("""
# Exemple de métrique exposée
PREDICTIONS_TOTAL.labels(
    class=pred_class
).inc()
    """, language="python")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- SECTION 2 : INTÉGRATION SÉCURISÉE (LIEN AVEC NGINX/AIRFLOW) ---
st.markdown('<p class="sub-header">2. Intégration dans l\Architecture Globale</p>', unsafe_allow_html=True)
st.markdown("""
BentoML n'est pas exposé directement. Il agit comme un moteur interne protégé par les autres briques du projet (**Nginx**, **Airflow**, **Prometheus**).
""")

col_sec, col_diag = st.columns([1, 1])

with col_sec:
    st.markdown("""
    ### Le Principe de "Défense en Profondeur"
    
    Le conteneur BentoML est isolé dans un réseau Docker privé. Ses interfaces sont spécialisées :
    
    1.  **Flux Utilisateur (`/predict`) :** 
        - Accessible uniquement via le Reverse Proxy **Nginx**.
        - La documentation Swagger (`/docs`) est volontairement masquée publiquement.
        
    2.  **Flux MLOps (`/reload_model`) :** 
        - Accessible uniquement par le conteneur **Airflow**.
        - Garantit que seul le pipeline validé peut mettre à jour le modèle.
        
    3.  **Flux Monitoring (`/metrics`) :** 
        - Accessible uniquement par **Prometheus**.
        - Empêche toute interrogation externe des métriques internes.
        
    ✅ **Résultat :** BentoML se concentre sur son métier (prédire), tandis que la sécurité et l'orchestration sont déléguées aux briques spécialisées.
    """)

with col_diag:
    st.markdown("### Vue des Flux Inter-Briques")
    # Diagramme simplifié pour montrer uniquement qui appelle BentoML
    st.graphviz_chart("""
    digraph Flux {
        rankdir=LR;
        node [shape=box, style=filled, fontname="Arial", penwidth=2];
        edge [fontsize=10, color="#555"];
        
        % External
        Nginx [label="🟢 Nginx\\n(Garde-fou)", fillcolor="#009639", fontcolor="white"];
        
        % Internal
        subgraph cluster_bento {
            label="Conteneur BentoML";
            style=dashed;
            color=gray;
            BentoML [label="🟡 API Modèle\\n/predict\\n/reload\\n/metrics", fillcolor="#f1c232"];
        }
        
        % Actors
        Airflow [label="🟠 Airflow\\n(CI/CD)", fillcolor="#e69138"];
        Prometheus [label="🟣 Prometheus\\n(Monitoring)", fillcolor="#9900ff", fontcolor="white"];
        
        % Flows
        Nginx -> BentoML [label="HTTPS\\n/predict"];
        Airflow -> BentoML [label="HTTP\\n/reload_model"];
        Prometheus -> BentoML [label="HTTP\\n/metrics"];
    }
    """)

st.divider()

# --- CONCLUSION NARRATIVE ---
st.success("""
✅ **Synthèse :** 
BentoML transforme notre fichier modèle statique en un **micro-service résilient**.
Grâce à sa capacité de rechargement à chaud et son instrumentation native, il s'intègre parfaitement dans notre boucle MLOps automatisée (Airflow → MLflow → BentoML → Prometheus).
""")