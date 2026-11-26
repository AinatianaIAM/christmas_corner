
from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('produit/<int:id>/', views.detail_produit, name='detail_produit'),
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:id>/', views.ajouter_panier, name='ajouter_panier'),
    path('panier/modifier/<int:id>/', views.modifier_panier, name='modifier_panier'),
    path('panier/supprimer/<int:id>/', views.supprimer_panier, name='supprimer_panier'),
    path('commande/', views.passer_commande, name='passer_commande'),
    path('commande/confirmation/<int:id>/', views.confirmation_commande, name='confirmation_commande'),
]
