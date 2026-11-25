# Fiche de travail étudiant
## BigData Commerce Analytics — DummyJSON
**B2 · Sup de Vinci Rennes · Jour 1**

### Contexte
Vous intervenez comme équipe Data d'une boutique en ligne fictive. Vous devez identifier les sources disponibles, comprendre leur structure, mesurer leurs limites puis évaluer la qualité d'une table de lignes de panier.

**Source :** DummyJSON — https://dummyjson.com/  
**Nature :** API de démonstration avec données fictives. Ne pas présenter les données comme de vraies transactions ou de vrais clients.

## Atelier 1 — Explorer les sources (binôme)
### Travail à réaliser
1. Exécuter le notebook `01_atelier_exploration_sources.ipynb`.
2. Interroger au minimum `products`, `carts`, `users` et `comments`.
3. Compléter l'inventaire : endpoint, producteur, format, volume observé, fréquence d'accès, usage et limite.
4. Examiner un objet JSON et repérer les champs imbriqués.
5. Évaluer les cinq V avec une justification mesurable.
6. Proposer deux usages et deux limites pour chaque source principale.

### Questions obligatoires
- Pourquoi `carts` ne représente-t-il pas un historique de commandes finalisées ?
- Quelle ressource contient le catalogue ?
- Comment relier un panier à un utilisateur ?
- Quels champs sont imbriqués ?
- Pourquoi une API accessible à tout moment n'est-elle pas nécessairement du temps réel ?
- Quelles précautions prendre avec les informations de profil utilisateur ?

### Livrable Atelier 1
Un notebook exécuté et une synthèse d'une page (inventaire, 5V, usages, limites). Restitution orale : 3 minutes par binôme.

## Atelier 2 — Profiler les données avec Pandas
### Travail à réaliser
1. Exécuter `02_atelier_profilage_pandas.ipynb`.
2. Vérifier la granularité et les dimensions.
3. Contrôler les types, valeurs manquantes et doublons.
4. Calculer des statistiques descriptives.
5. Vérifier les règles métier sur quantité, prix et remise.
6. Créer un fichier nettoyé sans modifier la source brute.
7. Rédiger une note de qualité.

### Livrable Atelier 2
- Notebook exécuté.
- `commandes_ecommerce_nettoyees.csv`.
- Note de qualité d'une page.


## Règles de rendu
- Nommez le dossier `B2_NOM1_NOM2_BigData`.
- Gardez les fichiers bruts et les résultats nettoyés séparés.
- Exécutez toutes les cellules et vérifiez qu'aucune erreur ne subsiste.
- Citez les endpoints utilisés et indiquez la date de collecte.
- Distinguez les champs fournis par l'API des champs dérivés ou synthétiques.
