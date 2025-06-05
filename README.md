Projet NoSQL - Gestion d'inventaire

Ce projet est une mini-application de gestion de stock pour un entrepôt de matériel informatique. 

Il utilise :
-  MongoDB (NoSQL) pour stocker les données  
-  FastAPI pour créer une API REST  
-  Streamlit pour l’interface web

 Fonctionnalités

- Ajout d’un produit avec :
  - ID auto-incrémenté (`prod001`, `prod002`, etc.)
  - Nom, description, prix, stock, catégorie
- Affichage clair des produits (type fiche)
- Suppression de produit 
- Visualisation de la valeur totale du stock et par catégorie
- Catégories affichées avec des noms lisibles :
  - `Périphériques`, `Composants`, `Réseau`, `Stockage`


Commandes de lancement
Lancer FastAPI (backend)

uvicorn main:app --reload

Lancer Streamlit (interface web)
streamlit run app_streamlit.py
