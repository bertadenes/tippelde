from django import forms
from tippelde.models import Bet, Game


class Bet_form(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ('value', )


class Game_form(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('home_team', 'away_team', 'kickoff', )
