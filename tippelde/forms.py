from django import forms
from tippelde.models import Bet


class Bet_form(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ('value', )
    outcomes = [
    (0, ("Draw")),
    (1, ("Home")),
    (2, ("Away")),
    ]
