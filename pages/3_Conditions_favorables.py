# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# PAGE 3 — CONDITIONS FAVORABLES
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (
    BLEU,
    BLEU_CLAIR,
    BLEU_FONCE,
    BLEU_VIF,
    GRILLE,
    GRIS,
    INSOLATION_MAX,
    INSOLATION_MIN,
    RAYON_MAX,
    RAYON_MAX_KM,
    RAYON_MIN,
    RAYON_MIN_KM,
    RAYON_TERRE_KM,
    TERRE,
    charger_donnees,
    footer,
    inject_style,
    nav,
    sidebar_filters
)


st.set_page_config(
    page_title="Conditions favorables · Exoplanètes",
    page_icon="☀️",
    layout="wide"
)


inject_style()


df = charger_donnees()


df_filtre, methodes_selectionnees = sidebar_filters(df)


nav("pages/3_Conditions_favorables.py")


st.divider()


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


footer()
