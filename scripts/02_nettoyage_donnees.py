#!/usr/bin/env python3
"""Nettoie la table des commandes et écrit le résultat dans un dossier séparé."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CANDIDATES = (
    ROOT / "data" / "processed" / "commandes_ecommerce.csv",
    ROOT / "data" / "raw" / "commandes_ecommerce.csv",
)
OUTPUT_DIR = ROOT / "data" / "dataset_nettoye"
REQUIRED_COLUMNS = ("quantity", "unit_price")


def nettoyer_commandes(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Colonnes obligatoires absentes : " + ", ".join(missing_columns)
        )

    valid_rows = pd.Series(True, index=df.index)
    numeric_columns = df.select_dtypes(include="number").columns
    if len(numeric_columns):
        valid_rows &= ~df[numeric_columns].lt(0).any(axis=1)

    quantity = pd.to_numeric(df["quantity"], errors="coerce")
    unit_price = pd.to_numeric(df["unit_price"], errors="coerce")
    valid_rows &= quantity.notna() & quantity.gt(0)
    valid_rows &= unit_price.notna() & unit_price.ge(0)

    return df.loc[valid_rows].copy()


def main() -> None:
    source = next((path for path in SOURCE_CANDIDATES if path.is_file()), None)
    if source is None:
        expected_paths = "\n".join(f"- {path}" for path in SOURCE_CANDIDATES)
        raise FileNotFoundError(
            "Aucun fichier de commandes trouvé. Fichiers recherchés :\n"
            f"{expected_paths}"
        )

    orders = pd.read_csv(source)
    cleaned_orders = nettoyer_commandes(orders)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / "commandes_ecommerce_nettoyees.csv"
    cleaned_orders.to_csv(output, index=False)

    removed_rows = len(orders) - len(cleaned_orders)
    print(f"Source : {source}")
    print(f"Lignes avant nettoyage : {len(orders)}")
    print(f"Lignes supprimées : {removed_rows}")
    print(f"Lignes après nettoyage : {len(cleaned_orders)}")
    print(f"Jeu nettoyé enregistré : {output}")


if __name__ == "__main__":
    main()
