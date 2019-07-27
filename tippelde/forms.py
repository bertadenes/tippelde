import datetime
from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from tippelde.models import Bet, Game, Tournament, StringQuestion, StringAnswer, NumericQuestion, NumericAnswer


class Bet_form(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ('home_guess', 'away_guess', 'mult4', )


class Game_form(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('home_team', 'away_team', 'due', 'tournament', 'multiplier', 'matchday')

    def clean_kickoff(self):
        now = timezone.now()
        ko = self.cleaned_data['kickoff']
        if ko < now:
            raise ValidationError("Cannot add past games.")
        if Game.objects.filter(home_team=self.cleaned_data['home_team'], away_team=self.cleaned_data['away_team'])\
                .filter(kickoff__gte=self.cleaned_data['kickoff'] - datetime.timedelta(days=1))\
                .filter(kickoff__lte=self.cleaned_data['kickoff'] + datetime.timedelta(days=1)).exists():
            raise ValidationError("There is a similar entry.")
        return ko


class Game_update_form(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('home_goals', 'away_goals')


class Tournament_form(forms.Form):
    name = forms.ChoiceField(choices=[(t.name, t.name) for t in Tournament.objects.all()])
    # name = forms.TextInput()


class Evaluate(forms.Form):
    home_goals = forms.IntegerField()
    away_goals = forms.IntegerField()
    home_guess = forms.IntegerField()
    away_guess = forms.IntegerField()


class SQForm(forms.ModelForm):
    class Meta:
        model = StringQuestion
        fields = ('name', 'description', 'due', 'award', 'changes', 'penalty', 'tournament')


class SQ_update_form(forms.ModelForm):
    class Meta:
        model = StringQuestion
        fields = ('correct_answer', )


class SAForm(forms.ModelForm):
    class Meta:
        model = StringAnswer
        fields = ('answer', )


class NQForm(forms.ModelForm):
    class Meta:
        model = NumericQuestion
        fields = ('name', 'description', 'due', 'award', 'changes', 'penalty', 'tournament')


class NQ_update_form(forms.ModelForm):
    class Meta:
        model = NumericQuestion
        fields = ('correct_answer', )


class NAForm(forms.ModelForm):
    class Meta:
        model = NumericAnswer
        fields = ('answer', )
