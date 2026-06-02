import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("MODEL_API_URL")

LABEL_MAP = {0: "non-prioritary", 1: "prioritary"}

CATU = {1: "Conducteur", 2: "Passager", 3: "Piéton", 4: "Piéton en rollers / trottinette"}
SECU1 = {
    0: "Sans objet",
    1: "Ceinture",
    2: "Casque",
    3: "Dispositif enfants",
    4: "Gilet de sécurité",
    5: "Airbag",
    6: "Gants",
    7: "Gants + Airbag",
    8: "Non déterminable",
    9: "Autre",
}
CATV = {
    0: "Indéterminé",
    1: "Bicyclette / 2-roues léger",
    2: "Voiture",
    3: "Poids lourd / Utilitaire",
    4: "Véhicule spécial",
    5: "2-3 roues motorisé",
    6: "EDP motorisé",
}
OBSM = {
    0: "Aucun",
    1: "Piéton",
    2: "Véhicule",
    3: "Véhicule sur rail",
    4: "Animal domestique",
    5: "Animal sauvage",
    6: "Autre",
    9: "Autre obstacle",
}
MOTOR = {
    1: "Inconnue",
    2: "Hydrocarbures",
    3: "Hybride électrique",
    4: "Électrique",
    5: "Hydrogène",
    6: "Humaine",
    9: "Autre",
}
CATR = {
    1: "Autoroute",
    2: "Route nationale",
    3: "Route départementale",
    4: "Voie communale",
    5: "Hors réseau public",
    6: "Parc de stationnement",
    7: "Route de métropole urbaine",
    9: "Autre",
}
CIRC = {1: "Sens unique", 2: "Bidirectionnel", 3: "Voies séparées", 4: "Variable"}
SURF = {
    1: "Normale",
    2: "Mouillée",
    3: "Flaques",
    4: "Inondée",
    5: "Enneigée",
    6: "Boue",
    7: "Verglacée",
    8: "Corps gras / huile",
    9: "Autre",
}
SITU = {
    1: "Sur chaussée",
    2: "Bande d'arrêt d'urgence",
    3: "Accotement",
    4: "Trottoir",
    5: "Piste cyclable",
    6: "Voie spéciale",
    8: "Autre",
}
LUM = {
    1: "Plein jour",
    2: "Crépuscule / aube",
    3: "Nuit sans éclairage",
    4: "Nuit — éclairage non allumé",
    5: "Nuit — éclairage allumé",
}
ATM = {0: "Normale", 1: "Conditions risquées"}
COL = {
    1: "Frontale (2 véhicules)",
    2: "Par l'arrière (2 véhicules)",
    3: "Par le côté (2 véhicules)",
    4: "En chaîne (3+ véhicules)",
    5: "Multiples (3+ véhicules)",
    6: "Autre collision",
    7: "Sans collision",
}
INT = {
    1: "Hors intersection",
    2: "Intersection en X",
    3: "Intersection en T",
    4: "Intersection en Y",
    5: "Plus de 4 branches",
    6: "Giratoire",
    7: "Place",
    8: "Passage à niveau",
    9: "Autre",
}

st.set_page_config(page_title="Accident Classifier", layout="wide")

st.title("Classification gravité accident")
st.markdown("Remplis les champs ci-dessous et envoie les données au modèle.")
st.divider()

with st.form("prediction_form"):
    st.subheader("Données de l'accident")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Contexte général**")
        place = st.number_input("Place occupée (place)", value=1, step=1)
        catu = st.selectbox("Catégorie usager (catu)", options=list(CATU), format_func=lambda x: CATU[x])
        sexe = st.selectbox(
            "Sexe (sexe)",
            options=[1, 2],
            format_func=lambda x: "Masculin" if x == 1 else "Féminin",
        )
        secu1 = st.selectbox("Équipement sécurité (secu1)", options=list(SECU1), format_func=lambda x: SECU1[x])
        year_acc = st.number_input("Année accident (year_acc)", value=2021, step=1)
        victim_age = st.number_input("Âge victime (victim_age)", value=30, step=1)
        nb_victim = st.number_input("Nb victimes (nb_victim)", value=1, step=1)
        nb_vehicules = st.number_input("Nb véhicules (nb_vehicules)", value=1, step=1)

    with col2:
        st.markdown("**Véhicule & route**")
        catv = st.selectbox("Catégorie véhicule (catv)", options=list(CATV), format_func=lambda x: CATV[x], index=2)
        obsm = st.selectbox("Obstacle mobile (obsm)", options=list(OBSM), format_func=lambda x: OBSM[x])
        motor = st.selectbox("Motorisation (motor)", options=list(MOTOR), format_func=lambda x: MOTOR[x])
        catr = st.selectbox("Catégorie route (catr)", options=list(CATR), format_func=lambda x: CATR[x], index=2)
        circ = st.selectbox("Régime circulation (circ)", options=list(CIRC), format_func=lambda x: CIRC[x], index=1)
        surf = st.selectbox("État surface (surf)", options=list(SURF), format_func=lambda x: SURF[x])
        situ = st.selectbox("Situation accident (situ)", options=list(SITU), format_func=lambda x: SITU[x])
        vma = st.number_input("Vitesse max autorisée (vma)", value=50, step=10)

    with col3:
        st.markdown("**Localisation & conditions**")
        jour = st.number_input("Jour (jour)", value=1, step=1, min_value=1, max_value=31)
        mois = st.number_input("Mois (mois)", value=1, step=1, min_value=1, max_value=12)
        hour = st.number_input("Heure (hour)", value=12, step=1, min_value=0, max_value=23)
        lum = st.selectbox("Luminosité (lum)", options=list(LUM), format_func=lambda x: LUM[x])
        dep = st.number_input("Département (dep)", value=75, step=1)
        com = st.number_input("Commune (com)", value=1, step=1)
        agg_ = st.selectbox(
            "En agglomération (agg_)",
            options=[1, 2],
            format_func=lambda x: "Hors agglomération" if x == 1 else "En agglomération",
        )
        int_ = st.selectbox("Intersection (int)", options=list(INT), format_func=lambda x: INT[x])
        atm = st.selectbox("Conditions atmosphériques (atm)", options=list(ATM), format_func=lambda x: ATM[x])
        col_ = st.selectbox("Type collision (col)", options=list(COL), format_func=lambda x: COL[x])
        lat = st.number_input("Latitude (lat)", value=48.85, format="%.5f")
        long_ = st.number_input("Longitude (long)", value=2.35, format="%.5f")

    submitted = st.form_submit_button("Prédiction", use_container_width=True)

if submitted:
    st.divider()
    col_result, col_map = st.columns(2)

    with col_map:
        st.subheader("Localisation de l'accident")
        st.map(pd.DataFrame({"lat": [lat], "lon": [long_]}), zoom=10)

    payload = {
        "place": place,
        "catu": catu,
        "sexe": sexe,
        "secu1": secu1,
        "year_acc": year_acc,
        "victim_age": victim_age,
        "catv": catv,
        "obsm": obsm,
        "motor": motor,
        "catr": catr,
        "circ": circ,
        "surf": surf,
        "situ": situ,
        "vma": vma,
        "jour": jour,
        "mois": mois,
        "lum": lum,
        "dep": dep,
        "com": com,
        "agg_": agg_,
        "int": int_,
        "atm": atm,
        "col": col_,
        "lat": lat,
        "long": long_,
        "hour": hour,
        "nb_victim": nb_victim,
        "nb_vehicules": nb_vehicules,
    }

    with col_result:
        with st.spinner("Envoi au modèle..."):
            try:
                response = requests.post(
                    f"{API_URL}/predict",
                    json=payload,
                    timeout=15,
                )
                response.raise_for_status()
                result = response.json()

                prediction = result.get("prediction")
                if isinstance(prediction, list):
                    prediction = prediction[0]

                st.subheader("Résultat")

                if prediction in LABEL_MAP:
                    label = LABEL_MAP[prediction]
                    st.metric(label="Classe prédite", value=label)
                else:
                    st.info(f"Réponse brute du modèle : `{result}`")

            except requests.exceptions.ConnectionError:
                st.error("Impossible de joindre le modèle.")
            except requests.exceptions.Timeout:
                st.error("Timeout")
            except requests.exceptions.HTTPError as e:
                st.error(f"Erreur HTTP {response.status_code} : {e}")
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")
