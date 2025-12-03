# HACKATHON
Hackathon de la team winner 
L'objectif du dépot de CETTE BRANCHE (main)est de calculer l'indice ICU (ilot de chaleur urbain) sur la région parisienne pour une période de 10 ans. On s'est servi des bases de données anastasia.
L'autre branche "imane-branch" construit une grille 1 km sur l'Île-de-France et fusionne
plusieurs sources : - LCZ (Local Climate Zones) - INSEE (carroyage200 m) - OpenStreetMap POI - Distances aux aménités -Indicateurs sociaux - Indice de vulnérabilité.Il produit ensuite un GeoJSON exploitable et une application Streamlit
interactive.
Pour la branche main
Le fichier central est main.py pour le lancer il faut télécharger les bibliothèque du require.
Le fichier main produit des cartes moyennées sur toutes les périodes de 10 ans de l'indice ICU .

