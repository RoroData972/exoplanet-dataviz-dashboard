# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# PAGE 2 — DIVERSITÉ DES TAILLES
# ============================================================

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils import (
    BLEU,
    GRILLE,
    GRIS,
    RAYON_MAX,
    RAYON_TERRE_KM,
    charger_donnees,
    footer,
    inject_style,
    nav,
    sidebar_filters
)


st.set_page_config(
    page_title="Diversité · Exoplanètes",
    page_icon="🌐",
    layout="wide"
)


inject_style()


df = charger_donnees()


df_filtre, methodes_selectionnees = sidebar_filters(df)


nav("pages/2_Diversité.py")


st.divider()


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


footer()
