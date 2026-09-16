# Cadrage — À la recherche de mondes potentiellement habitables

## Public cible

Ce dashboard s’adresse au **grand public curieux d’astronomie**, sans connaissance scientifique particulière.

L’objectif est donc de privilégier une lecture simple : comparaison avec la Terre, distances en années-lumière et rayons exprimés en kilomètres plutôt qu’en unités scientifiques seules.

## Question et message principal

**Question :** parmi les milliers d’exoplanètes découvertes, combien présentent certaines caractéristiques physiques proches de celles de la Terre ?

**Message principal :** parmi les milliers d’exoplanètes découvertes, seule une petite fraction des planètes suffisamment documentées réunit simultanément des caractéristiques physiques compatibles avec une habitabilité potentielle.

Il s’agit d’une **présélection pédagogique**, et non d’une preuve d’habitabilité.

## Storytelling

Le dashboard suit une progression en quatre étapes :

1. **Découvertes** — montrer comment les découvertes d’exoplanètes ont fortement augmenté depuis 1992, notamment avec la mission Kepler.
2. **Diversité** — montrer que les exoplanètes découvertes présentent des tailles très variées et que la majorité ne ressemble pas à la Terre.
3. **Conditions favorables** — croiser le rayon et l’énergie reçue afin d’identifier les planètes correspondant à deux critères simplifiés.
4. **Candidates** — présenter l’entonnoir de sélection et identifier les mondes qui restent.

Une page complémentaire **« Pour aller plus loin »** approfondit ensuite les candidates retenues : distance, disponibilité des données et caractéristiques individuelles.

## Choix de visualisation

- **Courbe temporelle** pour montrer l’évolution des découvertes.
- **Barres horizontales** pour comparer les catégories de taille.
- **Nuage de points** pour croiser rayon et énergie reçue, avec la Terre comme repère visuel.
- **Entonnoir** pour montrer la réduction progressive de la population étudiée.
- **Barres et fiches interactives** dans la page complémentaire pour approfondir les candidates.

Les titres sont formulés comme des **messages** plutôt que comme de simples noms de graphiques.

## Critères de présélection

Une candidate potentielle est définie ici comme une planète :

- ayant un rayon compris entre **0,5 et 1,6 fois celui de la Terre**, soit environ **3 200 à 10 200 km** ;
- recevant entre **0,5 et 2 fois l’énergie reçue par la Terre**.

Ces seuils servent uniquement à réduire le champ d’étude.

## Interactivité

Le dashboard permet de filtrer :

- l’année maximale de découverte, à partir de **1992** ;
- la méthode de découverte : **Transit**, **Vitesse radiale** ou **Autres** ;
- éventuellement la distance maximale à la Terre.

Les KPIs et visualisations sont recalculés automatiquement selon les filtres.

## Source et limites

**Source : NASA Exoplanet Archive.**

Une seule ligne de référence est conservée par planète avec `default_flag = 1`.

Le rayon et l’énergie reçue ne suffisent pas à déterminer l’habitabilité réelle. L’atmosphère, la composition, l’eau liquide, le type d’étoile ou encore l’activité géologique devraient notamment être étudiés pour aller plus loin.

**Dashboard :** https://exoplanet-dataviz-dashboard.streamlit.app