from django import forms


class Bet_form(forms.Form):
    CHOICES = [
    (0, ("Draw")),
    (1, ("Home")),
    (2, ("Away")),
    ]
    outcome = forms.ChoiceField(choices=CHOICES, required=True)
