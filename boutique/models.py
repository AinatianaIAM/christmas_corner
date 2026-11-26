
from django.db import models
from django.utils import timezone


class Categorie(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'categorie'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom


class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    image = models.ImageField(
        upload_to='produits/',
        blank=True,
        null=True,
        db_column='image'
    )
    actif = models.BooleanField(default=True)
    id_categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        db_column='id_categorie'
    )

    class Meta:
        managed = False
        db_table = 'produit'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.nom


class Client(models.Model):
    id_client = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=150, unique=True)

    class Meta:
        managed = False
        db_table = 'client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.nom


class Commande(models.Model):

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmée'),
        ('PRETE', 'Prête'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]

    RECEPTION_CHOICES = [
        ('RETRAIT', 'Retrait'),
        ('LIVRAISON', 'Livraison'),
    ]

    PAIEMENT_CHOICES = [
        ('NON_PAYE', 'Non payé'),
        ('PAYE', 'Payé'),
    ]

    MODE_PAIEMENT_CHOICES = [
        ('ESPECES', 'Espèces'),
        ('MOBILE_MONEY', 'Mobile Money'),
    ]

    id_commande = models.AutoField(primary_key=True)
    id_client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        db_column='id_client'
    )
    date_commande = models.DateTimeField(default=timezone.now)
    statut_commande = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    mode_reception = models.CharField(
        max_length=10,
        choices=RECEPTION_CHOICES
    )
    adresse_livraison = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    date_reception_prevue = models.DateField(
        blank=True,
        null=True
    )
    frais_livraison = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    statut_paiement = models.CharField(
        max_length=10,
        choices=PAIEMENT_CHOICES,
        default='NON_PAYE'
    )
    mode_paiement = models.CharField(
        max_length=15,
        choices=MODE_PAIEMENT_CHOICES,
        blank=True,
        null=True
    )
    date_paiement = models.DateField(
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'commande'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'

    def __str__(self):
        return f"Commande n°{self.id_commande}"


class LigneCommande(models.Model):
    pk = models.CompositePrimaryKey(
        'id_commande',
        'id_produit'
    )

    id_commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        db_column='id_commande'
    )
    id_produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        db_column='id_produit'
    )
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        managed = False
        db_table = 'ligne_commande'
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'

    def __str__(self):
        return f"Commande {self.id_commande_id} - Produit {self.id_produit_id}"
