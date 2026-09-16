# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# Dashboard Streamlit — Grand public
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURATION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="À la recherche de mondes potentiellement habitables",
    page_icon="🪐",
    layout="wide"
)


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


## ============================================================
# STYLE GLOBAL
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
# CHEMIN DU DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "exoplanets.csv"


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


df = charger_donnees()


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

ANNEE_MAX = int(
    df["disc_year"].max()
)


# ============================================================
# EN-TÊTE
# ============================================================

st.title(
    "🪐 À la recherche de mondes potentiellement habitables"
)

st.markdown(
    """
    **Parmi les milliers d’exoplanètes découvertes, seule une petite
    fraction des planètes suffisamment documentées réunit simultanément
    des caractéristiques physiques compatibles avec une habitabilité potentielle.**
    """
)

st.caption(
    "Une exploration destinée au grand public · "
    "Source : NASA Exoplanet Archive"
)


# ============================================================
# SIDEBAR — FILTRES
# ============================================================

st.sidebar.header(
    "Explorer les découvertes"
)


# ------------------------------------------------------------
# FILTRE 1 — ANNÉE DE FIN UNIQUEMENT
# ------------------------------------------------------------

# Valeur persistante entre les pages
if "filtre_annee_fin" not in st.session_state:
    st.session_state.filtre_annee_fin = ANNEE_MAX


# Le widget possède une clé différente.
# Quand on revient de la page bonus, on recharge
# le slider avec la dernière année choisie.
if "widget_annee_fin" not in st.session_state:
    st.session_state.widget_annee_fin = (
        st.session_state.filtre_annee_fin
    )


def sauvegarder_annee_fin():

    st.session_state.filtre_annee_fin = (
        st.session_state.widget_annee_fin
    )


st.sidebar.slider(
    "Découvertes jusqu’en",
    min_value=ANNEE_DEBUT,
    max_value=ANNEE_MAX,
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

# ------------------------------------------------------------
# FILTRE 2 — MÉTHODES REGROUPÉES
# ------------------------------------------------------------


st.sidebar.markdown(
    "### Méthode de découverte"
)


# ------------------------------------------------------------
# ÉTAT INITIAL
# Les 3 méthodes sont sélectionnées au lancement
# ------------------------------------------------------------

if "filtre_transit" not in st.session_state:
    st.session_state.filtre_transit = True

if "filtre_vitesse_radiale" not in st.session_state:
    st.session_state.filtre_vitesse_radiale = True

if "filtre_autres" not in st.session_state:
    st.session_state.filtre_autres = True


# ------------------------------------------------------------
# FONCTION DE SÉLECTION / DÉSÉLECTION
# ------------------------------------------------------------

def basculer_methode(cle):

    st.session_state[cle] = (
        not st.session_state[cle]
    )


# ------------------------------------------------------------
# BOUTON TRANSIT
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# BOUTON VITESSE RADIALE
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# BOUTON AUTRES
# ------------------------------------------------------------

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

# ------------------------------------------------------------
# LISTE DES MÉTHODES RÉELLEMENT SÉLECTIONNÉES
# ------------------------------------------------------------

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

# ------------------------------------------------------------
# FILTRE 3 — DISTANCE
# ------------------------------------------------------------

st.sidebar.markdown(
    "<div style='height: 10px;'></div>",
    unsafe_allow_html=True
)

st.sidebar.divider()


# ------------------------------------------------------------
# ÉTAT DU FILTRE DISTANCE
# ------------------------------------------------------------

if "filtre_distance_active" not in st.session_state:
    st.session_state.filtre_distance_active = False


st.sidebar.checkbox(
    "Limiter la distance à la Terre",
    key="filtre_distance_active"
)


filtrer_distance = (
    st.session_state.filtre_distance_active
)


# ------------------------------------------------------------
# DISTANCE MAXIMALE
# ------------------------------------------------------------

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

# ============================================================
# APPLICATION DES FILTRES
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
        & (
            df_filtre["distance_ly"]
            <= distance_max
        )
    ].copy()


# ============================================================
# RÉSUMÉ DES FILTRES
# ============================================================

nb_selection_affiche = (
    f"{len(df_filtre):,}"
    .replace(",", " ")
)

st.caption(
    f"Sélection actuelle : "
    f"{nb_selection_affiche} exoplanètes · "
    f"{ANNEE_DEBUT}–{annee_fin}"
)


# ============================================================
# NAVIGATION — BOUTONS
# ============================================================

if "page_dashboard" not in st.session_state:

    st.session_state.page_dashboard = 1


pages = {
    1: "1 · Découvertes",
    2: "2 · Diversité",
    3: "3 · Conditions favorables",
    4: "4 · Candidates"
}


colonnes_nav = st.columns(4)


for numero, colonne in zip(
    pages.keys(),
    colonnes_nav
):

    with colonne:

        actif = (
            st.session_state.page_dashboard
            == numero
        )

        if st.button(
            pages[numero],
            key=f"nav_{numero}",
            type=(
                "primary"
                if actif
                else "secondary"
            ),
            use_container_width=True
        ):

            st.session_state.page_dashboard = numero

            st.rerun()


st.divider()

page = (
    st.session_state
    .page_dashboard
)


# ============================================================
# PAGE 1 — HISTOIRE DES DÉCOUVERTES
# ============================================================

if page == 1:

    if df_filtre.empty:

        st.warning(
            "Aucune exoplanète ne correspond aux filtres sélectionnés."
        )

    else:

        # ----------------------------------------------------
        # Agrégation annuelle
        # ----------------------------------------------------

        decouvertes_annee = (
            df_filtre
            .groupby("disc_year")
            .size()
            .reset_index(
                name="decouvertes"
            )
            .sort_values(
                "disc_year"
            )
        )


        total_planetes = len(
            df_filtre
        )


        ligne_pic = (
            decouvertes_annee
            .loc[
                decouvertes_annee[
                    "decouvertes"
                ].idxmax()
            ]
        )


        annee_pic = int(
            ligne_pic[
                "disc_year"
            ]
        )


        nb_pic = int(
            ligne_pic[
                "decouvertes"
            ]
        )


        methode_counts = (
            df_filtre[
                "methode_groupe"
            ]
            .value_counts()
        )


        methode_dominante = (
            methode_counts.index[0]
        )


        nb_methode_dominante = int(
            methode_counts.iloc[0]
        )


        part_methode = (
            nb_methode_dominante
            / total_planetes
            * 100
        )


        # ----------------------------------------------------
        # 2014
        # ----------------------------------------------------

        ligne_2014 = decouvertes_annee[
            decouvertes_annee[
                "disc_year"
            ] == 2014
        ]


        nb_2014 = (
            int(
                ligne_2014[
                    "decouvertes"
                ].iloc[0]
            )
            if not ligne_2014.empty
            else 0
        )


        # ----------------------------------------------------
        # 2016
        # ----------------------------------------------------

        ligne_2016 = decouvertes_annee[
            decouvertes_annee[
                "disc_year"
            ] == 2016
        ]


        nb_2016 = (
            int(
                ligne_2016[
                    "decouvertes"
                ].iloc[0]
            )
            if not ligne_2016.empty
            else 0
        )


        kepler_story_visible = (
            annee_pic in [
                2014,
                2016
            ]
            and "Transit"
            in methodes_selectionnees
        )


        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        if annee_pic == 2016:

            st.header(
                "Kepler a transformé la recherche d’exoplanètes, "
                "avec deux vagues de découvertes culminant en 2016"
            )

        elif annee_pic == 2014:

            st.header(
                "Kepler accélère la recherche d’exoplanètes, "
                "avec un premier grand tournant en 2014"
            )

        else:

            st.header(
                "En trois décennies, les découvertes "
                "d’exoplanètes se sont multipliées"
            )


        st.caption(
            "Chaque point représente le nombre d’exoplanètes "
            "associées à une année de découverte dans la sélection actuelle."
        )


        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Exoplanètes dans la sélection",
                f"{total_planetes:,}"
                .replace(",", " ")
            )


        with col2:

            st.metric(
                label=(
                    f"Année la plus riche · "
                    f"{nb_pic} découvertes"
                ),
                value=str(
                    annee_pic
                )
            )


        with col3:

            st.metric(
                label=(
                    f"Méthode dominante · "
                    f"{part_methode:.0f} % des découvertes"
                ),
                value=methode_dominante
            )


        # ----------------------------------------------------
        # GRAPHIQUE
        # ----------------------------------------------------

        st.markdown(
            "### Les découvertes au fil du temps"
        )


        fig1 = go.Figure()


        fig1.add_trace(

            go.Scatter(

                x=decouvertes_annee[
                    "disc_year"
                ],

                y=decouvertes_annee[
                    "decouvertes"
                ],

                mode="lines+markers",

                line=dict(
                    width=3,
                    color=BLEU
                ),

                marker=dict(
                    size=7,
                    color=BLEU
                ),

                fill="tozeroy",

                fillcolor=(
                    "rgba(25,118,210,0.10)"
                ),

                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "%{y} découvertes"
                    "<extra></extra>"
                ),

                showlegend=False
            )
        )


        # Année record

        fig1.add_trace(

            go.Scatter(

                x=[
                    annee_pic
                ],

                y=[
                    nb_pic
                ],

                mode="markers",

                marker=dict(
                    size=17,
                    color=BLEU_VIF,
                    line=dict(
                        width=2,
                        color=BLEU_FONCE
                    )
                ),

                hovertemplate=(
                    f"<b>{annee_pic}</b><br>"
                    f"{nb_pic} découvertes"
                    "<extra></extra>"
                ),

                showlegend=False
            )
        )


        # ----------------------------------------------------
        # ANNOTATIONS KEPLER
        # ----------------------------------------------------

        if kepler_story_visible:

            if nb_2014 > 0:

                fig1.add_annotation(

                    x=2014,

                    y=nb_2014,

                    text=(
                        "<b>2014</b><br>"
                        "715 planètes validées<br>"
                        "par Kepler"
                    ),

                    showarrow=True,

                    arrowhead=2,

                    arrowwidth=1.5,

                    arrowcolor=BLEU_FONCE,

                    ax=-90,

                    ay=-80,

                    bgcolor=(
                        "rgba(255,255,255,0.96)"
                    ),

                    bordercolor=BLEU_VIF,

                    borderwidth=1,

                    borderpad=6,

                    font=dict(
                        size=13,
                        color="#263238"
                    )
                )


            if nb_2016 > 0:

                fig1.add_annotation(

                    x=2016,

                    y=nb_2016,

                    text=(
                        "<b>2016</b><br>"
                        "1 284 planètes validées<br>"
                        "par Kepler"
                    ),

                    showarrow=True,

                    arrowhead=2,

                    arrowwidth=1.5,

                    arrowcolor=BLEU_FONCE,

                    ax=95,

                    ay=-95,

                    bgcolor=(
                        "rgba(255,255,255,0.96)"
                    ),

                    bordercolor=BLEU_VIF,

                    borderwidth=1,

                    borderpad=6,

                    font=dict(
                        size=13,
                        color="#263238"
                    )
                )


        # ----------------------------------------------------
        # LAYOUT
        # ----------------------------------------------------

        fig1.update_layout(

            height=580,

            xaxis_title=(
                "Année de découverte"
            ),

            yaxis_title=(
                "Nombre d’exoplanètes découvertes"
            ),

            margin=dict(
                l=30,
                r=30,
                t=80,
                b=50
            ),

            plot_bgcolor="white",

            paper_bgcolor="white",

            font=dict(
                size=14
            )
        )


        fig1.update_xaxes(
            showgrid=False
        )


        fig1.update_yaxes(
            showgrid=True,
            gridcolor=GRILLE,
            rangemode="tozero"
        )


        st.plotly_chart(
            fig1,
            use_container_width=True
        )


        # ----------------------------------------------------
        # EXPLICATION
        # ----------------------------------------------------

        if kepler_story_visible:

            st.info(
                "🚀 **Pourquoi les pics de 2014 et 2016 ?**\n\n"

                "La NASA a lancé le télescope spatial **Kepler en 2009** "
                "pour rechercher spécifiquement des exoplanètes. "
                "Pendant plusieurs années, il a surveillé en continu "
                "la luminosité de plus de **150 000 étoiles**. "
                "Lorsqu’une planète passe devant son étoile, "
                "elle provoque une très légère baisse de luminosité : "
                "c’est la **méthode du transit**.\n\n"

                "Kepler a ainsi accumulé des milliers de candidates. "
                "En **2014**, la NASA a annoncé la validation de "
                "**715 nouvelles exoplanètes** issues des données Kepler. "
                "Deux ans plus tard, en **2016**, l’exploitation statistique "
                "du catalogue permet de valider **1 284 nouvelles planètes "
                "en une seule annonce**.\n\n"

                "Ces deux vagues montrent comment une mission dédiée, "
                "combinée à de nouvelles méthodes d’analyse, "
                "a changé l’échelle de la recherche d’exoplanètes."
            )


            st.caption(
                "Sources : NASA · Mission Kepler · "
                "annonces du 26 février 2014 et du 10 mai 2016"
            )


        else:

            st.info(
                "💡 La sélection actuelle montre une autre partie de "
                "l’histoire des découvertes. Les filtres sur la période, "
                "la méthode ou la distance peuvent changer fortement "
                "l’année record et la méthode dominante."
            )


# ============================================================
# PAGE 2 — DIVERSITÉ DES TAILLES
# ============================================================

elif page == 2:

    df_rayon = df_filtre[
        df_filtre[
            "pl_rade"
        ].notna()
    ].copy()


    if df_rayon.empty:

        st.warning(
            "Aucune mesure de rayon disponible pour cette sélection."
        )


    else:

        nb_rayon = len(
            df_rayon
        )


        rayon_median = (
            df_rayon[
                "pl_rade"
            ]
            .median()
        )


        rayon_median_km = (
            rayon_median
            * RAYON_TERRE_KM
        )


        nb_taille_compatible = int(
            (
                df_rayon[
                    "pl_rade"
                ]
                <= RAYON_MAX
            )
            .sum()
        )


        part_taille_compatible = (
            nb_taille_compatible
            / nb_rayon
            * 100
        )


        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        st.header(
            f"{part_taille_compatible:.0f} % des exoplanètes "
            "dont le rayon est connu ont un rayon inférieur "
            "à 1,6 fois celui de la Terre"
        )


        st.caption(
            "La Terre possède un rayon d’environ 6 371 km. "
            "Les valeurs ci-dessous sont converties en kilomètres "
            "pour faciliter la lecture."
        )


        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Planètes avec rayon connu",
                f"{nb_rayon:,}"
                .replace(",", " ")
            )


        with col2:

            st.metric(
                label="Rayon médian",
                value=(
                    f"≈ {rayon_median_km:,.0f} km"
                    .replace(",", " ")
                ),
                help=(
                    "Le rayon correspond à la distance entre le centre "
                    "de la planète et sa surface. "
                    f"Ici, la médiane vaut environ "
                    f"{rayon_median:.1f} fois le rayon de la Terre."
                )
            )


        with col3:

            st.metric(
                label=(
                    f"Rayon < 10 200 km · "
                    f"{nb_taille_compatible:,} planètes"
                ).replace(",", " "),
                value=(
                    f"{part_taille_compatible:.0f} %"
                )
            )


        # ----------------------------------------------------
        # GRAPHIQUE
        # ----------------------------------------------------

        st.markdown(
            "### Répartition par catégorie de taille"
        )


        ordre_categories = [
            "Plus petite que la Terre · < 5 100 km",
            "Proche de la taille terrestre · 5 100–10 200 km",
            "Taille intermédiaire · 10 200–25 500 km",
            "Grande planète · 25 500–63 700 km",
            "Très grande planète · > 63 700 km"
        ]


        repartition = (
            df_rayon[
                "categorie_taille"
            ]
            .value_counts()
            .reindex(
                ordre_categories,
                fill_value=0
            )
            .reset_index()
        )


        repartition.columns = [
            "categorie",
            "nombre"
        ]


        categories_petites = [
            "Plus petite que la Terre · < 5 100 km",
            "Proche de la taille terrestre · 5 100–10 200 km"
        ]


        repartition[
            "couleur"
        ] = np.where(
            repartition[
                "categorie"
            ].isin(
                categories_petites
            ),
            BLEU,
            GRIS
        )


        fig2 = go.Figure()


        fig2.add_trace(

            go.Bar(

                x=repartition[
                    "nombre"
                ],

                y=repartition[
                    "categorie"
                ],

                orientation="h",

                marker_color=repartition[
                    "couleur"
                ],

                text=repartition[
                    "nombre"
                ],

                textposition="outside",

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "%{x} exoplanètes"
                    "<extra></extra>"
                )
            )
        )


        fig2.update_layout(

            height=520,

            xaxis_title=(
                "Nombre d’exoplanètes"
            ),

            yaxis_title="",

            margin=dict(
                l=30,
                r=90,
                t=30,
                b=40
            ),

            plot_bgcolor="white",

            paper_bgcolor="white",

            font=dict(
                size=14
            )
        )


        fig2.update_xaxes(
            showgrid=True,
            gridcolor=GRILLE,
            rangemode="tozero"
        )


        fig2.update_yaxes(
            showgrid=False,
            autorange="reversed",
            automargin=True,

            tickfont=dict(
                size=17,
                color="#3E4A59"
            )
        )


        st.plotly_chart(
            fig2,
            use_container_width=True
        )


        # ----------------------------------------------------
        # EXPLICATIONS
        # ----------------------------------------------------

        with st.expander(
            "🌍 Comment lire le rayon d’une planète ?"
        ):

            st.markdown(
                """
                Le rayon correspond à la distance entre le centre
                d’une planète et sa surface.

                La Terre possède un rayon d’environ **6 371 km**.

                - une planète ayant **0,8 fois** le rayon terrestre
                  mesure environ **5 100 km de rayon** ;
                - **1,6 fois** le rayon terrestre correspond à environ
                  **10 200 km de rayon** ;
                - à forme comparable, une planète de 1,6 fois le rayon
                  terrestre possède déjà environ **4 fois le volume**
                  de la Terre.
                """
            )


        with st.expander(
            "🔎 Pourquoi utiliser 1,6 fois le rayon de la Terre comme repère ?"
        ):

            st.markdown(
                """
                Le rayon donne un premier indice sur la
                **composition probable** d’une planète.

                Les observations reliant la masse et le rayon
                des exoplanètes montrent qu’autour de
                **1,6 fois le rayon terrestre**, soit environ
                **10 200 km**, la probabilité qu’une planète soit
                principalement constituée de roche et de fer
                diminue fortement.

                Au-delà de cette taille, les planètes possèdent
                plus souvent une importante enveloppe de gaz
                ou de matériaux volatils.

                **Ce n’est pas une frontière absolue :**
                une petite planète n’est pas forcément rocheuse,
                et une planète rocheuse n’est pas forcément habitable.
                """
            )


        # ----------------------------------------------------
        # TRANSITION
        # ----------------------------------------------------

        st.success(
            "➡️ **Mais une taille proche de celle de la Terre ne suffit pas.** "
            "Une planète peut être rocheuse tout en étant beaucoup trop chaude "
            "ou trop fortement irradiée. L’étape suivante consiste donc "
            "à regarder l’énergie qu’elle reçoit de son étoile."
        )


# ============================================================
# PAGE 3 — CONDITIONS FAVORABLES
# ============================================================

elif page == 3:

    df_conditions = df_filtre.dropna(
        subset=[
            "pl_rade",
            "pl_insol"
        ]
    ).copy()


    df_conditions = df_conditions[
        df_conditions[
            "pl_insol"
        ] > 0
    ].copy()


    if df_conditions.empty:

        st.warning(
            "Aucune planète ne possède à la fois un rayon "
            "et une énergie reçue renseignés pour cette sélection."
        )


    else:

        # ----------------------------------------------------
        # CRITÈRES
        # ----------------------------------------------------

        df_conditions[
            "taille_compatible"
        ] = (
            df_conditions[
                "pl_rade"
            ]
            .between(
                RAYON_MIN,
                RAYON_MAX
            )
        )


        df_conditions[
            "energie_compatible"
        ] = (
            df_conditions[
                "pl_insol"
            ]
            .between(
                INSOLATION_MIN,
                INSOLATION_MAX
            )
        )


        df_conditions[
            "candidate"
        ] = (
            df_conditions[
                "taille_compatible"
            ]
            & df_conditions[
                "energie_compatible"
            ]
        )


        nb_documentees = len(
            df_conditions
        )


        nb_taille = int(
            df_conditions[
                "taille_compatible"
            ].sum()
        )


        nb_candidates = int(
            df_conditions[
                "candidate"
            ].sum()
        )


        part_taille = (
            nb_taille
            / nb_documentees
            * 100
        )


        part_candidates = (
            nb_candidates
            / nb_documentees
            * 100
        )


        nb_documentees_affiche = (
            f"{nb_documentees:,}"
            .replace(",", " ")
        )


        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        st.header(
            f"Sur {nb_documentees_affiche} planètes analysables, "
            f"seules {nb_candidates} combinent une petite taille "
            "et une énergie reçue proche de celle de la Terre"
        )


        st.caption(
            "Cette analyse porte uniquement sur les exoplanètes "
            "pour lesquelles le rayon et l’énergie reçue "
            "sont tous les deux renseignés."
        )


        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Rayon + énergie connus",
                nb_documentees_affiche,
                help=(
                    "Planètes pour lesquelles le rayon "
                    "et l'énergie reçue sont tous les deux disponibles."
                )
            )


        with col2:

            st.metric(
                label=(
                    f"Taille compatible · "
                    f"{part_taille:.0f} % des planètes analysables"
                ),
                value=(
                    f"{nb_taille:,}"
                    .replace(",", " ")
                )
            )


        with col3:

            st.metric(
                label=(
                    f"Taille + énergie compatibles · "
                    f"{part_candidates:.1f} % des planètes analysables"
                ).replace(".", ","),
                value=(
                    f"{nb_candidates:,}"
                    .replace(",", " ")
                )
            )


        # ----------------------------------------------------
        # GRAPHIQUE
        # ----------------------------------------------------

        st.markdown(
            "### Taille de la planète et énergie reçue"
        )


        df_conditions_zoom = df_conditions[
            df_conditions[
                "pl_insol"
            ].between(
                0.1,
                10
            )
            &
            df_conditions[
                "pl_rade"
            ].between(
                0,
                5
            )
        ].copy()


        nb_affichees = len(
            df_conditions_zoom
        )


        df_conditions_zoom[
            "distance_affiche"
        ] = df_conditions_zoom[
            "distance_ly"
        ].apply(
            lambda valeur: (
                "Non renseignée"
                if pd.isna(valeur)
                else f"{valeur:.0f} années-lumière"
            )
        )


        autres = df_conditions_zoom[
            ~df_conditions_zoom[
                "candidate"
            ]
        ].copy()


        candidates_graph = df_conditions_zoom[
            df_conditions_zoom[
                "candidate"
            ]
        ].copy()


        fig3 = go.Figure()


        # ----------------------------------------------------
        # ZONE DE PRÉSÉLECTION
        # ----------------------------------------------------

        fig3.add_shape(

            type="rect",

            x0=INSOLATION_MIN,

            x1=INSOLATION_MAX,

            y0=RAYON_MIN_KM,

            y1=RAYON_MAX_KM,

            fillcolor=BLEU_CLAIR,

            opacity=0.55,

            line=dict(
                color=BLEU,
                width=2,
                dash="dash"
            ),

            layer="below"
        )


        # ----------------------------------------------------
        # AUTRES EXOPLANÈTES
        # ----------------------------------------------------

        fig3.add_trace(

            go.Scatter(

                x=autres[
                    "pl_insol"
                ],

                y=autres[
                    "rayon_km"
                ],

                mode="markers",

                name="Autres exoplanètes",

                marker=dict(
                    size=9,
                    color=GRIS,
                    opacity=0.45
                ),

                text=autres[
                    "pl_name"
                ],

                customdata=np.stack(
                    [
                        autres[
                            "disc_year"
                        ],
                        autres[
                            "distance_affiche"
                        ]
                    ],
                    axis=-1
                ),

                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Année de découverte : %{customdata[0]:.0f}<br>"
                    "Rayon : %{y:,.0f} km<br>"
                    "Énergie reçue : %{x:.2f} × Terre<br>"
                    "Distance : %{customdata[1]}"
                    "<extra></extra>"
                )
            )
        )


        # ----------------------------------------------------
        # CANDIDATES
        # ----------------------------------------------------

        fig3.add_trace(

            go.Scatter(

                x=candidates_graph[
                    "pl_insol"
                ],

                y=candidates_graph[
                    "rayon_km"
                ],

                mode="markers",

                name="Candidates potentielles",

                marker=dict(
                    size=15,
                    color=BLEU_VIF,
                    line=dict(
                        width=1.8,
                        color=BLEU_FONCE
                    )
                ),

                text=candidates_graph[
                    "pl_name"
                ],

                customdata=np.stack(
                    [
                        candidates_graph[
                            "disc_year"
                        ],
                        candidates_graph[
                            "distance_affiche"
                        ]
                    ],
                    axis=-1
                ),

                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Année de découverte : %{customdata[0]:.0f}<br>"
                    "Rayon : %{y:,.0f} km<br>"
                    "Énergie reçue : %{x:.2f} × Terre<br>"
                    "Distance : %{customdata[1]}"
                    "<extra></extra>"
                )
            )
        )


        # ----------------------------------------------------
        # ANNOTATION ZONE
        # ----------------------------------------------------

        fig3.add_annotation(

            # Axe X logarithmique
            # log10(1) = 0

            x=0,

            y=(
                RAYON_MAX_KM
                + 1200
            ),

            xref="x",

            yref="y",

            text=(
                "<b>Zone de présélection</b>"
            ),

            showarrow=False,

            font=dict(
                color=BLEU_FONCE,
                size=13
            ),

            bgcolor=(
                "rgba(255,255,255,0.92)"
            ),

            bordercolor=BLEU,

            borderwidth=1,

            borderpad=4
        )


        # ----------------------------------------------------
        # TERRE — AJOUTÉE EN DERNIER POUR ÊTRE AU PREMIER PLAN
        # ----------------------------------------------------

        fig3.add_trace(

            go.Scatter(

                x=[1],

                y=[RAYON_TERRE_KM],

                mode="markers",

                name="Terre · repère",

                marker=dict(
                    size=32,
                    symbol="star",
                    color=TERRE,
                    line=dict(
                        width=3,
                        color="#111111"
                    )
                ),

                hovertemplate=(
                    "<b>Terre — point de comparaison</b><br>"
                    "Rayon : 6 371 km<br>"
                    "Énergie reçue : 1 × Terre<br>"
                    "La Terre n'est pas incluse dans "
                    "le dataset d'exoplanètes"
                    "<extra></extra>"
                )
            )
        )


        # ----------------------------------------------------
        # LIBELLÉ TERRE — CONTRASTE RENFORCÉ
        # ----------------------------------------------------

        fig3.add_annotation(

            # Axe X logarithmique :
            # log10(1) = 0
            x=0,

            y=4700,

            xref="x",

            yref="y",

            text="<b>Terre (repère)</b>",

            showarrow=False,

            font=dict(
                size=14,
                color="#111111"
            ),

            bgcolor="rgba(255,255,255,0.92)",

            bordercolor="#111111",

            borderwidth=1,

            borderpad=4
        )


        # ----------------------------------------------------
        # LAYOUT
        # ----------------------------------------------------

        fig3.update_layout(

            height=650,

            xaxis_title=(
                "Énergie reçue par rapport à la Terre "
                "(1 = Terre)"
            ),

            yaxis_title=(
                "Rayon de la planète (km)"
            ),

            hovermode="closest",

            margin=dict(
                l=30,
                r=30,
                t=60,
                b=50
            ),

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            ),

            plot_bgcolor="white",

            paper_bgcolor="white",

            font=dict(
                size=14
            )
        )


        fig3.update_xaxes(

            type="log",

            range=[
                -1,
                1
            ],

            tickmode="array",

            tickvals=[
                0.1,
                0.5,
                1,
                2,
                5,
                10
            ],

            ticktext=[
                "0,1",
                "0,5",
                "1",
                "2",
                "5",
                "10"
            ],

            showgrid=True,

            gridcolor=GRILLE,

            zeroline=False
        )


        fig3.update_yaxes(

            range=[
                0,
                5 * RAYON_TERRE_KM
            ],

            tickmode="array",

            tickvals=[
                0,
                5000,
                10000,
                15000,
                20000,
                25000,
                30000
            ],

            ticktext=[
                "0",
                "5 000",
                "10 000",
                "15 000",
                "20 000",
                "25 000",
                "30 000"
            ],

            showgrid=True,

            gridcolor=GRILLE,

            zeroline=False
        )


        st.plotly_chart(
            fig3,
            use_container_width=True
        )


        rayon_zoom_max = (
            5
            * RAYON_TERRE_KM
        )


        st.caption(
            (
                f"🔍 Le graphique zoome volontairement sur la zone "
                f"0,1–10 × l’énergie terrestre et "
                f"0–{rayon_zoom_max:,.0f} km de rayon afin de rendre "
                f"les conditions proches de celles de la Terre lisibles. "
                f"{nb_affichees} des {nb_documentees} planètes analysables "
                f"sont visibles dans cette fenêtre. "
                f"Les KPIs restent calculés sur l’ensemble "
                f"des {nb_documentees} planètes."
            )
            .replace(",", " ")
        )


        # ----------------------------------------------------
        # EXPLICATIONS
        # ----------------------------------------------------

        with st.expander(
            "☀️ Que signifie « énergie reçue × Terre » ?"
        ):

            st.markdown(
                """
                Cette valeur compare la quantité d'énergie reçue
                par une planète depuis son étoile à celle reçue
                par la Terre depuis le Soleil.

                - **1 × Terre** : environ autant d'énergie que la Terre ;
                - **0,5 × Terre** : environ deux fois moins ;
                - **2 × Terre** : environ deux fois plus.

                Cette valeur ne donne pas directement la température
                de surface. Une atmosphère, l'albédo ou d'autres
                phénomènes peuvent fortement modifier les conditions
                réelles de la planète.
                """
            )


        with st.expander(
            "🔎 Pourquoi retenir entre 0,5 et 2 × l’énergie terrestre ?"
        ):

            st.markdown(
                """
                Nous utilisons **0,5 à 2 fois l'énergie reçue par la Terre**
                comme une **fenêtre volontairement large de présélection**.

                Le but n'est pas d'affirmer qu'une planète comprise
                dans cette zone est habitable.

                Ce filtre sert simplement à écarter les mondes recevant
                des niveaux d'énergie très éloignés de ceux connus sur Terre.

                Une véritable étude de l'habitabilité devrait aussi prendre
                en compte le type d'étoile, l'atmosphère, l'albédo,
                la composition de la planète, la présence éventuelle
                d'eau liquide et d'autres paramètres.

                Il s'agit donc d'un **outil de présélection pédagogique**,
                et non d'une définition exacte de la zone habitable.
                """
            )


        # ----------------------------------------------------
        # TRANSITION
        # ----------------------------------------------------

        if nb_candidates == 1:

            texte_candidates = (
                "1 candidate reste"
            )

        else:

            texte_candidates = (
                f"{nb_candidates} candidates restent"
            )


        st.success(
            f"➡️ **En combinant nos deux critères, "
            f"{texte_candidates} dans la sélection.** "
            "La dernière étape consiste maintenant à voir "
            "quelles planètes elles sont."
        )


# ============================================================
# PAGE 4 — CANDIDATES
# ============================================================

elif page == 4:

    total_selection = len(
        df_filtre
    )


    # --------------------------------------------------------
    # PLANÈTES DOCUMENTÉES
    # --------------------------------------------------------

    base_candidates = df_filtre.dropna(
        subset=[
            "pl_rade",
            "pl_insol"
        ]
    ).copy()


    base_candidates = base_candidates[
        base_candidates[
            "pl_insol"
        ] > 0
    ].copy()


    # --------------------------------------------------------
    # ÉTAPE TAILLE
    # --------------------------------------------------------

    apres_rayon = base_candidates[
        base_candidates[
            "pl_rade"
        ]
        .between(
            RAYON_MIN,
            RAYON_MAX
        )
    ].copy()


    # --------------------------------------------------------
    # ÉTAPE ÉNERGIE
    # --------------------------------------------------------

    candidates = apres_rayon[
        apres_rayon[
            "pl_insol"
        ]
        .between(
            INSOLATION_MIN,
            INSOLATION_MAX
        )
    ].copy()


    nb_documentees = len(
        base_candidates
    )


    nb_candidates = len(
        candidates
    )


    if nb_documentees > 0:

        part_candidates = (
            nb_candidates
            / nb_documentees
            * 100
        )

    else:

        part_candidates = 0


    # --------------------------------------------------------
    # FORMATAGE
    # --------------------------------------------------------

    total_selection_affiche = (
        f"{total_selection:,}"
        .replace(",", " ")
    )


    nb_documentees_affiche = (
        f"{nb_documentees:,}"
        .replace(",", " ")
    )


    nb_candidates_affiche = (
        f"{nb_candidates:,}"
        .replace(",", " ")
    )


    # --------------------------------------------------------
    # CANDIDATE LA PLUS PROCHE
    # --------------------------------------------------------

    candidates_distance = candidates[
        candidates[
            "distance_ly"
        ].notna()
    ].copy()


    if not candidates_distance.empty:

        plus_proche = (
            candidates_distance
            .sort_values(
                "distance_ly"
            )
            .iloc[0]
        )

        nom_plus_proche = (
            plus_proche[
                "pl_name"
            ]
        )

        distance_plus_proche = (
            plus_proche[
                "distance_ly"
            ]
        )

    else:

        nom_plus_proche = (
            "Non renseignée"
        )

        distance_plus_proche = None


    # --------------------------------------------------------
    # INTRODUCTION PLUS DISCRÈTE
    # --------------------------------------------------------

    if nb_candidates > 0:

        mot_monde = (
            "monde"
            if nb_candidates == 1
            else "mondes"
        )

        verbe_rester = (
            "reste"
            if nb_candidates == 1
            else "restent"
        )

        st.markdown(
            f"#### Après notre présélection, "
            f"{nb_candidates_affiche} "
            f"{mot_monde} {verbe_rester} parmi "
            f"{nb_documentees_affiche} planètes "
            "suffisamment documentées"
        )


    else:

        st.markdown(
            "### Aucune planète ne remplit simultanément "
            "les deux critères dans la sélection actuelle"
        )


    st.caption(
        "Le passage de toutes les exoplanètes aux candidates "
        "distingue les données manquantes des critères physiques "
        "utilisés pour notre présélection."
    )


    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Candidates potentielles",
            nb_candidates_affiche,
            help=(
                "Planètes ayant un rayon compris entre environ "
                "3 200 et 10 200 km et recevant entre "
                "0,5 et 2 fois l'énergie reçue par la Terre."
            )
        )


    with col2:

        st.metric(
            label=(
                f"Part des planètes analysables · "
                f"{nb_candidates_affiche} sur "
                f"{nb_documentees_affiche}"
            ),
            value=(
                f"{part_candidates:.1f} %"
                .replace(".", ",")
            )
        )


    with col3:

        if distance_plus_proche is not None:

            st.metric(
                label=(
                    "Candidate connue la plus proche · "
                    f"{distance_plus_proche:.0f} années-lumière"
                ),
                value=nom_plus_proche
            )

        else:

            st.metric(
                "Candidate connue la plus proche",
                "Distance inconnue"
            )


    # --------------------------------------------------------
    # ENTONNOIR
    # --------------------------------------------------------

    st.markdown(
        "### De toutes les découvertes aux candidates potentielles"
    )


    etapes = [
        "Exoplanètes dans la sélection",
        "Rayon + énergie connus",
        "Rayon entre 3 200 et 10 200 km",
        "Taille + énergie compatibles"
    ]


    valeurs = [
        total_selection,
        nb_documentees,
        len(apres_rayon),
        nb_candidates
    ]


    fig4 = go.Figure(

        go.Funnel(

            y=etapes,

            x=valeurs,

            textinfo="value",

            marker=dict(
                color=[
                    "#C9D3DE",
                    "#9FB7CF",
                    "#5FA8E8",
                    BLEU
                ]
            ),

            connector=dict(
                line=dict(
                    color="#D7E1EA",
                    width=1
                )
            ),

            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x} planète(s)"
                "<extra></extra>"
            )
        )
    )


    fig4.update_layout(

        height=500,

        margin=dict(
            l=40,
            r=40,
            t=20,
            b=30
        ),

        paper_bgcolor="white",

        font=dict(
            size=14
        )
    )

    fig4.update_yaxes(
        automargin=True,

        tickfont=dict(
            size=17,
            color="#3E4A59"
        )
    )


    st.plotly_chart(
        fig4,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ATTENTION DONNÉES MANQUANTES
    # --------------------------------------------------------

    mot_documentee = (
        "planète"
        if nb_documentees == 1
        else "planètes"
    )


    st.info(
        "🔎 **Attention à l’interprétation de l’entonnoir :** "
        f"le passage de {total_selection_affiche} à "
        f"{nb_documentees_affiche} {mot_documentee} "
        "ne signifie pas que toutes les autres ont été jugées "
        "défavorables. Elles sont principalement exclues "
        "de cette analyse parce que leur rayon ou leur énergie "
        "reçue ne sont pas renseignés."
    )


    # --------------------------------------------------------
    # TABLEAU
    # --------------------------------------------------------

    st.markdown(
        "### Les mondes qui restent"
    )


    if candidates.empty:

        st.warning(
            "Aucune candidate ne correspond aux filtres actuels. "
            "Élargis l’année de fin, les méthodes de découverte "
            "ou la distance maximale."
        )


    else:

        tableau_candidates = candidates[
            [
                "pl_name",
                "disc_year",
                "methode_groupe",
                "rayon_km",
                "pl_insol",
                "pl_eqt",
                "distance_ly"
            ]
        ].copy()


        tableau_candidates = (
            tableau_candidates
            .sort_values(
                "distance_ly",
                na_position="last"
            )
        )


        tableau_candidates.columns = [
            "Planète",
            "Découverte",
            "Méthode",
            "Rayon (km)",
            "Énergie reçue (× Terre)",
            "Température d’équilibre (K)",
            "Distance (années-lumière)"
        ]


        tableau_candidates[
            "Température d’équilibre (K)"
        ] = tableau_candidates[
            "Température d’équilibre (K)"
        ].apply(
            lambda valeur: (
                "Non renseignée"
                if pd.isna(valeur)
                else f"{valeur:.0f}"
            )
        )


        tableau_candidates[
            "Distance (années-lumière)"
        ] = tableau_candidates[
            "Distance (années-lumière)"
        ].apply(
            lambda valeur: (
                "Non renseignée"
                if pd.isna(valeur)
                else f"{valeur:.1f}"
            )
        )


        st.dataframe(

            tableau_candidates,

            use_container_width=True,

            hide_index=True,

            column_config={

                "Découverte":
                    st.column_config.NumberColumn(
                        format="%d"
                    ),

                "Rayon (km)":
                    st.column_config.NumberColumn(
                        format="%.0f"
                    ),

                "Énergie reçue (× Terre)":
                    st.column_config.NumberColumn(
                        format="%.2f"
                    )
            }
        )


        # ----------------------------------------------------
        # EXPLICATIONS
        # ----------------------------------------------------

        with st.expander(
            "🪐 Pourquoi les appeler « candidates potentielles » ?"
        ):

            st.markdown(
                """
                Les planètes affichées ici remplissent uniquement
                **deux critères simples** :

                - un rayon compris entre environ **3 200 et 10 200 km**
                  (0,5 à 1,6 fois le rayon de la Terre) ;
                - une énergie reçue comprise entre **0,5 et 2 fois**
                  celle reçue par la Terre.

                Cela permet d'identifier des mondes présentant certaines
                caractéristiques intéressantes, mais **cela ne prouve pas
                qu'ils sont habitables**.

                Nous ne disposons pas ici d'informations suffisantes
                sur leur atmosphère, la présence réelle d'eau liquide,
                la composition exacte de leur surface, leur activité
                géologique, leur champ magnétique ou la présence éventuelle
                de molécules associées à la vie.

                Le terme **candidate potentielle** signifie donc simplement :
                *planète intéressante à étudier davantage selon les données
                disponibles dans ce projet.*
                """
            )


        with st.expander(
            "📏 Pourquoi regarder aussi la distance ?"
        ):

            st.markdown(
                """
                La distance ne détermine pas si une planète est habitable.

                Elle permet cependant de répondre à une question intuitive :
                **parmi nos candidates, lesquelles sont les plus proches
                de la Terre ?**

                Une candidate plus proche peut également être plus accessible
                à certaines observations astronomiques détaillées qu'un monde
                situé à plusieurs centaines d'années-lumière.

                Dans ce dashboard, la distance sert donc uniquement
                de **contexte supplémentaire** et non de critère
                d'habitabilité.
                """
            )


        # ----------------------------------------------------
        # CONCLUSION
        # ----------------------------------------------------

        mot_planete = (
            "planète"
            if nb_candidates == 1
            else "planètes"
        )


        verbe_reunir = (
            "réunit"
            if nb_candidates == 1
            else "réunissent"
        )


        st.success(
            f"🌍 **Conclusion de notre présélection :** "
            f"{nb_candidates_affiche} {mot_planete} "
            "de la sélection actuelle "
            f"{verbe_reunir} nos deux critères physiques simplifiés. "
            "Ces mondes sont intéressants à examiner davantage, "
            "mais aucun ne peut être déclaré habitable "
            "à partir de ces seules données."
        )

        # ----------------------------------------------------
        # PAGE BONUS
        # ----------------------------------------------------

        st.markdown(
            "<div style='height: 10px;'></div>",
            unsafe_allow_html=True
        )


        bonus_col1, bonus_col2, bonus_col3 = st.columns(
            [
                1,
                2,
                1
            ]
        )


        with bonus_col2:

            if st.button(
                "🔭 Pour aller plus loin sur les candidates",
                key="ouvrir_page_bonus",
                type="secondary",
                use_container_width=True
            ):

                st.switch_page(
                    "pages/5_Pour_aller_plus_loin.py"
                )

# ============================================================
# MÉTHODOLOGIE / SOURCE
# ============================================================

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