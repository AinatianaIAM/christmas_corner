# Christmas Corner

## Présentation

Christmas Corner est une application web de gestion et de vente de produits de Noël.

Elle permet aux clients de consulter un catalogue, de constituer un panier et de passer une commande avec un choix entre le retrait en boutique et la livraison.

Un espace administrateur permet de gérer les produits, les catégories, les clients, les commandes, les stocks et le suivi des ventes.

## Technologies utilisées

- Python
- Django
- PostgreSQL
- HTML
- CSS

## Fonctionnalités

### Espace client
- Consultation du catalogue.
- Filtrage des produits par catégorie.
- Consultation des détails des produits.
- Gestion du panier.
- Passage de commande.
- Choix du mode de réception.

### Espace administrateur
- Gestion des catégories et des produits.
- Gestion des stocks.
- Gestion des clients.
- Gestion des commandes et des paiements.
- Suivi des ventes.

## Base de données

La base de données comporte cinq tables principales :

- categorie
- produit
- client
- commande
- ligne_commande

Les scripts SQL fournis permettent de créer la structure et d'insérer les données de démonstration.

## Installation

1. Cloner le dépôt :

   `git clone URL_DU_DEPOT`

2. Accéder au dossier du projet :

   `cd christmas_corner`

3. Créer et activer un environnement virtuel :

   `python -m venv .venv`

   Sous Git Bash :

   `source .venv/Scripts/activate`

4. Installer les dépendances :

   `pip install -r requirements.txt`

5. Créer une base de données PostgreSQL.

6. Exécuter les scripts `schema.sql` et `data.sql` dans cette base.

7. Définir les variables d'environnement `DB_PASSWORD` et `DJANGO_SECRET_KEY`.
#### Variables d'environnement

Avant de lancer le projet, chaque utilisateur doit définir ses propres variables d'environnement.

Définir les variables dans Git Bash :

`$ export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"`

`export DB_PASSWORD="votre_mot_de_passe_postgresql"`

**Ces variables doivent être définies avant le lancement du serveur Django.**



8. Configurer les paramètres de connexion PostgreSQL dans `config/settings.py`: mettre le même nom de database que dans PostgreSQL.

9. Exécuter :

   `python manage.py migrate`

9. Lancer le serveur :

   `python manage.py runserver`

## Accès

- Site client : http://127.0.0.1:8000/
- Administration : http://127.0.0.1:8000/admin/


