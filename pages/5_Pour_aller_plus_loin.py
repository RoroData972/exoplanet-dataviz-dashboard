# ============================================================
# PAGE BONUS · POUR ALLER PLUS LOIN
# Approfondissement des candidates sélectionnées
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pour aller plus loin · Exoplanètes",
    page_icon="🔭",
    layout="wide"
)


# ============================================================
# PALETTE
# ============================================================

BLEU_FONCE = "#0D3B66"
BLEU = "#1976D2"
BLEU_VIF = "#2D9CDB"
GRIS = "#B8C4D1"
GRILLE = "#E8EDF3"

RAYON_TERRE_KM = 6371

RAYON_MIN = 0.5
RAYON_MAX = 1.6

INSOLATION_MIN = 0.5
INSOLATION_MAX = 2.0

ANNEE_DEBUT = 1992


# ============================================================
# STYLE
# ============================================================

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
        min-height: 3.2rem;

        display: flex;
        align-items: flex-start;

        white-space: normal !important;
        overflow: visible !important;
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

    button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {{
        background-color: #EEF7FF !important;
        border-color: #B9D7F2 !important;
        color: {BLEU_FONCE} !important;
        font-weight: 650 !important;
    }}

    /* Bouton retour toujours visible */
    .st-key-retour_fixe {{
        position: fixed;
        top: 3.8rem;
        left: 1.5rem;
        z-index: 9999;
        width: 190px;
    }}

    .st-key-retour_fixe button {{
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATASET
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DATA_PATH = (
    BASE_DIR
    / "data"
    / "exoplanets.csv"
)


@st.cache_data
def charger_donnees():

    df = pd.read_csv(
        DATA_PATH,
        sep=";",
        low_memory=False
    )

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


    # Une seule ligne par planète
    df = df[
        df["default_flag"] == 1
    ].copy()


    df = df.drop_duplicates(
        subset="pl_name"
    )


    # Années valides
    df = df[
        df["disc_year"].notna()
    ].copy()


    df["disc_year"] = (
        df["disc_year"]
        .astype(int)
    )


    # Distance : parsecs → années-lumière
    df["distance_ly"] = (
        df["sy_dist"]
        * 3.26156
    )


    # Rayon terrestre → kilomètres
    df["rayon_km"] = (
        df["pl_rade"]
        * RAYON_TERRE_KM
    )


    # Méthodes regroupées
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


    return df


df = charger_donnees()


ANNEE_MAX = int(
    df["disc_year"].max()
)


# ============================================================
# RÉCUPÉRATION DES FILTRES DU DASHBOARD PRINCIPAL
# ============================================================

# Si la page est ouverte directement,
# on utilise les valeurs par défaut du dashboard.

if "filtre_annee_fin" not in st.session_state:
    st.session_state.filtre_annee_fin = ANNEE_MAX


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


annee_fin = (
    st.session_state.filtre_annee_fin
)


filtrer_distance = (
    st.session_state.filtre_distance_active
)


distance_max = (
    st.session_state.filtre_distance_max
)


# ============================================================
# MÉTHODES SÉLECTIONNÉES
# ============================================================

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


# ============================================================
# APPLICATION DES MÊMES FILTRES QUE DANS APP.PY
# ============================================================

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
        &
        (
            df_filtre["distance_ly"]
            <= distance_max
        )
    ].copy()


# ============================================================
# RECALCUL DES CANDIDATES
# ============================================================

candidates = df_filtre.dropna(
    subset=[
        "pl_rade",
        "pl_insol"
    ]
).copy()


candidates = candidates[
    candidates["pl_insol"] > 0
].copy()


candidates = candidates[
    candidates["pl_rade"]
    .between(
        RAYON_MIN,
        RAYON_MAX
    )
    &
    candidates["pl_insol"]
    .between(
        INSOLATION_MIN,
        INSOLATION_MAX
    )
].copy()


nb_candidates = len(
    candidates
)


# ============================================================
# RETOUR AU DASHBOARD — BOUTON FLOTTANT
# ============================================================

with st.container(
    key="retour_fixe"
):

    if st.button(
        "← Retour au dashboard",
        key="bouton_retour_dashboard",
        type="secondary",
        use_container_width=True
    ):

        st.switch_page(
            "app.py"
        )


# Petit espace en haut pour éviter que le bouton
# chevauche le contenu lorsque l'on arrive sur la page
st.markdown(
    "<div style='height: 20px;'></div>",
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.title(
    "🔭 Pour aller plus loin"
)


if nb_candidates == 0:

    st.header(
        "Aucune candidate ne correspond aux filtres actuels"
    )

    st.warning(
        "Retournez au dashboard principal pour élargir "
        "l’année de fin, les méthodes de découverte "
        "ou la distance maximale."
    )

    st.stop()


mot_candidate = (
    "candidate"
    if nb_candidates == 1
    else "candidates"
)


st.header(
    f"Que savons-nous vraiment des "
    f"{nb_candidates} {mot_candidate} ?"
)


# ============================================================
# RÉSUMÉ DES FILTRES
# ============================================================

methodes_resume = (
    ", ".join(
        methodes_selectionnees
    )
)


resume_distance = (
    f"≤ {distance_max} années-lumière"
    if filtrer_distance
    else "sans limite de distance"
)


st.caption(
    f"Filtres repris du dashboard · "
    f"1992–{annee_fin} · "
    f"{methodes_resume} · "
    f"{resume_distance}"
)


st.markdown(
    """
    Les critères de présélection permettent d'identifier des mondes
    intéressants, mais ils ne disent pas tout.

    Cette page regarde donc **ce que les données permettent encore
    d'apprendre sur les candidates actuellement sélectionnées**.
    """
)


st.divider()


# ============================================================
# 1 — DISTANCE DES CANDIDATES
# ============================================================

st.markdown(
    "## 1 · Quelles candidates sont les plus proches ?"
)


candidates_distance = candidates[
    candidates["distance_ly"].notna()
].copy()


nb_distance_connue = len(
    candidates_distance
)


mot_distance = (
    "candidate"
    if nb_distance_connue == 1
    else "candidates"
)


st.caption(
    f"La distance est renseignée pour "
    f"{nb_distance_connue} {mot_distance} "
    f"sur {nb_candidates}. "
    "Le graphique porte uniquement sur les distances connues."
)


if candidates_distance.empty:

    st.info(
        "Aucune distance n'est renseignée "
        "pour les candidates actuelles."
    )


else:

    candidats_distance_graph = (
        candidates_distance
        .sort_values(
            "distance_ly",
            ascending=False
        )
        .copy()
    )


    fig_distance = go.Figure()


    fig_distance.add_trace(

        go.Bar(

            x=candidats_distance_graph[
                "distance_ly"
            ],

            y=candidats_distance_graph[
                "pl_name"
            ],

            orientation="h",

            marker_color=BLEU,

            text=candidats_distance_graph[
                "distance_ly"
            ].round(1),

            texttemplate=(
                "%{text} al"
            ),

            textposition="outside",

            hovertemplate=(
                "<b>%{y}</b><br>"
                "Distance : %{x:.1f} années-lumière"
                "<extra></extra>"
            )
        )
    )


    fig_distance.update_layout(

        height=min(
            580,
            max(
                400,
                38 * nb_distance_connue
            )
        ),

        xaxis_title=(
            "Distance à la Terre "
            "(années-lumière)"
        ),

        yaxis_title="",

        margin=dict(
            l=30,
            r=100,
            t=20,
            b=40
        ),

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(
            size=14
        )
    )


    fig_distance.update_xaxes(
        showgrid=True,
        gridcolor=GRILLE,
        rangemode="tozero"
    )


    fig_distance.update_yaxes(
        showgrid=False,
        automargin=True,

        tickfont=dict(
            size=16,
            color="#3E4A59"
        )
    )


    st.plotly_chart(
        fig_distance,
        use_container_width=True
    )


    plus_proche = (
        candidates_distance
        .sort_values(
            "distance_ly"
        )
        .iloc[0]
    )


    st.info(
        f"🌍 Parmi les candidates dont la distance est connue, "
        f"**{plus_proche['pl_name']}** est la plus proche "
        f"dans cette sélection, à environ "
        f"**{plus_proche['distance_ly']:.0f} années-lumière**."
    )


st.divider()


# ============================================================
# 2 — COMPLÉTUDE DES DONNÉES
# ============================================================

st.markdown(
    "## 2 · Que savons-nous réellement de ces mondes ?"
)


st.caption(
    "Toutes les caractéristiques ne sont pas disponibles "
    "pour toutes les candidates."
)


indicateurs_completude = [

    (
        "Distance",
        "distance_ly"
    ),

    (
        "Période orbitale",
        "pl_orbper"
    ),

    (
        "Température de l’étoile",
        "st_teff"
    ),

    (
        "Température d’équilibre",
        "pl_eqt"
    ),

    (
        "Masse",
        "pl_bmasse"
    )
]


lignes_completude = []


for libelle, colonne in indicateurs_completude:

    nb_connu = int(
        candidates[
            colonne
        ]
        .notna()
        .sum()
    )


    lignes_completude.append(
        {
            "information": libelle,
            "connues": nb_connu,
            "texte": (
                f"{nb_connu} / "
                f"{nb_candidates}"
            )
        }
    )


df_completude = pd.DataFrame(
    lignes_completude
)


fig_completude = go.Figure()


fig_completude.add_trace(

    go.Bar(

        x=df_completude[
            "connues"
        ],

        y=df_completude[
            "information"
        ],

        orientation="h",

        marker_color=BLEU_VIF,

        text=df_completude[
            "texte"
        ],

        textposition="outside",

        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x} candidates avec une valeur connue"
            "<extra></extra>"
        )
    )
)


fig_completude.update_layout(

    height=420,

    xaxis_title=(
        "Nombre de candidates avec "
        "une donnée disponible"
    ),

    yaxis_title="",

    margin=dict(
        l=30,
        r=100,
        t=20,
        b=40
    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    font=dict(
        size=14
    )
)


fig_completude.update_xaxes(

    range=[
        0,
        max(
            nb_candidates * 1.15,
            1
        )
    ],

    dtick=1,

    showgrid=True,

    gridcolor=GRILLE,

    rangemode="tozero"
)


fig_completude.update_yaxes(

    showgrid=False,

    autorange="reversed",

    automargin=True,

    tickfont=dict(
        size=16,
        color="#3E4A59"
    )
)


st.plotly_chart(
    fig_completude,
    use_container_width=True
)


st.info(
    "💡 Une candidate peut satisfaire nos deux critères "
    "de présélection tout en restant mal documentée sur "
    "d'autres caractéristiques importantes. "
    "C'est une des raisons pour lesquelles cette sélection "
    "ne constitue pas une preuve d'habitabilité."
)


st.divider()


# ============================================================
# 3 — EXPLORER UNE CANDIDATE
# ============================================================

st.markdown(
    "## 3 · Explorer une candidate"
)


# Les planètes avec distance connue apparaissent d'abord,
# de la plus proche à la plus lointaine.

candidates_details = (
    candidates
    .sort_values(
        [
            "distance_ly",
            "pl_name"
        ],
        na_position="last"
    )
    .copy()
)


nom_candidate = st.selectbox(
    "Choisir une planète",
    options=candidates_details[
        "pl_name"
    ].tolist()
)


planete = (
    candidates_details[
        candidates_details[
            "pl_name"
        ] == nom_candidate
    ]
    .iloc[0]
)


# ============================================================
# MÉTHODE DE DÉCOUVERTE LIS lisible
# ============================================================

methode_affichee = (
    "Vitesse radiale"
    if planete[
        "discoverymethod"
    ] == "Radial Velocity"
    else planete[
        "discoverymethod"
    ]
)


st.markdown(
    f"### {planete['pl_name']}"
)


st.caption(
    f"Découverte en "
    f"{int(planete['disc_year'])} · "
    f"Méthode : {methode_affichee}"
)


# ============================================================
# FONCTION DE FORMATAGE
# ============================================================

def format_nombre(
    valeur,
    format_spec,
    suffixe=""
):

    if pd.isna(
        valeur
    ):

        return (
            "Non renseignée"
        )


    return (
        f"{valeur:{format_spec}}"
        f"{suffixe}"
        .replace(",", " ")
        .replace(".", ",")
    )


# ============================================================
# PREMIÈRE LIGNE DE KPIs
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Rayon",
        format_nombre(
            planete[
                "rayon_km"
            ],
            ",.0f",
            " km"
        )
    )


with col2:

    st.metric(
        "Énergie reçue",
        format_nombre(
            planete[
                "pl_insol"
            ],
            ".2f",
            " × Terre"
        )
    )


with col3:

    st.metric(
        "Distance",
        format_nombre(
            planete[
                "distance_ly"
            ],
            ".1f",
            " années-lumière"
        )
    )


# ============================================================
# DEUXIÈME LIGNE DE KPIs
# ============================================================

col4, col5, col6 = st.columns(3)


with col4:

    st.metric(
        "Période orbitale",
        format_nombre(
            planete[
                "pl_orbper"
            ],
            ".1f",
            " jours"
        )
    )


with col5:

    st.metric(
        "Masse",
        format_nombre(
            planete[
                "pl_bmasse"
            ],
            ".2f",
            " × Terre"
        )
    )


with col6:

    if pd.isna(
        planete[
            "pl_eqt"
        ]
    ):

        temperature_affichee = (
            "Non renseignée"
        )


    else:

        temperature_celsius = (
            planete[
                "pl_eqt"
            ]
            - 273.15
        )


        temperature_affichee = (
            f"{planete['pl_eqt']:.0f} K "
            f"(≈ {temperature_celsius:.0f} °C)"
        )


    st.metric(
        "Température d’équilibre",
        temperature_affichee
    )


# ============================================================
# ÉTOILE
# ============================================================

if pd.isna(
    planete[
        "st_teff"
    ]
):

    temperature_etoile = (
        "Non renseignée"
    )


else:

    temperature_etoile = (
        f"{planete['st_teff']:,.0f} K"
        .replace(",", " ")
    )


st.info(
    f"⭐ **Température de l’étoile :** "
    f"{temperature_etoile}\n\n"
    "La température d’équilibre est une estimation théorique. "
    "Elle ne correspond pas nécessairement à la température "
    "réelle à la surface de la planète."
)


# ============================================================
# CONCLUSION
# ============================================================

st.success(
    "🔎 **À retenir :** arriver jusqu'à cette liste de candidates "
    "n'est que le début. Pour étudier réellement leur habitabilité, "
    "il faudrait disposer d'informations supplémentaires sur leur "
    "atmosphère, leur composition et leur environnement."
)