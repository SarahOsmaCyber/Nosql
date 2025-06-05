from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime, timedelta
from fastapi import Body
from bson import ObjectId
from fastapi import Body, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["Projet"]
collection = db["inventaire"]

from datetime import datetime

def convertir_document(doc):
    doc["_id"] = str(doc["_id"])
    if "date_added" in doc and doc["date_added"]:
        if isinstance(doc["date_added"], datetime):
            doc["date_added"] = doc["date_added"].strftime("%Y-%m-%d")
        elif isinstance(doc["date_added"], str):
            try:
                parsed_date = datetime.fromisoformat(doc["date_added"])
                doc["date_added"] = parsed_date.strftime("%Y-%m-%d")
            except:
                doc["date_added"] = doc["date_added"]  
    return doc

# Routes

@app.get("/categories")
def get_categories():
    return list(collection.find({ "type": "category" }, { "_id": 1, "name": 1 }))

@app.get("/produits-en-stock")
def produits_en_stock():
    produits = collection.find({ "type": "product", "quantity_in_stock": { "$gt": 0 } })
    return [convertir_document(p) for p in produits]

@app.get("/stock-faible")
def stock_faible():
    produits = collection.find({ "type": "product", "quantity_in_stock": { "$lt": 10, "$gt": 0 } })
    return [convertir_document(p) for p in produits]

@app.get("/rupture-stock")
def rupture_stock():
    produits = collection.find({ "type": "product", "quantity_in_stock": 0 })
    return [convertir_document(p) for p in produits]

@app.get("/produits-recents")
def produits_recents():
    date_limite = datetime.utcnow() - timedelta(days=7)
    produits = collection.find({ "type": "product", "date_added": { "$gte": date_limite } })
    return [convertir_document(p) for p in produits]

@app.get("/valeur-totale-stock")
def valeur_totale_stock():
    pipeline = [
        { "$match": { "type": "product" } },
        { "$project": { "valeur": { "$multiply": ["$price", "$quantity_in_stock"] } } },
        { "$group": { "_id": None, "total": { "$sum": "$valeur" } } }
    ]
    result = list(collection.aggregate(pipeline))
    return result[0] if result else { "total": 0 }

@app.get("/produits-par-categorie")
def produits_par_categorie(categorie_id: str):
    produits = collection.find({ "type": "product", "category_id": categorie_id })
    return [convertir_document(p) for p in produits]

@app.get("/produit-par-nom")
def produit_par_nom(nom: str):
    produits = collection.find({ "type": "product", "name": { "$regex": nom, "$options": "i" } })
    return [convertir_document(p) for p in produits]

@app.get("/compte-produits-par-categorie")
def count_par_categorie():
    pipeline = [
        { "$match": { "type": "product" } },
        { "$group": { "_id": "$category_id", "total": { "$sum": 1 } } }
    ]
    return list(collection.aggregate(pipeline))

@app.get("/produits-par-statut")
def produits_par_statut(stat: str):
    produits = collection.find({ "type": "product", "status": stat })
    return [convertir_document(p) for p in produits]

@app.post("/ajouter-produit")
async def ajouter_produit(data: dict = Body(...)):
    if "_id" not in data:
        raise HTTPException(status_code=400, detail="ID manquant")
    collection.insert_one(data)
    return {"message": "Produit ajouté avec succès"}



@app.get("/last-product-id")
def get_next_product_id():
    last = collection.find({"type": "product", "_id": {"$regex": "^prod\\d{3}$"}}).sort("_id", -1).limit(1)
    for doc in last:
        number = int(doc["_id"][4:])
        return {"next_id": f"prod{number + 1:03d}"}
    return {"next_id": "prod001"}


@app.delete("/supprimer-produit/{product_id}")
def supprimer_produit(product_id: str):
    result = collection.delete_one({
        "$or": [
            { "_id": product_id },
            { "_id": ObjectId(product_id) }
        ]
    })
    if result.deleted_count == 1:
        return {"message": "Produit supprimé"}
    raise HTTPException(status_code=404, detail="Produit non trouvé")
