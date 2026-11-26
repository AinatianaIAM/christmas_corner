-- ============================================================
-- Christmas Corner : données de test
-- À exécuter APRÈS schema.sql
-- ============================================================
BEGIN;

INSERT INTO categorie (id_categorie, nom) VALUES
 (1, 'Gourmandises'),
 (2, 'Cadeaux / Décoration');

INSERT INTO produit (id_produit, nom, description, prix, quantite_stock, image, actif, id_categorie) VALUES
 (1, 'Biscuits au gingembre', 'Boîte de 12 biscuits épicés', 12000, 40, 'produits/biscuits_gingembre.jpg', TRUE, 1),
 (2, 'Chocolats de Noël',     'Assortiment de 20 chocolats',  25000, 25, 'produits/chocolats_noel.jpg',      TRUE, 1),
 (3, 'Cannes en sucre',       'Sachet de 10 cannes en sucre',  6000, 60, 'produits/cannes_sucre.jpg',        TRUE, 1),
 (4, 'Bûche de Noël',         'Bûche chocolat-praliné, 6 parts', 45000, 8, 'produits/buche_noel.jpg',        TRUE, 1),
 (5, 'Boules de sapin',       'Lot de 6 boules rouges et or', 18000, 30, 'produits/boules_sapin.jpg',        TRUE, 2),
 (6, 'Guirlande lumineuse',   'Guirlande LED 5 m, blanc chaud', 30000, 15, 'produits/guirlande.jpg',         TRUE, 2),
 (7, 'Bonnet du Père Noël',   'Bonnet rouge taille unique',    8000, 50, 'produits/bonnet.jpg',              TRUE, 2),
 (8, 'Calendrier de l''Avent 2025', 'Ancien modèle, retiré de la vente', 20000, 0, 'produits/calendrier.jpg', FALSE, 1);

INSERT INTO client (id_client, nom, telephone, email) VALUES
 (1, 'Rakoto Andry',     '034 11 222 33', 'andry.rakoto@example.com'),
 (2, 'Rasoa Miora',      '032 44 555 66', 'miora.rasoa@example.com'),
 (3, 'Randria Hery',     '033 77 888 99', 'hery.randria@example.com'),
 (4, 'Razafy Lalaina',   '034 00 111 22', 'lalaina.razafy@example.com');

-- 1) Terminée, retrait, payée en espèces
INSERT INTO commande (id_commande, id_client, date_commande, statut_commande, mode_reception,
    adresse_livraison, date_reception_prevue, frais_livraison, statut_paiement, mode_paiement, date_paiement)
VALUES (1, 1, '2026-11-10 10:30', 'TERMINEE', 'RETRAIT', NULL, '2026-11-12', 0, 'PAYE', 'ESPECES', '2026-11-12');

-- 2) Confirmée, livraison, non payée
INSERT INTO commande (id_commande, id_client, date_commande, statut_commande, mode_reception,
    adresse_livraison, date_reception_prevue, frais_livraison, statut_paiement, mode_paiement, date_paiement)
VALUES (2, 2, '2026-11-18 14:00', 'CONFIRMEE', 'LIVRAISON', 'Lot II B 45, Analakely, Antananarivo', '2026-11-27', 5000, 'NON_PAYE', NULL, NULL);

-- 3) En attente, retrait
INSERT INTO commande (id_commande, id_client, date_commande, statut_commande, mode_reception,
    adresse_livraison, date_reception_prevue, frais_livraison, statut_paiement, mode_paiement, date_paiement)
VALUES (3, 3, '2026-11-23 09:15', 'EN_ATTENTE', 'RETRAIT', NULL, NULL, 0, 'NON_PAYE', NULL, NULL);

-- 4) Annulée
INSERT INTO commande (id_commande, id_client, date_commande, statut_commande, mode_reception,
    adresse_livraison, date_reception_prevue, frais_livraison, statut_paiement, mode_paiement, date_paiement)
VALUES (4, 1, '2026-11-20 16:45', 'ANNULEE', 'RETRAIT', NULL, NULL, 0, 'NON_PAYE', NULL, NULL);

-- 5) Terminée, livraison, payée en mobile money (client 4)
INSERT INTO commande (id_commande, id_client, date_commande, statut_commande, mode_reception,
    adresse_livraison, date_reception_prevue, frais_livraison, statut_paiement, mode_paiement, date_paiement)
VALUES (5, 4, '2026-11-15 11:00', 'TERMINEE', 'LIVRAISON', 'Ankadifotsy, Antananarivo', '2026-11-17', 4000, 'PAYE', 'MOBILE_MONEY', '2026-11-17');

INSERT INTO ligne_commande (id_commande, id_produit, quantite, prix_unitaire) VALUES
 (1, 1, 2, 12000),
 (1, 3, 1,  6000),
 (2, 2, 1, 25000),
 (2, 5, 2, 18000),
 (3, 4, 1, 45000),
 (4, 7, 3,  8000),
 (5, 6, 1, 30000),
 (5, 5, 1, 17000);  -- prix historique différent du prix catalogue actuel (18000)

-- Remise à niveau des séquences après insertion d'identifiants explicites
SELECT setval(pg_get_serial_sequence('categorie','id_categorie'), (SELECT MAX(id_categorie) FROM categorie));
SELECT setval(pg_get_serial_sequence('produit','id_produit'),     (SELECT MAX(id_produit)   FROM produit));
SELECT setval(pg_get_serial_sequence('client','id_client'),       (SELECT MAX(id_client)    FROM client));
SELECT setval(pg_get_serial_sequence('commande','id_commande'),   (SELECT MAX(id_commande)  FROM commande));

COMMIT;
