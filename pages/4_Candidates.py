# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# PAGE 4 — CANDIDATES
# ============================================================

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (
    BLEU,
    INSOLATION_MAX,
    INSOLATION_MIN,
    RAYON_MAX,
    RAYON_MIN,
    charger_donnees,
    footer,
    inject_style,
    nav,
    sidebar_filters
)


st.set_page_config(
    page_title="Candidates · Exoplanètes",
    page_icon="🪐",
    layout="wide"
)


inject_style()


df = charger_donnees()


df_filtre, methodes_selectionnees = sidebar_filters(df)


nav("pages/4_Candidates.py")


st.divider()


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


footer()
