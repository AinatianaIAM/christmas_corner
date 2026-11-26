
from django import forms


class CommandeForm(forms.Form):

    nom = forms.CharField(
        max_length=100,
        label="Nom complet"
    )

    telephone = forms.CharField(
        max_length=20,
        label="Téléphone"
    )

    email = forms.EmailField(
        max_length=150,
        label="Adresse e-mail"
    )

    mode_reception = forms.ChoiceField(
        choices=[
            ('RETRAIT', 'Retrait en boutique'),
            ('LIVRAISON', 'Livraison'),
        ],
        label="Mode de réception",
        widget=forms.Select(attrs={'id': 'mode_reception'})
    )

    adresse_livraison = forms.CharField(
        max_length=255,
        required=False,
        label="Adresse de livraison"
    )

    date_reception_prevue = forms.DateField(
        required=False,
        label="Date de réception souhaitée",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean(self):
        cleaned_data = super().clean()

        mode = cleaned_data.get('mode_reception')
        adresse = cleaned_data.get('adresse_livraison')

        if mode == 'LIVRAISON' and not adresse:
            self.add_error(
                'adresse_livraison',
                "L'adresse est obligatoire pour une livraison."
            )

        if mode == 'RETRAIT':
            cleaned_data['adresse_livraison'] = None

        return cleaned_data
