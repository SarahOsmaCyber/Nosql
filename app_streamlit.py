import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title=" Dashboard Inventaire", layout="wide")
API_URL = "http://127.0.0.1:8000"

CATEGORIES = {
    "cat001": "Périphériques",
    "cat002": "Composants",
    "cat003": "Réseau",
    "cat004": "Stockage"
}


def afficher_table(endpoint):
    try:
        r = requests.get(f"{API_URL}{endpoint}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                for row in data:
                    with st.container(border=True):
                        st.markdown(f"###  {row['_id']} - {row['name']}")
                        st.write(f"**Description** : {row.get('description', '-')}")
                        st.write(f"**Prix** : {row['price']} €")
                        st.write(f"**Stock** : {row['quantity_in_stock']} unités")
                        st.write(f"**Statut** : `{row['status']}`")
                        cat_label = CATEGORIES.get(row['category_id'], row['category_id'])
                        st.write(f"**Catégorie** : {cat_label}")
                        st.write(f"📅 **Ajouté le** : {row['date_added']}")

                        if st.button("Supprimer ce produit", key=f"del_{row['_id']}"):
                            res = requests.delete(f"{API_URL}/supprimer-produit/{row['_id']}")
                            if res.status_code == 200:
                                st.success("Produit supprimé ")
                                st.rerun()
                            else:
                                st.error("Erreur de suppression ")
            else:
                st.info("Aucun produit trouvé.")
        else:
            st.error(f"Erreur API : {r.status_code}")
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")


onglet = st.selectbox("Page :", ["Inventaire", "Valeur du stock"])

if onglet == "Inventaire":
    st.title(" Gestion des Stocks")

    with st.expander(" Ajouter un produit"):
        with st.form("form_ajout"):
            
            id_res = requests.get(f"{API_URL}/last-product-id")
            produit_id = id_res.json().get("next_id") if id_res.status_code == 200 else "prodXXX"

            nom = st.text_input("Nom")
            description = st.text_area("Description")
            prix = st.number_input("Prix (€)", min_value=0.0, step=0.01)
            quantite = st.number_input("Quantité en stock", min_value=0, step=1)
            categorie_nom = st.selectbox("Catégorie", list(CATEGORIES.values()))
            categorie = [k for k, v in CATEGORIES.items() if v == categorie_nom][0]

            submitted = st.form_submit_button("Ajouter")
            if submitted:
                new_product = {
                    "_id": produit_id,
                    "type": "product",
                    "name": nom,
                    "description": description,
                    "price": prix,
                    "quantity_in_stock": quantite,
                    "category_id": categorie,
                    "date_added": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "status": "in_stock" if quantite > 10 else "low_stock" if quantite > 0 else "out_of_stock"
                }
                res = requests.post(f"{API_URL}/ajouter-produit", json=new_product)
                if res.status_code == 200:
                    st.success("Produit ajouté avec succès ")
                    st.rerun()
                else:
                    st.error("Erreur d'ajout ")

    filtre = st.selectbox(" Filtrer :", [
        "Tous les produits", "Stock faible", "Rupture", "Par catégorie"
    ])
    if filtre == "Tous les produits":
        afficher_table("/produits-en-stock")
    elif filtre == "Stock faible":
        afficher_table("/stock-faible")
    elif filtre == "Rupture":
        afficher_table("/rupture-stock")
    elif filtre == "Par catégorie":
        categorie_id = st.selectbox("Catégorie", ["cat001", "cat002", "cat003", "cat004"])
        afficher_table(f"/produits-par-categorie?categorie_id={categorie_id}")

elif onglet == "Valeur du stock":
    st.title(" Valeur du Stock")
    r = requests.get(f"{API_URL}/valeur-totale-stock")
    if r.status_code == 200:
        total = r.json().get("total", 0)
        st.metric(" Valeur totale", f"{total:.2f} €")

    data = requests.get(f"{API_URL}/produits-en-stock")
    if data.status_code == 200:
        produits = pd.DataFrame(data.json())
        if not produits.empty:
            produits["valeur"] = produits["price"] * produits["quantity_in_stock"]
            valeurs = produits.groupby("category_id")["valeur"].sum().reset_index()
            st.dataframe(valeurs, use_container_width=True)
        else:
            st.info("Aucun produit.")
