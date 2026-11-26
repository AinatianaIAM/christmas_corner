
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Produit, Categorie, Client, Commande
from django.db import transaction, connection
from .forms import CommandeForm

def accueil(request):
    produits = Produit.objects.filter(actif=True)[:4]

    return render(request, 'boutique/accueil.html', {
        'produits': produits
    })


def catalogue(request):
    produits = Produit.objects.filter(actif=True)
    categories = Categorie.objects.all()

    categorie_id = request.GET.get('categorie')

    if categorie_id:
        produits = produits.filter(id_categorie_id=categorie_id)

    return render(request, 'boutique/catalogue.html', {
        'produits': produits,
        'categories': categories,
        'categorie_selectionnee': categorie_id
    })


def detail_produit(request, id):
    produit = get_object_or_404(
        Produit,
        id_produit=id,
        actif=True
    )

    return render(request, 'boutique/detail_produit.html', {
        'produit': produit
    })


def panier(request):
    panier_session = request.session.get('panier', {})
    produits_panier = []
    total = 0

    for produit_id, quantite in panier_session.items():
        produit = get_object_or_404(
            Produit,
            id_produit=int(produit_id),
            actif=True
        )

        sous_total = produit.prix * quantite
        total += sous_total

        produits_panier.append({
            'produit': produit,
            'quantite': quantite,
            'sous_total': sous_total,
        })

    return render(request, 'boutique/panier.html', {
        'produits_panier': produits_panier,
        'total': total,
    })


@require_POST
def ajouter_panier(request, id):
    produit = get_object_or_404(
        Produit,
        id_produit=id,
        actif=True
    )

    quantite = int(request.POST.get('quantite', 1))

    if quantite < 1 or quantite > produit.quantite_stock:
        return redirect('detail_produit', id=id)

    panier_session = request.session.get('panier', {})
    cle = str(id)

    nouvelle_quantite = panier_session.get(cle, 0) + quantite

    if nouvelle_quantite <= produit.quantite_stock:
        panier_session[cle] = nouvelle_quantite
        request.session['panier'] = panier_session

    return redirect('panier')


@require_POST
def modifier_panier(request, id):
    panier_session = request.session.get('panier', {})
    cle = str(id)

    if cle in panier_session:
        try:
            quantite = int(request.POST.get('quantite', 1))
        except (ValueError, TypeError):
            return redirect('panier')

        produit = get_object_or_404(Produit, id_produit=id, actif=True)

        if quantite <= 0:
            del panier_session[cle]
        elif quantite <= produit.quantite_stock:
            panier_session[cle] = quantite

        request.session['panier'] = panier_session

    return redirect('panier')


@require_POST
def supprimer_panier(request, id):
    panier_session = request.session.get('panier', {})
    panier_session.pop(str(id), None)
    request.session['panier'] = panier_session

    return redirect('panier')


def passer_commande(request):
    panier_session = request.session.get('panier', {})

    if not panier_session:
        return redirect('panier')

    form = CommandeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        # Vérifier les quantités du panier
        try:
            articles = {
                int(produit_id): int(quantite)
                for produit_id, quantite in panier_session.items()
            }
        except (ValueError, TypeError):
            form.add_error(None, "Le contenu du panier est invalide.")
            return render(request, 'boutique/commande.html', {'form': form})

        if any(quantite <= 0 for quantite in articles.values()):
            form.add_error(None, "Une quantité du panier est invalide.")
            return render(request, 'boutique/commande.html', {'form': form})

        with transaction.atomic():

            # Récupérer les produits et vérifier leur stock
            produits = Produit.objects.select_for_update().filter(
                id_produit__in=articles.keys()
            ).order_by('id_produit')

            produits_dict = {
                produit.id_produit: produit
                for produit in produits
            }

            erreur_stock = False

            for produit_id, quantite in articles.items():
                produit = produits_dict.get(produit_id)

                if (
                    produit is None
                    or not produit.actif
                    or produit.quantite_stock < quantite
                ):
                    erreur_stock = True
                    break

            if erreur_stock:
                form.add_error(
                    None,
                    "Un produit n'est plus disponible en quantité suffisante. "
                    "Vérifie ton panier."
                )

            else:
                # Créer ou retrouver le client grâce à son e-mail
                client, created = Client.objects.update_or_create(
                    email=form.cleaned_data['email'],
                    defaults={
                        'nom': form.cleaned_data['nom'],
                        'telephone': form.cleaned_data['telephone'],
                    }
                )

                # Créer la commande
                commande = Commande.objects.create(
                    id_client=client,
                    statut_commande='EN_ATTENTE',
                    mode_reception=form.cleaned_data['mode_reception'],
                    adresse_livraison=form.cleaned_data['adresse_livraison'],
                    date_reception_prevue=form.cleaned_data['date_reception_prevue'],
                    frais_livraison=0,
                    statut_paiement='NON_PAYE',
                )

                # Enregistrer les lignes de commande
                # Insertion SQL pour gérer la clé primaire composée
                with connection.cursor() as cursor:
                    for produit_id, quantite in articles.items():
                        produit = produits_dict[produit_id]

                        cursor.execute(
                            """
                            INSERT INTO ligne_commande
                            (id_commande, id_produit, quantite, prix_unitaire)
                            VALUES (%s, %s, %s, %s)
                            """,
                            [
                                commande.id_commande,
                                produit_id,
                                quantite,
                                produit.prix,
                            ]
                        )
        if erreur_stock:
            return render(request, 'boutique/commande.html', {
                'form': form
            })
        # Vider le panier après l'enregistrement
        request.session['panier'] = {}

        return redirect(
            'confirmation_commande',
            id=commande.id_commande
        )

    return render(request, 'boutique/commande.html', {
        'form': form
    })


def confirmation_commande(request, id):
    commande = get_object_or_404(Commande, id_commande=id)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(quantite * prix_unitaire), 0)
            FROM ligne_commande
            WHERE id_commande = %s
        """, [id])

        total = cursor.fetchone()[0]

    return render(request, 'boutique/confirmation.html', {
        'commande': commande,
        'total': total
    })
