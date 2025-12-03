# HACKATHON -- LCZ × INSEE × OSM × Vulnerability Index

Ce projet construit une grille 1 km sur l'Île-de-France et fusionne
plusieurs sources : - **LCZ (Local Climate Zones)** - **INSEE (carroyage
200 m)** - **OpenStreetMap POI** - **Distances aux aménités** -
**Indicateurs sociaux** - **Indice de vulnérabilité**

Il produit ensuite un GeoJSON exploitable et une application Streamlit
interactive.

------------------------------------------------------------------------

## 1. Installation de l'environnement

``` bash
python3 -m venv hackathon
source hackathon/bin/activate
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 2. Données nécessaires

Toutes les données doivent être placées dans :

    /data/

### LCZ

    /lcz_paris/LCZ_SPOT_2022_Paris.shp

### INSEE Carroyage 200 m

    /data/insee/carroyage_insee_metro.csv

### OSM (points d'intérêt)

    /data/gis_osm_pois_a_free_1.shp

------------------------------------------------------------------------

## 3. Pipeline de préparation des données

Exécuter **dans cet ordre** :

### Fusion LCZ × OSM

``` bash
python fusion_data/fusion_data.py
```

### Agrégation en grille 1 km

``` bash
python fusion_data/aggregate_1km.py
```

### Insertion INSEE (social)

``` bash
python fusion_data/insertion_insee.py
```

### Création du GeoJSON

``` bash
python fusion_data/create_geojson_from_table.py
```

### Nettoyage du nom des colonnes du GeoJSON

``` bash
python fusion_data/clean_geojson.py
```

### Ajout des colonnes sociales (prop_elderly, prop_low_income)

``` bash
python fusion_data/clean_geojson_social.py
```

------------------------------------------------------------------------

## 4. Pipeline indicateur (indicator/)

Le dossier `indicator/` produit un indice de vulnérabilité et une carte
PNG.

### A. Calcul de l'indicateur

``` bash
python indicator/create_indicator.py
```

### B. Génération GeoJSON indicateur

``` bash
python indicator/clean_geojson_indicateur.py
```

### C. Export d'une carte PNG

``` bash
python indicator/map.py
```

------------------------------------------------------------------------

## 5. Visualisation Streamlit

Lancer l'interface interactive :

``` bash
streamlit run main.py
```

Elle contient : - Carte LCZ - Carte des distances - Carte sociale -
Carte de vulnérabilité (optionnelle)

------------------------------------------------------------------------

## 6. Structure du projet

    HACKATHON/
    ├── data/
    ├── fusion_data/
    ├── indicator/
    ├── main.py
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 🎯 Fin du pipeline

Vous disposez maintenant : - du GeoJSON propre - des indicateurs LCZ ×
INSEE × OSM - de l'indice de vulnérabilité - des cartes interactives
Streamlit - d'une carte PNG exportable

------------------------------------------------------------------------


