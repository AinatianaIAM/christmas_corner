
from django.contrib import admin
from .models import Categorie, Produit, Client, Commande
from django.utils.html import format_html
from urllib.parse import quote
from django.core.mail import send_mail
from django.contrib import messages
from django.db import connection, transaction
from django.urls import path, reverse
from datetime import date
from decimal import Decimal
from django.shortcuts import render

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("id_categorie", "nom")
    search_fields = ("nom",)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        "id_produit",
        "nom",
        "id_categorie",
        "prix",
        "quantite_stock",
        "actif",
    )
    list_filter = ("id_categorie", "actif")
    search_fields = ("nom", "description")
    list_editable = ("prix", "quantite_stock", "actif")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id_client", "nom", "telephone", "email")
    search_fields = ("nom", "telephone", "email")



@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):

    list_display = (
        "id_commande",
        "id_client",
        "date_commande",
        "statut_commande",
        "mode_reception",
        "statut_paiement",
        "mode_paiement",
        "date_paiement",
        "frais_livraison",
        "contacter_client",
        "informer_frais_whatsapp",
    )

    fields = (
        'id_client',
        'date_commande',
        'statut_commande',
        'mode_reception',
        'adresse_livraison',
        'date_reception_prevue',
        'frais_livraison',
        'statut_paiement',
        'mode_paiement',
        'date_paiement',
    )

    list_editable = ("frais_livraison",)
    def save_model(self, request, obj, form, change):
        with transaction.atomic():

            ancien_statut = None

            if change:
                ancien_statut = (
                    Commande.objects
                    .select_for_update()
                    .get(pk=obj.pk)
                    .statut_commande
                )

            # Une commande terminée ne peut plus être réouverte
            if ancien_statut == 'TERMINEE' and obj.statut_commande != 'TERMINEE':
                obj.statut_commande = 'TERMINEE'
                self.message_user(
                    request,
                    "Une commande terminée ne peut plus être modifiée.",
                    level=messages.WARNING
                )

            # Déduire le stock lors du passage à TERMINEE
            elif obj.statut_commande == 'TERMINEE' and ancien_statut != 'TERMINEE':

                if obj.statut_paiement != 'PAYE':
                    obj.statut_commande = ancien_statut or 'EN_ATTENTE'
                    self.message_user(
                        request,
                        "Impossible de terminer une commande non payée.",
                        level=messages.WARNING
                    )

                else:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT id_produit, quantite
                            FROM ligne_commande
                            WHERE id_commande = %s
                            ORDER BY id_produit
                            """,
                            [obj.id_commande]
                        )
                        lignes = cursor.fetchall()

                    produits = Produit.objects.select_for_update().filter(
                        id_produit__in=[ligne[0] for ligne in lignes]
                    ).order_by('id_produit')

                    produits_dict = {
                        p.id_produit: p for p in produits
                    }

                    erreur_stock = not lignes

                    for produit_id, quantite in lignes:
                        produit = produits_dict.get(produit_id)

                        if produit is None or produit.quantite_stock < quantite:
                            erreur_stock = True
                            break

                    if erreur_stock:
                        obj.statut_commande = ancien_statut or 'EN_ATTENTE'
                        self.message_user(
                            request,
                            "Stock insuffisant ou commande sans articles. "
                            "Le statut n'a pas été modifié.",
                            level=messages.WARNING
                        )

                    else:
                        for produit_id, quantite in lignes:
                            produit = produits_dict[produit_id]
                            produit.quantite_stock -= quantite
                            produit.save(update_fields=['quantite_stock'])

                        self.message_user(
                            request,
                            "Stock mis à jour : les quantités ont été déduites.",
                            level=messages.SUCCESS
                        )

        super().save_model(request, obj, form, change)
    list_filter = (
        "statut_commande",
        "mode_reception",
        "statut_paiement",
    )

    search_fields = (
        "id_client__nom",
        "id_client__telephone",
        "id_client__email",
    )

    actions = ['envoyer_email', 'envoyer_email_frais']

    def calculer_total_articles(self, commande):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COALESCE(SUM(quantite * prix_unitaire), 0)
                FROM ligne_commande
                WHERE id_commande = %s
                """,
                [commande.id_commande]
            )
            return cursor.fetchone()[0]

    def contacter_client(self, obj):
        telephone = ''.join(
            c for c in obj.id_client.telephone if c.isdigit()
        )

        if telephone.startswith('0'):
            telephone = '261' + telephone[1:]
        elif not telephone.startswith('261'):
            telephone = '261' + telephone

        message = (
            f"Bonjour {obj.id_client.nom}, "
            f"votre commande n°{obj.id_commande} "
            "chez Christmas Corner est prête ! "
            "Vous pouvez venir la récupérer. "
            "Merci pour votre confiance."
        )

        url = f"https://wa.me/{telephone}?text={quote(message)}"

        return format_html(
            '<a href="{}" target="_blank">Commande prête</a>',
            url
        )

    contacter_client.short_description = "WhatsApp (prête)"

    def informer_frais_whatsapp(self, obj):
        if obj.mode_reception != 'LIVRAISON':
            return "-"

        telephone = ''.join(
            c for c in obj.id_client.telephone if c.isdigit()
        )

        if telephone.startswith('0'):
            telephone = '261' + telephone[1:]
        elif not telephone.startswith('261'):
            telephone = '261' + telephone

        total_articles = self.calculer_total_articles(obj)
        frais = obj.frais_livraison
        total = total_articles + frais

        message = (
            f"Bonjour {obj.id_client.nom},\n\n"
            f"Concernant votre commande n°{obj.id_commande} "
            "chez Christmas Corner :\n\n"
            f"Montant des articles : {total_articles:,.0f} Ar\n"
            f"Frais de livraison : {frais:,.0f} Ar\n"
            f"TOTAL À PAYER : {total:,.0f} Ar\n\n"
            "Merci pour votre confiance !"
        )

        url = f"https://wa.me/{telephone}?text={quote(message)}"

        return format_html(
            '<a href="{}" target="_blank">Informer des frais</a>',
            url
        )

    informer_frais_whatsapp.short_description = "WhatsApp (frais)"

    @admin.action(description="Envoyer un e-mail : commande prête")
    def envoyer_email(self, request, queryset):
        for commande in queryset:
            if commande.statut_commande != 'PRETE':
                self.message_user(
                    request,
                    f"Commande n°{commande.id_commande} non prête.",
                    level=messages.WARNING
                )
                continue

            client = commande.id_client

            message = (
                f"Bonjour {client.nom},\n\n"
                f"Votre commande n°{commande.id_commande} "
                "chez Christmas Corner est prête !\n"
                "Vous pouvez venir la récupérer.\n\n"
                "Merci pour votre confiance !\n"
                "L'équipe Christmas Corner"
            )

            try:
                send_mail(
                    subject=f"Votre commande n°{commande.id_commande} est prête !",
                    message=message,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                self.message_user(
                    request,
                    f"E-mail envoyé à {client.email}.",
                    level=messages.SUCCESS
                )

            except Exception as erreur:
                self.message_user(
                    request,
                    f"Erreur : {erreur}",
                    level=messages.ERROR
                )

    @admin.action(description="Envoyer un e-mail : frais de livraison")
    def envoyer_email_frais(self, request, queryset):
        for commande in queryset:

            if commande.mode_reception != 'LIVRAISON':
                self.message_user(
                    request,
                    f"Commande n°{commande.id_commande} : pas de livraison.",
                    level=messages.WARNING
                )
                continue

            client = commande.id_client
            total_articles = self.calculer_total_articles(commande)
            frais = commande.frais_livraison
            total = total_articles + frais

            message = (
                f"Bonjour {client.nom},\n\n"
                f"Concernant votre commande n°{commande.id_commande} :\n\n"
                f"Montant des articles : {total_articles:,.0f} Ar\n"
                f"Frais de livraison : {frais:,.0f} Ar\n"
                f"TOTAL À PAYER : {total:,.0f} Ar\n\n"
                "Merci pour votre confiance !\n"
                "L'équipe Christmas Corner"
            )

            try:
                send_mail(
                    subject=f"Frais de livraison - Commande n°{commande.id_commande}",
                    message=message,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                self.message_user(
                    request,
                    f"E-mail envoyé à {client.email}.",
                    level=messages.SUCCESS
                )

            except Exception as erreur:
                self.message_user(
                    request,
                    f"Erreur : {erreur}",
                    level=messages.ERROR
                )
    def get_urls(self):
        urls = super().get_urls()

        urls_personnalisees = [
            path(
                'suivi-ventes/',
                self.admin_site.admin_view(self.suivi_ventes),
                name='suivi_ventes',
            ),
        ]

        return urls_personnalisees + urls
    change_list_template = "admin/boutique/commande/change_list.html"
    def get_urls(self):
        urls = super().get_urls()

        urls_personnalisees = [
            path(
                'suivi-ventes/',
                self.admin_site.admin_view(self.suivi_ventes),
                name='suivi_ventes',
            ),
        ]

        return urls_personnalisees + urls

    def suivi_ventes(self, request):
        date_debut = request.GET.get('date_debut', '')
        date_fin = request.GET.get('date_fin', '')
        produit_id = request.GET.get('produit', '')

        erreur = None

        # Vérifier les dates
        try:
            debut = date.fromisoformat(date_debut) if date_debut else None
            fin = date.fromisoformat(date_fin) if date_fin else None

            if debut and fin and debut > fin:
                erreur = "La date de début doit précéder la date de fin."
                debut = fin = None

        except ValueError:
            erreur = "Date invalide."
            debut = fin = None

        # Conditions communes : commandes payées
        conditions = ["c.statut_paiement = 'PAYE'"]
        parametres = []

        if debut:
            conditions.append("c.date_paiement::date >= %s")
            parametres.append(debut)

        if fin:
            conditions.append("c.date_paiement::date <= %s")
            parametres.append(fin)

        where_sql = " AND ".join(conditions)

        # Filtre produit : uniquement pour les ventes de produits
        filtre_produit = ""
        params_produit = list(parametres)

        if produit_id:
            try:
                int(produit_id)
                filtre_produit = " AND lc.id_produit = %s"
                params_produit.append(int(produit_id))
            except ValueError:
                produit_id = ''

        # Liste des ventes de produits par commande
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    c.id_commande,
                    cl.nom,
                    c.date_paiement,
                    SUM(lc.quantite * lc.prix_unitaire)
                FROM commande c
                JOIN client cl ON cl.id_client = c.id_client
                JOIN ligne_commande lc
                    ON lc.id_commande = c.id_commande
                WHERE {where_sql} {filtre_produit}
                GROUP BY c.id_commande, cl.nom, c.date_paiement
                ORDER BY c.date_paiement DESC
                """,
                params_produit
            )

            ventes_produits = [
                {
                    'commande': ligne[0],
                    'client': ligne[1],
                    'date': ligne[2],
                    'montant': ligne[3],
                }
                for ligne in cursor.fetchall()
            ]

        # Liste des frais de livraison : indépendante du filtre produit
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    c.id_commande,
                    cl.nom,
                    c.date_paiement,
                    c.frais_livraison
                FROM commande c
                JOIN client cl ON cl.id_client = c.id_client
                WHERE {where_sql}
                  AND c.frais_livraison > 0
                ORDER BY c.date_paiement DESC
                """,
                parametres
            )

            frais_livraison = [
                {
                    'commande': ligne[0],
                    'client': ligne[1],
                    'date': ligne[2],
                    'montant': ligne[3],
                }
                for ligne in cursor.fetchall()
            ]

        total_produits = sum(
            (ligne['montant'] for ligne in ventes_produits),
            Decimal('0')
        )

        total_livraison = sum(
            (ligne['montant'] for ligne in frais_livraison),
            Decimal('0')
        )

        context = {
            **self.admin_site.each_context(request),
            'title': 'Suivi des ventes',
            'ventes_produits': ventes_produits,
            'frais_livraison': frais_livraison,
            'total_produits': total_produits,
            'total_livraison': total_livraison,
            'total_encaisse': total_produits + total_livraison,
            'produits': Produit.objects.all().order_by('nom'),
            'date_debut': date_debut,
            'date_fin': date_fin,
            'produit_selectionne': produit_id,
            'erreur': erreur,
            'opts': self.model._meta,
        }

        return render(
            request,
            'admin/boutique/commande/suivi_ventes.html',
            context
        )

def tableau_de_bord(request):
    total_commandes = Commande.objects.count()

    commandes_attente = Commande.objects.filter(
        statut_commande='EN_ATTENTE'
    ).count()

    commandes_confirmees = Commande.objects.filter(
        statut_commande='CONFIRMEE'
    ).count()

    commandes_pretes = Commande.objects.filter(
        statut_commande='PRETE'
    ).count()

    produits_disponibles = Produit.objects.filter(
        actif=True,
        quantite_stock__gt=0
    ).count()

    produits_rupture = Produit.objects.filter(
        actif=True,
        quantite_stock=0
    ).count()

    total_clients = Client.objects.count()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(lc.quantite * lc.prix_unitaire), 0)
            FROM commande c
            JOIN ligne_commande lc
                ON lc.id_commande = c.id_commande
            WHERE c.statut_paiement = 'PAYE'
        """)
        total_ventes = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(frais_livraison), 0)
            FROM commande
            WHERE statut_paiement = 'PAYE'
        """)
        total_frais = cursor.fetchone()[0]

        cursor.execute("""
            SELECT c.id_commande, cl.nom, c.date_commande,
                   c.statut_commande, c.statut_paiement
            FROM commande c
            JOIN client cl ON cl.id_client = c.id_client
            ORDER BY c.date_commande DESC
            LIMIT 8
        """)
        commandes_recentes = cursor.fetchall()

    context = {
        **admin.site.each_context(request),
        'title': 'Tableau de bord',
        'total_commandes': total_commandes,
        'commandes_attente': commandes_attente,
        'commandes_confirmees': commandes_confirmees,
        'commandes_pretes': commandes_pretes,
        'produits_disponibles': produits_disponibles,
        'produits_rupture': produits_rupture,
        'total_clients': total_clients,
        'total_ventes': total_ventes,
        'total_frais': total_frais,
        'total_encaisse': total_ventes + total_frais,
        'commandes_recentes': commandes_recentes,
    }

    return render(request, 'admin/tableau_de_bord.html', context)
