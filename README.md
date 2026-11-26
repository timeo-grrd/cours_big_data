# BigData Commerce Analytics — Kit pédagogique DummyJSON
**B2 · Sup de Vinci Rennes · Jour 1 — Sources, exploration et qualité des données**

## Objectif
Ce kit sert à découvrir une API REST, inventorier plusieurs sources, comprendre leurs formats et leurs limites, puis profiler un jeu de commandes avec Pandas.

## Important : nature des données
DummyJSON est une API de données fictives/de démonstration. Ce n'est pas une plateforme e-commerce réelle, ni un historique transactionnel représentatif d'une entreprise. Les opérations POST/PUT/PATCH/DELETE sont simulées et ne persistent pas dans la base distante. Les données peuvent évoluer : le script capture un instantané à la date de collecte.

La session de création de ce ZIP ne disposait pas d'un accès réseau Python à dummyjson.com. Le dossier `data/raw/` contient donc un **petit jeu de démonstration hors ligne**, explicitement identifié comme tel. Pour récupérer les jeux complets actuels, exécuter `scripts/01_collecte_dummyjson.py` depuis un poste connecté à Internet. Le script utilise `limit=0`, conserve les réponses JSON brutes, construit des CSV normalisés et écrit un manifeste de collecte. Il ne prétend pas que le mini-échantillon fourni est le jeu complet de l'API.

## Démarrage rapide (Ubuntu / macOS / Linux)
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install pandas requests jupyter matplotlib
python scripts/01_collecte_dummyjson.py
jupyter notebook
```
Sous Windows PowerShell :
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas requests jupyter matplotlib
python scripts/01_collecte_dummyjson.py
jupyter notebook
```
Ouvrir ensuite `notebooks/01_atelier_exploration_sources.ipynb`, puis `notebooks/02_atelier_profilage_pandas.ipynb`.

## Organisation
- `data/raw/` : réponses JSON brutes et CSV d'exemple hors ligne.
- `data/processed/` : tables aplaties produites par le script.
- `data/dataset_nettoye/` : table de commandes nettoyée, générée par le script de nettoyage.
- `scripts/01_collecte_dummyjson.py` : extraction des ressources.
- `scripts/02_nettoyage_donnees.py` : suppression des lignes contenant une valeur numérique négative.
- `notebooks/` : deux notebooks guidés.
- `consignes/` : fiche étudiant et barème indicatif.

## Nettoyer les données de commandes
Après la collecte (ou avec le CSV d'exemple hors ligne), lancer depuis la racine du projet :
```powershell
.\.venv\Scripts\python.exe .\scripts\02_nettoyage_donnees.py
```
Le script lit `data/processed/commandes_ecommerce.csv` s'il existe, sinon le CSV d'exemple `data/raw/commandes_ecommerce.csv`. Il conserve les sources intactes et écrit le résultat dans `data/dataset_nettoye/commandes_ecommerce_nettoyees.csv`. Les lignes contenant une valeur numérique négative sont retirées; les lignes sans quantité positive ou sans prix unitaire valide sont également écartées.

## Sources API étudiées
- Produits : `https://dummyjson.com/products?limit=0`
- Paniers : `https://dummyjson.com/carts?limit=0`
- Utilisateurs : `https://dummyjson.com/users?limit=0`
- Publications : `https://dummyjson.com/posts?limit=0`
- Commentaires : `https://dummyjson.com/comments?limit=0`
- Recettes : `https://dummyjson.com/recipes?limit=0`
- Citations : `https://dummyjson.com/quotes?limit=0`
- Todos : `https://dummyjson.com/todos?limit=0`

Les ressources `products`, `carts`, `users` sont le cœur du cas e-commerce. Les autres ressources servent à comparer des formats et à discuter de sources hors transactionnel.

## Schéma de la table de commandes pédagogique
`commandes_ecommerce.csv` est construit à partir des lignes de paniers collectées :
`order_id, cart_id, user_id, product_id, product_title, category, quantity, unit_price, line_total, discount_percentage, discounted_line_total, cart_total, order_date`
**Attention :** DummyJSON carts n'est pas un véritable journal de commandes datées. `order_date` est une date pédagogique générée à partir d'une graine fixe pour permettre les exercices temporels ; elle ne provient pas de l'API. Le script la signale dans le manifeste. Les montants et articles proviennent des paniers renvoyés par l'API.

## Dépannage
- Si la collecte échoue : vérifier l'accès Internet et relancer le script.
- Si l'API est indisponible : les notebooks peuvent être étudiés avec les fichiers d'exemple fournis.
- Ne jamais considérer les données comme des données personnelles ou commerciales réelles.
