# ============================================================
# TP DATAVIZ · EXOPLANÈTES
# PAGE SYNTHÈSE — Dashboard Streamlit — Grand public
# ============================================================

import streamlit as st

from utils import (
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


# ============================================================
# CONFIGURATION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="À la recherche de mondes potentiellement habitables",
    page_icon="🪐",
    layout="wide"
)


inject_style()


df = charger_donnees()


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

df_filtre, methodes_selectionnees = sidebar_filters(df)


nav("app.py")


st.divider()


# ============================================================
# CANDIDATES — SÉLECTION ET CATALOGUE COMPLET
# Même présélection que dans les pages 3 et 4
# ============================================================

def compter_candidates(donnees):

    documentees = donnees.dropna(
        subset=[
            "pl_rade",
            "pl_insol"
        ]
    ).copy()

    documentees = documentees[
        documentees["pl_insol"] > 0
    ].copy()

    candidates = documentees[
        documentees["pl_rade"]
        .between(
            RAYON_MIN,
            RAYON_MAX
        )
        &
        documentees["pl_insol"]
        .between(
            INSOLATION_MIN,
            INSOLATION_MAX
        )
    ].copy()

    return documentees, candidates


def candidate_plus_proche(candidates):

    avec_distance = candidates[
        candidates["distance_ly"].notna()
    ]

    if avec_distance.empty:

        return None

    return (
        avec_distance
        .sort_values("distance_ly")
        .iloc[0]
    )


documentees_selection, candidates_selection = compter_candidates(
    df_filtre
)

documentees_catalogue, candidates_catalogue = compter_candidates(
    df
)


total_selection = len(df_filtre)
total_catalogue = len(df)

nb_documentees_selection = len(documentees_selection)

nb_candidates_selection = len(candidates_selection)
nb_candidates_catalogue = len(candidates_catalogue)


if nb_documentees_selection > 0:

    part_candidates_selection = (
        nb_candidates_selection
        / nb_documentees_selection
        * 100
    )

else:

    part_candidates_selection = 0


part_candidates_catalogue = (
    nb_candidates_catalogue
    / len(documentees_catalogue)
    * 100
)


proche_selection = candidate_plus_proche(
    candidates_selection
)

proche_catalogue = candidate_plus_proche(
    candidates_catalogue
)


# ============================================================
# FORMATAGE
# ============================================================

total_selection_affiche = (
    f"{total_selection:,}"
    .replace(",", " ")
)

total_catalogue_affiche = (
    f"{total_catalogue:,}"
    .replace(",", " ")
)

nb_documentees_selection_affiche = (
    f"{nb_documentees_selection:,}"
    .replace(",", " ")
)

nb_candidates_selection_affiche = (
    f"{nb_candidates_selection:,}"
    .replace(",", " ")
)


# ============================================================
# TITRE-MESSAGE
# ============================================================

if nb_candidates_selection == 0:

    st.header(
        "Aucune planète de la sélection actuelle ne réunit "
        "une taille et une énergie reçue proches de celles de la Terre"
    )

else:

    verbe_reunir = (
        "réunit"
        if nb_candidates_selection == 1
        else "réunissent"
    )

    st.header(
        f"Sur {total_selection_affiche} exoplanètes sélectionnées, "
        f"seules {nb_candidates_selection_affiche} {verbe_reunir} "
        "une taille et une énergie reçue proches de celles de la Terre"
    )


st.caption(
    "Chaque indicateur compare la sélection actuelle "
    "au catalogue complet, sans aucun filtre."
)


# ============================================================
# KPIs
# ============================================================

col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# KPI 1 — TAILLE DE LA SÉLECTION
# ------------------------------------------------------------

with col1:

    ecart_selection = (
        total_selection
        - total_catalogue
    )

    st.metric(
        label=(
            f"Exoplanètes dans la sélection · "
            f"{total_catalogue_affiche} au catalogue complet"
        ),
        value=total_selection_affiche,
        delta=(
            None
            if ecart_selection == 0
            else (
                f"{ecart_selection:,}"
                .replace(",", " ")
                + " vs catalogue complet"
            )
        ),
        delta_color="off"
    )


# ------------------------------------------------------------
# KPI 2 — PART DE CANDIDATES
# ------------------------------------------------------------

with col2:

    ecart_part = (
        part_candidates_selection
        - part_candidates_catalogue
    )

    st.metric(
        label=(
            f"Candidates potentielles · "
            f"{part_candidates_selection:.1f} % des "
            f"{nb_documentees_selection_affiche} planètes analysables"
        ).replace(".", ","),
        value=nb_candidates_selection_affiche,
        delta=(
            None
            if round(ecart_part, 1) == 0
            else (
                f"{ecart_part:+.1f} pts vs "
                f"{part_candidates_catalogue:.1f} % au catalogue complet"
            ).replace(".", ",")
        ),
        help=(
            "Planètes ayant un rayon compris entre environ "
            "3 200 et 10 200 km et recevant entre "
            "0,5 et 2 fois l'énergie reçue par la Terre. "
            "La part est calculée sur les planètes dont le rayon "
            "et l'énergie reçue sont tous les deux renseignés."
        )
    )


# ------------------------------------------------------------
# KPI 3 — CANDIDATE LA PLUS PROCHE
# ------------------------------------------------------------

with col3:

    if proche_selection is None:

        st.metric(
            "Candidate connue la plus proche",
            "Distance inconnue"
        )

    else:

        ecart_distance = (
            proche_selection["distance_ly"]
            - proche_catalogue["distance_ly"]
        )

        st.metric(
            label=(
                "Candidate connue la plus proche · "
                f"{proche_selection['distance_ly']:.0f} années-lumière"
            ),
            value=proche_selection["pl_name"],
            delta=(
                None
                if round(ecart_distance) == 0
                else (
                    f"{ecart_distance:+,.0f} années-lumière vs "
                    f"{proche_catalogue['pl_name']}"
                ).replace(",", " ")
            ),
            delta_color="inverse",
            help=(
                "Comparée à la candidate la plus proche "
                "du catalogue complet. Plus la distance est faible, "
                "plus le monde est proche de nous."
            )
        )


footer()
