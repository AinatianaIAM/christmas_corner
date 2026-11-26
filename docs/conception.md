# Modélisation de la base de données

## 1. Modèle entité-association

### Entités

| Entité | Rôle | Identifiant |
|---|---|---|
| **CATEGORIE** | Famille de produits | `id_categorie` |
| **PRODUIT** | Article à vendre | `id_produit` |
| **CLIENT** | Personne qui passe commande | `id_client` |
| **COMMANDE** | Achat effectué par un client | `id_commande` |
| **LIGNE_COMMANDE** | Produit commandé dans une commande (avec quantité et prix) | `(id_produit, id_commande)` |

### Associations et cardinalités

| Association | Entités | Cardinalités | Signification |
|---|---|---|---|
| **regrouper** | CATEGORIE – PRODUIT | 0,N — 1,1 | Une catégorie peut regrouper plusieurs produits ou aucun. Un produit appartient obligatoirement à une seule catégorie. |
| **effectuer** | CLIENT – COMMANDE | 0,N — 1,1 | Un client peut passer plusieurs commandes ou aucune. Une commande est toujours associée à un seul client. |
| **contenir** | COMMANDE – LIGNE_COMMANDE | 1,N — 1,1 | Uune commande contient au moins une ligne de commande. Une ligne de commande appartient à une seule commande.|
| **apparaître** | PRODUIT – LIGNE_COMMANDE | 0,N — 1,1 | Un produit peut apparaître dans plusieurs lignes de commande ou aucune. Une ligne de commande concerne un seul produit. |

---

## 2. Schéma relationnel

Notation : <u>clé primaire</u> soulignée, `#` = clé étrangère.

```
CATEGORIE (id_categorie, nom)

PRODUIT (id_produit, nom, description, prix, image, quantite_stock, actif, #id_categorie)

CLIENT (id_client, nom, téléphone, email)

COMMANDE (id_commande, #id_client, date_commande, statut_commande,
          mode_reception, adresse_livraison, frais_livraison,
          mode_paiement, statut_paiement, date_reception, date_paiement)

LIGNE_COMMANDE (#id_produit, #id_commande, quantité, prix_unitaire)
```

## 3. Dépendances fonctionnelles

```
CATEGORIE :      id_categorie → nom

PRODUIT :        id_produit → nom, description, prix, image, actif, quantite_stock,id_categorie

CLIENT :         id_client → nom, téléphone, email
                 email → id_client            (email unique)

COMMANDE :       id_commande → id_client, date_commande, statut_commande,
                               mode_reception, adresse_livraison, frais_livraison,
                               mode_paiement, statut_paiement, date_reception, date_paiement

LIGNE_COMMANDE : (id_produit, id_commande) → quantité, prix_unitaire
```

---

## 4. Normalisation jusqu'à BCNF

### 1FN : attributs atomiques
Chaque attribut contient une seule valeur (pas de liste de produits dans une commande : elle est décomposée en lignes dans `LIGNE_COMMANDE`). Chaque table a une clé primaire.

### 2FN : pas de dépendance partielle
Les tables à clé simple sont automatiquement en 2FN. Pour `LIGNE_COMMANDE` (clé composée), `quantité` et `prix_unitaire` dépendent de **toute** la clé `(id_produit, id_commande)` et non d'une partie seulement.

### 3FN : pas de dépendance transitive
Aucun attribut non-clé ne dépend d'un autre attribut non-clé :
- la catégorie est référencée par `id_categorie` (le nom n'est pas recopié dans PRODUIT) ;
- le client est référencé par `id_client` (nom, téléphone, email ne sont pas recopiés dans COMMANDE).

Les informations de paiement et de réception (`mode_paiement`, `statut_paiement`, `date_paiement`, `date_reception`, `mode_reception`, `adresse_livraison`, `frais_livraison`) dépendent directement de `id_commande`, car elles décrivent chaque commande.

### BCNF : tout déterminant est une clé candidate
Pour chaque dépendance fonctionnelle `X → Y`, `X` est une clé (ou une clé candidate) :

| Table | Déterminant | Clé candidate ? |
|---|---|---|
| CATEGORIE | `id_categorie` | Oui (clé primaire) |
| CATEGORIE | `nom` | Oui (clé candidate, unique) |
| PRODUIT | `id_produit` | Oui (clé primaire) |
| CLIENT | `id_client` | Oui (clé primaire) |
| CLIENT | `email` | Oui (clé candidate, unique) |
| COMMANDE | `id_commande` | Oui (clé primaire) |
| LIGNE_COMMANDE | `(id_produit, id_commande)` | Oui (clé primaire) |

Aucun déterminant n'est en dehors des clés : **toutes les relations sont en BCNF**.

**Remarque sur le rôle de l'administration**

L'administrateur n'est pas représenté comme une entité dans le modèle entité-association, car son rôle concerne principalement la gestion et le suivi des données de la boutique, et non les opérations de vente en tant que telles.

Dans l'application Christmas Corner, l'administration est assurée à travers l'interface d'administration de Django. Elle permet notamment de :

- gérer les catégories et les produits (ajout, modification et suppression) ;
- suivre et mettre à jour les quantités en stock ;
- consulter et gérer les commandes ;
- modifier les statuts des commandes ;
- consulter les informations des clients et les informations relatives aux paiements.
