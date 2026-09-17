# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# Utilitaires partagés entre toutes les pages
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# PALETTE VISUELLE — TERRE / ESPACE
# ============================================================

BLEU_FONCE = "#0D3B66"
BLEU = "#1976D2"
BLEU_VIF = "#2D9CDB"
BLEU_CLAIR = "#DCEEFF"
BLEU_TRES_CLAIR = "#EEF7FF"
TERRE = "#16A085"
TERRE_FONCE = "#0E6F61"
GRIS = "#B8C4D1"
GRIS_FONCE = "#6B7280"
GRILLE = "#E8EDF3"

RAYON_TERRE_KM = 6371


# ============================================================
# CONSTANTES DU PROJET
# ============================================================

RAYON_MIN = 0.5
RAYON_MAX = 1.6

RAYON_MIN_KM = (
    RAYON_MIN
    * RAYON_TERRE_KM
)

RAYON_MAX_KM = (
    RAYON_MAX
    * RAYON_TERRE_KM
)

INSOLATION_MIN = 0.5
INSOLATION_MAX = 2.0

ANNEE_DEBUT = 1992


# ============================================================
# CHEMIN DU DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "exoplanets.csv"


# ============================================================
# STYLE GLOBAL
# ============================================================

def inject_style():

    st.markdown(
        f"""
        <style>

        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }}

        [data-testid="stMetric"] {{
            background-color: #FAFCFF;
            border: 1px solid #DFE8F2;
            border-radius: 12px;
            padding: 14px 18px;

            height: 135px;
            min-height: 135px;

            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        [data-testid="stMetricLabel"] {{
            font-size: 0.95rem;

            /* Même espace réservé au titre sur toutes les cartes */
            min-height: 3.2rem;

            display: flex;
            align-items: flex-start;
        }}

        [data-testid="stMetricLabel"] p {{
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            line-height: 1.25 !important;
        }}

        [data-testid="stMetricValue"] {{
            font-size: 2rem;
            font-weight: 700;
        }}

        /* Navigation : page active foncée, autres pages claires */
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background-color: {BLEU_FONCE} !important;
            border-color: {BLEU_FONCE} !important;
            color: white !important;
            font-weight: 700 !important;
        }}

        button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover {{
            background-color: #082C4D !important;
            border-color: #082C4D !important;
        }}

        button[kind="secondary"],
        button[data-testid="stBaseButton-secondary"] {{
            background-color: {BLEU_TRES_CLAIR} !important;
            border-color: #B9D7F2 !important;
            color: {BLEU_FONCE} !important;
            font-weight: 650 !important;
        }}

        button[kind="secondary"]:hover,
        button[data-testid="stBaseButton-secondary"]:hover {{
            background-color: {BLEU_CLAIR} !important;
            border-color: {BLEU} !important;
        }}


    /* Sidebar plus compacte */

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.55rem;
        }}

        [data-testid="stSidebar"] hr {{
            margin-top: 0.6rem;
            margin-bottom: 0.6rem;
        }}

        [data-testid="stSidebar"] h3 {{
            margin-top: 0.5rem;
            margin-bottom: 0.25rem;
        }}

    /* Labels des KPI : autoriser le retour à la ligne */
    [data-testid="stMetricLabel"] {{
        white-space: normal !important;
        overflow: visible !important;
    }}

    [data-testid="stMetricLabel"] p {{
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        line-height: 1.25 !important;
    }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# NAVIGATION
# La navigation native est désactivée dans
# .streamlit/config.toml (showSidebarNavigation = false) :
# la page bonus reste ainsi accessible uniquement
# depuis la fin de la page Candidates.
# ============================================================

PAGES_NAV = [
    (
        "Synthèse",
        "app.py"
    ),
    (
        "1 · Découvertes",
        "pages/1_Découvertes.py"
    ),
    (
        "2 · Diversité",
        "pages/2_Diversité.py"
    ),
    (
        "3 · Conditions favorables",
        "pages/3_Conditions_favorables.py"
    ),
    (
        "4 · Candidates",
        "pages/4_Candidates.py"
    )
]


def nav(page_active):

    colonnes = st.columns(
        len(PAGES_NAV)
    )

    for (libelle, chemin), colonne in zip(
        PAGES_NAV,
        colonnes
    ):

        with colonne:

            actif = (
                chemin
                == page_active
            )

            if st.button(
                libelle,
                key=f"nav_{chemin}",
                type=(
                    "primary"
                    if actif
                    else "secondary"
                ),
                use_container_width=True
            ):

                if not actif:

                    st.switch_page(
                        chemin
                    )


# ============================================================
# CHARGEMENT ET PRÉPARATION DES DONNÉES
# ============================================================

@st.cache_data
def charger_donnees():

    df = pd.read_csv(
        DATA_PATH,
        sep=";",
        low_memory=False
    )

    # Colonnes vides parasites au début du fichier
    df = df.loc[
        :,
        ~df.columns.str.startswith("Unnamed")
    ].copy()

    colonnes_numeriques = [
        "default_flag",
        "disc_year",
        "pl_rade",
        "pl_bmasse",
        "pl_insol",
        "pl_eqt",
        "sy_dist",
        "pl_orbper",
        "pl_orbsmax",
        "st_teff"
    ]

    for colonne in colonnes_numeriques:

        if colonne in df.columns:

            df[colonne] = pd.to_numeric(
                df[colonne],
                errors="coerce"
            )

    # Une seule ligne de référence par planète
    df = df[
        df["default_flag"] == 1
    ].copy()

    df = df.drop_duplicates(
        subset="pl_name"
    )

    # Année de découverte
    df = df[
        df["disc_year"].notna()
    ].copy()

    df["disc_year"] = (
        df["disc_year"]
        .astype(int)
    )

    # Distance
    # Le dataset utilise des parsecs
    # 1 parsec ≈ 3,26156 années-lumière
    df["distance_ly"] = (
        df["sy_dist"]
        * 3.26156
    )

    # Rayon en kilomètres
    df["rayon_km"] = (
        df["pl_rade"]
        * RAYON_TERRE_KM
    )

    # Regrouper les méthodes :
    # Transit / Vitesse radiale / Autres
    df["methode_groupe"] = np.select(
        [
            df["discoverymethod"] == "Transit",
            df["discoverymethod"] == "Radial Velocity"
        ],
        [
            "Transit",
            "Vitesse radiale"
        ],
        default="Autres"
    )

    # Catégories de taille simplifiées
    conditions = [

        df["pl_rade"] < 0.8,

        df["pl_rade"].between(
            0.8,
            1.6,
            inclusive="both"
        ),

        (
            (df["pl_rade"] > 1.6)
            & (df["pl_rade"] <= 4)
        ),

        (
            (df["pl_rade"] > 4)
            & (df["pl_rade"] <= 10)
        ),

        df["pl_rade"] > 10
    ]

    labels = [
        "Plus petite que la Terre · < 5 100 km",
        "Proche de la taille terrestre · 5 100–10 200 km",
        "Taille intermédiaire · 10 200–25 500 km",
        "Grande planète · 25 500–63 700 km",
        "Très grande planète · > 63 700 km"
    ]

    df["categorie_taille"] = np.select(
        conditions,
        labels,
        default="Taille inconnue"
    )

    return df


# ============================================================
# SIDEBAR — FILTRES
# ============================================================

def sauvegarder_annee_fin():

    st.session_state.filtre_annee_fin = (
        st.session_state.widget_annee_fin
    )


def basculer_methode(cle):

    st.session_state[cle] = (
        not st.session_state[cle]
    )


def sidebar_filters(df):

    annee_max = int(
        df["disc_year"].max()
    )

    # --------------------------------------------------------
    # ÉTAT INITIAL DES FILTRES
    # --------------------------------------------------------

    if "filtre_annee_fin" not in st.session_state:
        st.session_state.filtre_annee_fin = annee_max

    if "filtre_transit" not in st.session_state:
        st.session_state.filtre_transit = True

    if "filtre_vitesse_radiale" not in st.session_state:
        st.session_state.filtre_vitesse_radiale = True

    if "filtre_autres" not in st.session_state:
        st.session_state.filtre_autres = True

    if "filtre_distance_active" not in st.session_state:
        st.session_state.filtre_distance_active = False

    distance_max_dataset = int(
        np.ceil(
            df["distance_ly"]
            .dropna()
            .max()
        )
    )

    distance_defaut = min(
        500,
        distance_max_dataset
    )

    if "filtre_distance_max" not in st.session_state:
        st.session_state.filtre_distance_max = distance_defaut

    # --------------------------------------------------------
    # Le widget du slider possède une clé différente de la
    # valeur canonique. On la réassigne ici, en début de
    # fonction, à chaque exécution de page : ainsi le slider
    # reprend toujours la dernière année choisie, même en
    # arrivant sur une page différente.
    # --------------------------------------------------------

    st.session_state.widget_annee_fin = (
        st.session_state.filtre_annee_fin
    )

    st.sidebar.header(
        "Explorer les découvertes"
    )

    # ----------------------------------------------------
    # FILTRE 1 — ANNÉE DE FIN UNIQUEMENT
    # ----------------------------------------------------

    st.sidebar.slider(
        "Découvertes jusqu’en",
        min_value=ANNEE_DEBUT,
        max_value=annee_max,
        step=1,
        key="widget_annee_fin",
        on_change=sauvegarder_annee_fin
    )

    annee_fin = (
        st.session_state.filtre_annee_fin
    )

    st.sidebar.caption(
        "Début fixe : 1992"
    )

    # ----------------------------------------------------
    # FILTRE 2 — MÉTHODES REGROUPÉES
    # ----------------------------------------------------

    st.sidebar.markdown(
        "### Méthode de découverte"
    )

    st.sidebar.button(
        "Transit",
        key="bouton_transit",
        type=(
            "primary"
            if st.session_state.filtre_transit
            else "secondary"
        ),
        use_container_width=True,
        on_click=basculer_methode,
        args=("filtre_transit",)
    )

    st.sidebar.button(
        "Vitesse radiale",
        key="bouton_vitesse_radiale",
        type=(
            "primary"
            if st.session_state.filtre_vitesse_radiale
            else "secondary"
        ),
        use_container_width=True,
        on_click=basculer_methode,
        args=("filtre_vitesse_radiale",)
    )

    st.sidebar.button(
        "Autres",
        key="bouton_autres",
        type=(
            "primary"
            if st.session_state.filtre_autres
            else "secondary"
        ),
        use_container_width=True,
        on_click=basculer_methode,
        args=("filtre_autres",)
    )

    st.sidebar.markdown(
        "<div style='height: 10px;'></div>",
        unsafe_allow_html=True
    )

    methodes_selectionnees = []

    if st.session_state.filtre_transit:

        methodes_selectionnees.append(
            "Transit"
        )

    if st.session_state.filtre_vitesse_radiale:

        methodes_selectionnees.append(
            "Vitesse radiale"
        )

    if st.session_state.filtre_autres:

        methodes_selectionnees.append(
            "Autres"
        )

    # ----------------------------------------------------
    # FILTRE 3 — DISTANCE
    # ----------------------------------------------------

    st.sidebar.markdown(
        "<div style='height: 10px;'></div>",
        unsafe_allow_html=True
    )

    st.sidebar.divider()

    st.sidebar.checkbox(
        "Limiter la distance à la Terre",
        key="filtre_distance_active"
    )

    filtrer_distance = (
        st.session_state.filtre_distance_active
    )

    if filtrer_distance:

        st.sidebar.number_input(
            "Distance maximale (années-lumière)",
            min_value=1,
            max_value=distance_max_dataset,
            step=10,
            key="filtre_distance_max"
        )

        st.sidebar.caption(
            "Ce filtre permet de se concentrer sur notre voisinage "
            "astronomique. Il ne constitue pas un critère d’habitabilité."
        )

    distance_max = (
        st.session_state.filtre_distance_max
    )

    # ======================================================
    # APPLICATION DES FILTRES
    # ======================================================

    df_filtre = df[
        df["disc_year"].between(
            ANNEE_DEBUT,
            annee_fin
        )
    ].copy()

    if methodes_selectionnees:

        df_filtre = df_filtre[
            df_filtre["methode_groupe"]
            .isin(
                methodes_selectionnees
            )
        ].copy()

    else:

        df_filtre = (
            df_filtre
            .iloc[0:0]
            .copy()
        )

    if filtrer_distance:

        df_filtre = df_filtre[
            df_filtre["distance_ly"].notna()
            & (
                df_filtre["distance_ly"]
                <= distance_max
            )
        ].copy()

    # ======================================================
    # RÉSUMÉ DES FILTRES
    # ======================================================

    nb_selection_affiche = (
        f"{len(df_filtre):,}"
        .replace(",", " ")
    )

    st.caption(
        f"Sélection actuelle : "
        f"{nb_selection_affiche} exoplanètes · "
        f"{ANNEE_DEBUT}–{annee_fin}"
    )

    return df_filtre, methodes_selectionnees


# ============================================================
# MÉTHODOLOGIE / SOURCE
# ============================================================

def footer():

    st.divider()

    st.caption(
        "Méthode · Une candidate potentielle est définie ici "
        "comme une planète dont le rayon se situe entre environ "
        "3 200 et 10 200 km "
        "(0,5 à 1,6 fois le rayon terrestre) "
        "et qui reçoit entre 0,5 et 2 fois l’énergie reçue "
        "par la Terre. Il s’agit d’une présélection simplifiée, "
        "et non d’une preuve d’habitabilité."
    )

    st.caption(
        "Source · NASA Exoplanet Archive · "
        "Une seule ligne de référence est conservée "
        "par planète avec default_flag = 1."
    )
