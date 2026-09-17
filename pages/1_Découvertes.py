# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# PAGE 1 — HISTOIRE DES DÉCOUVERTES
# ============================================================

import plotly.graph_objects as go
import streamlit as st

from utils import (
    BLEU,
    BLEU_FONCE,
    BLEU_VIF,
    GRILLE,
    charger_donnees,
    footer,
    inject_style,
    nav,
    sidebar_filters
)


st.set_page_config(
    page_title="Découvertes · Exoplanètes",
    page_icon="🛰️",
    layout="wide"
)


inject_style()


df = charger_donnees()


df_filtre, methodes_selectionnees = sidebar_filters(df)


nav("pages/1_Découvertes.py")


st.divider()


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


footer()
