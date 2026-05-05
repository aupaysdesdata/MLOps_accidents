import streamlit as st
import requests
import os

API_URL = os.getenv("MODEL_API_URL")

LABEL_MAP = {
    2: "Classe 2",
    3: "Classe 3",
    4: "Classe 4",
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
        place = st.number_input("Place (place)", value=1, step=1)
        catu = st.number_input("Catégorie usager (catu)", value=1, step=1)
        sexe = st.selectbox(
            "Sexe (sexe)",
            options=[1, 2],
            format_func=lambda x: "Masculin" if x == 1 else "Féminin",
        )
        secu1 = st.number_input("Équipement sécurité (secu1)", value=1, step=1)
        year_acc = st.number_input("Année accident (year_acc)", value=2021, step=1)
        victim_age = st.number_input("Âge victime (victim_age)", value=30, step=1)
        nb_victim = st.number_input("Nb victimes (nb_victim)", value=1, step=1)
        nb_vehicules = st.number_input("Nb véhicules (nb_vehicules)", value=1, step=1)

    with col2:
        st.markdown("**Véhicule & route**")
        catv = st.number_input("Catégorie véhicule (catv)", value=7, step=1)
        obsm = st.number_input("Obstacle mobile (obsm)", value=0, step=1)
        motor = st.number_input("Motorisation (motor)", value=1, step=1)
        catr = st.number_input("Catégorie route (catr)", value=3, step=1)
        circ = st.number_input("Régime circulation (circ)", value=2, step=1)
        surf = st.number_input("État surface (surf)", value=1, step=1)
        situ = st.number_input("Situation accident (situ)", value=1, step=1)
        vma = st.number_input("Vitesse max autorisée (vma)", value=50, step=1)

    with col3:
        st.markdown("**Localisation & conditions**")
        jour = st.number_input(
            "Jour (jour)", value=1, step=1, min_value=1, max_value=31
        )
        mois = st.number_input(
            "Mois (mois)", value=1, step=1, min_value=1, max_value=12
        )
        hour = st.number_input(
            "Heure (hour)", value=12, step=1, min_value=0, max_value=23
        )
        lum = st.number_input("Luminosité (lum)", value=1, step=1)
        dep = st.number_input("Département (dep)", value=75, step=1)
        com = st.number_input("Commune (com)", value=1, step=1)
        agg_ = st.selectbox(
            "En agglomération (agg_)",
            options=[1, 2],
            format_func=lambda x: "Hors agglo" if x == 1 else "En agglo",
        )
        int_ = st.number_input("Intersection (int)", value=1, step=1)
        atm = st.number_input("Conditions atm. (atm)", value=1, step=1)
        col_ = st.number_input("Type collision (col)", value=1, step=1)
        lat = st.number_input("Latitude (lat)", value=48.85, format="%.5f")
        long_ = st.number_input("Longitude (long)", value=2.35, format="%.5f")

    submitted = st.form_submit_button("Prédiction", use_container_width=True)

if submitted:
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

    with st.spinner("Envoi au modèle..."):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            result = response.json()

            prediction = (
                result.get("prediction") or result.get("class") or result.get("label")
            )

            st.divider()
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
