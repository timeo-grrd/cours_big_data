#!/usr/bin/env python3
"""Collecte pédagogique des ressources DummyJSON et normalisation e-commerce."""
from pathlib import Path
from datetime import datetime, timedelta
import json, time, random, sys
import requests
import pandas as pd

BASE = "https://dummyjson.com"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RESOURCES = {
    "products": "products",
    "carts": "carts",
    "users": "users",
    "posts": "posts",
    "comments": "comments",
    "recipes": "recipes",
    "quotes": "quotes",
    "todos": "todos",
}

def get_json(url, timeout=40):
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()

def fetch_all(resource):
    # DummyJSON documente limit=0 pour demander tous les éléments.
    payload = get_json(f"{BASE}/{resource}?limit=0")
    key = resource
    if key not in payload:
        raise ValueError(f"Réponse inattendue pour {resource}: clé '{key}' absente")
    return payload

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": BASE,
        "collected_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "note": "Instantané API. Les dates order_date des tables dérivées sont synthétiques et générées pour l'exercice.",
        "resources": {}
    }
    data = {}
    for resource in RESOURCES:
        print(f"[COLLECTE] {resource} ...", flush=True)
        payload = fetch_all(resource)
        data[resource] = payload
        out = RAW / f"{resource}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        items = payload[resource]
        manifest["resources"][resource] = {
            "endpoint": f"{BASE}/{resource}?limit=0",
            "total_api": payload.get("total", len(items)),
            "items_downloaded": len(items),
            "file": str(out.relative_to(ROOT))
        }
        print(f"  -> {len(items)} éléments", flush=True)

    # Table de faits : une ligne par produit présent dans un panier.
    products = {p["id"]: p for p in data["products"]["products"]}
    users = {u["id"]: u for u in data["users"]["users"]}
    rows = []
    rng = random.Random(2026)
    base_date = datetime(2025, 1, 1)
    for cart in data["carts"]["carts"]:
        for item in cart.get("products", []):
            product = products.get(item.get("id"), {})
            rows.append({
                "order_id": f"CART-{cart['id']:05d}",
                "cart_id": cart.get("id"),
                "user_id": cart.get("userId"),
                "username": users.get(cart.get("userId"), {}).get("username"),
                "product_id": item.get("id"),
                "product_title": item.get("title") or product.get("title"),
                "category": product.get("category"),
                "brand": product.get("brand"),
                "quantity": item.get("quantity"),
                "unit_price": item.get("price"),
                "line_total": item.get("total"),
                "discount_percentage": item.get("discountPercentage"),
                "discounted_line_total": item.get("discountedTotal"),
                "cart_total": cart.get("total"),
                "cart_discounted_total": cart.get("discountedTotal"),
                "order_date": (base_date + timedelta(days=rng.randint(0, 364))).date().isoformat()
            })
    orders = pd.DataFrame(rows)
    orders.to_csv(PROCESSED / "commandes_ecommerce.csv", index=False)
    # tables utiles supplémentaires
    pd.json_normalize(data["products"]["products"]).to_csv(PROCESSED / "produits.csv", index=False)
    pd.json_normalize(data["users"]["users"]).drop(columns=[c for c in ["password","bank.cardNumber","bank.iban","crypto.wallet"] if c in pd.json_normalize(data["users"]["users"]).columns], errors="ignore").to_csv(PROCESSED / "utilisateurs_reduits.csv", index=False)
    carts_flat = [{k:v for k,v in c.items() if k != "products"} for c in data["carts"]["carts"]]
    pd.DataFrame(carts_flat).to_csv(PROCESSED / "paniers.csv", index=False)

    manifest["derived_tables"] = {
        "commandes_ecommerce.csv": {
            "rows": len(orders),
            "grain": "une ligne par produit dans un panier (ligne de panier)",
            "warning": "DummyJSON carts représente des paniers de démonstration, pas des commandes historiques réelles. order_date est artificielle."
        },
        "produits.csv": {"rows": len(data["products"]["products"])},
        "paniers.csv": {"rows": len(data["carts"]["carts"])},
        "utilisateurs_reduits.csv": {"rows": len(data["users"]["users"]), "warning": "Champs sensibles de démonstration exclus lorsque présents."}
    }
    (RAW / "manifest_collecte.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nCollecte terminée.")
    print(f"Fichiers bruts : {RAW}")
    print(f"Tables préparées : {PROCESSED}")
    print("IMPORTANT : order_date est une date synthétique, ne l'interprétez pas comme une date API.")

if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        print(f"\nERREUR RÉSEAU/API : {exc}", file=sys.stderr)
        print("Vérifiez Internet puis relancez le script. Les échantillons hors ligne restent disponibles.", file=sys.stderr)
        sys.exit(2)
