# BigData Commerce Analytics

**B2 · Sup de Vinci Rennes · Big Data (TP1, TP2, TP3)**

Projet fil rouge sur trois jours : collecter les données d'une boutique en ligne de démonstration (API DummyJSON), les stocker dans MongoDB, les traiter avec PySpark, pseudonymiser les clients, puis présenter les indicateurs dans des graphiques et un dashboard Streamlit.

```
API DummyJSON + CSV  →  Python  →  MongoDB (base commerce)  →  PySpark  →  Parquet pseudonymisé  →  Matplotlib / Streamlit
```

## Où trouver quoi

- **Comptes rendus** : les comptes rendus en notebook sont dans le dossier [`Compte_rendu_et_Synthese/`](Compte_rendu_et_Synthese/)
  - `Atelier_1_TP_1.ipynb` et `Atelier_2_TP_1.ipynb` : réponses du TP1 (sources, 5V, profilage) ;
  - `Synthese_TP_2.ipynb` : analyse et questions de synthèse du TP2.
- **Notebooks d'ingestion, de traitement et de sécurisation (TP2 et TP3)** : ils sont dans le dossier [`notebooks/`](notebooks/)
  - `TP2_Atelier_1_ingestion_api_mongodb.ipynb` : ingestion des 8 ressources de l'API dans MongoDB, import des commandes, simulation des paiements ;
  - `TP2_Atelier_2_Traitement_pyspark.ipynb` : traitement PySpark (lecture MongoDB, transformations, actions, lazy evaluation, partitions) et indicateurs ;
  - `TP3.ipynb` : pseudonymisation HMAC des clients, export Parquet et graphiques Matplotlib.
- **Dashboard** : le code du dashboard est dans [`dashboard/app.py`](dashboard/app.py)

Autres dossiers :

| Dossier | Contenu |
|---|---|
| `notebooks/01_atelier_exploration_sources.ipynb`, `02_atelier_profilage_pandas.ipynb` | Notebooks guidés du TP1 |
| `notebooks/demo_spark_products.ipynb` | Démonstration PySpark fournie par l'enseignant |
| `scripts/` | Collecte de l'API (`01_collecte_dummyjson.py`) et script de nettoyage (`02_nettoyage_donnees.py`) |
| `resultats/` | Indicateurs calculés par Spark (CSV) et graphiques exportés (`resultats/graphiques/`) |
| `captures/` | Captures de Spark UI (lazy evaluation, stages et tasks) |
| `consignes/` | Fiche étudiant fournie avec le kit |
| `.streamlit/config.toml` | Thème du dashboard |

## Installation

### Prérequis

| Outil | Version | Rôle |
|---|---|---|
| Python | 3.10 ou plus (testé en 3.11) | Notebooks, collecte, dashboard |
| Java | **17** (ou 21) | Requis par PySpark 4.0. Java 25 n'est pas pris en charge. |
| Docker | récent | Faire tourner MongoDB |
| MongoDB | 7 | Base de données `commerce` |

### 1. MongoDB avec Docker

```bash
docker run -d -p 27017:27017 --name mongo mongo:7
docker ps                  # le conteneur mongo doit être "Up"
```

Les fois suivantes, il suffit de `docker start mongo`.

### 2. Environnement Python

Ubuntu / macOS :
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows (PowerShell) :
```powershell
py -3.11 -m venv C:\venvs\bigdata
C:\venvs\bigdata\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Clé de pseudonymisation (TP3)

Le notebook `TP3.ipynb` lit la clé secrète dans la variable d'environnement `PSEUDO_KEY`. **Chacun choisit sa propre clé, qui ne doit jamais être écrite dans le code ni poussée sur GitHub.**

```bash
export PSEUDO_KEY="une-phrase-secrete-longue"          # Linux / macOS, à définir avant de lancer Jupyter
```
```powershell
setx PSEUDO_KEY "une-phrase-secrete-longue"            # Windows, puis fermer et rouvrir VS Code / le terminal
```

### 4. Particularités de Windows

Le TP est prévu sous Ubuntu. Sous Windows, Spark a besoin de quelques réglages supplémentaires :

- **Pas d'accent ni d'espace dans le chemin de l'environnement Python** : un chemin comme `C:\Users\Timéo\...` empêche Spark de trouver ses fichiers. D'où l'environnement dans `C:\venvs\bigdata`.
- **Nom du PC avec un accent** : définir `setx SPARK_LOCAL_HOSTNAME localhost`.
- **winutils** : Hadoop a besoin de `winutils.exe` et `hadoop.dll` sous Windows pour charger le connecteur MongoDB.
  ```powershell
  New-Item -ItemType Directory -Force C:\hadoop\bin
  Invoke-WebRequest "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin/winutils.exe" -OutFile C:\hadoop\bin\winutils.exe
  Invoke-WebRequest "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin/hadoop.dll" -OutFile C:\hadoop\bin\hadoop.dll
  setx HADOOP_HOME C:\hadoop
  ```
  La première cellule de `TP2_Atelier_2_Traitement_pyspark.ipynb` configure ensuite ces variables pour la session Spark.

Dans VS Code, choisir l'interpréteur de l'environnement (`Ctrl+Shift+P` → *Python: Select Interpreter*) et le même kernel dans chaque notebook.

## Exécution

Lancer les notebooks dans cet ordre, depuis la racine du projet (MongoDB démarré) :

1. `notebooks/TP2_Atelier_1_ingestion_api_mongodb.ipynb` : remplit la base `commerce` (8 collections `raw_*`, `raw_commandes`, `raw_payments`). Il peut être relancé sans créer de doublons.
2. `notebooks/TP2_Atelier_2_Traitement_pyspark.ipynb` : traitement Spark et indicateurs, exportés dans `resultats/`. Le premier lancement télécharge le connecteur MongoDB pour Spark (une à deux minutes). Spark UI est disponible sur http://localhost:4040 pendant la session.
3. `notebooks/TP3.ipynb` : pseudonymisation, export Parquet dans `data/analytique/` et graphiques dans `resultats/graphiques/`.

Puis le dashboard :
```bash
python -m streamlit run dashboard/app.py
```
Il s'ouvre sur http://localhost:8501 et lit les fichiers Parquet produits par `TP3.ipynb`.

La simulation des paiements utilise une graine fixe (42) : tout le monde obtient les mêmes statuts et les mêmes indicateurs. Seuls les pseudonymes changent d'une clé à l'autre.

## Données

DummyJSON est une API de **données fictives**. Ce n'est pas une vraie boutique : les paniers ne sont pas de vraies commandes, les dates `order_date` sont générées pour l'exercice et les paiements sont simulés. Aucune conclusion ne doit être tirée pour un commerce réel.

Ressources utilisées (toutes avec `?limit=0`) : `products`, `carts`, `users`, `posts`, `comments`, `recipes`, `quotes`, `todos` sur `https://dummyjson.com`. Les ressources `products`, `carts` et `users` sont le cœur du cas e-commerce, les autres servent à comparer des formats.

Le fichier `data/processed/commandes_ecommerce.csv` contient une ligne par produit dans un panier (800 lignes, 208 paniers). Attention : `cart_total` et `cart_discounted_total` sont répétés sur chaque ligne d'un panier, il ne faut pas les additionner.

### Données personnelles

La collection `raw_users` contient des champs sensibles (fictifs mais structurés comme de vraies données) : mots de passe, numéro de sécurité sociale, IBAN, adresse... Les datasets d'analyse du TP3 ne contiennent plus `user_id` ni `username`, remplacés par un pseudonyme HMAC-SHA256. Une donnée pseudonymisée reste une donnée personnelle : les fichiers de `data/` sont générés en local par les notebooks et ne doivent pas être publiés.

## Dépannage

| Problème | Solution |
|---|---|
| `ServerSelectionTimeoutError` | MongoDB n'est pas démarré : `docker start mongo` |
| `JAVA_GATEWAY_EXITED` ou `ClassNotFoundException: SparkSubmit` | Vérifier `java -version` (17) et que l'environnement Python n'est pas dans un chemin avec accent |
| `Invalid Spark URL` | `SPARK_LOCAL_HOSTNAME=localhost` (nom du PC avec accent) |
| `HADOOP_HOME and hadoop.home.dir are unset` | Installer winutils (voir plus haut) et redémarrer le kernel |
| `La variable d'environnement PSEUDO_KEY n'est pas définie` | Définir la clé puis redémarrer VS Code / Jupyter |
| `streamlit` n'est pas reconnu | Activer l'environnement Python et utiliser `python -m streamlit run dashboard/app.py` |
| Le dashboard affiche « Datasets introuvables » | Exécuter d'abord `notebooks/TP3.ipynb` |
