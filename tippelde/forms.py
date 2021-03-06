import datetime
from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from tippelde.models import Bet, Game, Tournament, StringQuestion, StringAnswer, SurvivorRound, SurvivorGuess, Post
from tippelde.widgets import ListTextWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', )
        widgets = {'content': TinyMCE(attrs={'cols': 80, 'rows': 20})}

    class Media:
        js = ('/site_media/static/tiny_mce/tinymce.min.js',)


class Bet_form(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ('home_guess', 'away_guess', 'mult4', )
        labels = {'mult4': '4x bonus'}


class Game_form(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('home_team', 'away_team', 'due', 'tournament', 'multiplier', 'matchday')

    def __init__(self, *args, **kwargs):
        teams = (
                'Budapest Honvéd FC',
                'MTK Budapest FC',
                'Diósgyőri VTK',
                'Ferencvárosi TC',
                'Budafoki MTE',
                'Kisvárda Master Good',
                'Mezőkövesd Zsóry FC',
                'MOL Fehérvár FC',
                'Paksi FC',
                'Puskás Akadémia FC',
                'Újpest FC',
                'Zalaegerszegi TE)'
                )
        super(Game_form, self).__init__(*args, **kwargs)

        # the "name" parameter will allow you to use the same widget more than once in the same
        # form, not setting this parameter differently will cuse all inputs display the
        # same list.
        self.fields['home_team'].widget = ListTextWidget(data_list=teams, name="Home Team")
        self.fields['away_team'].widget = ListTextWidget(data_list=teams, name="Away Team")

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
    # name = forms.ChoiceField(choices=[(t.name, t.name) for t in Tournament.objects.all()])
    tables = forms.MultipleChoiceField(choices=[(t.name, t.name) for t in Tournament.objects.all()],
                                       widget=forms.CheckboxSelectMultiple)


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


class SurvivorRoundForm(forms.ModelForm):
    class Meta:
        model = SurvivorRound
        fields = ('matchday', 'due', 'tournament', 'name', 'description')


class SurvivorRoundUpdateForm(forms.ModelForm):
    class Meta:
        model = SurvivorRound
        fields = ('correct_answer', )


class SurvivorGuessForm(forms.ModelForm):
    """ teams of 2020-21:
    Budapest Honvéd FC
    MTK Budapest FC
    Diósgyőri VTK
    Ferencvárosi TC
    Budafoki MTE
    Kisvárda Master Good
    Mezőkövesd Zsóry FC
    MOL Fehérvár FC
    Paksi FC
    Puskás Akadémia FC
    Újpest FC
    Zalaegerszegi TE
    """
    class Meta:
        model = SurvivorGuess
        fields = ('answer', )
        TEAMS = (
            ('', 'Select'),
            ('Budapest Honvéd FC', 'Budapest Honvéd FC'),
            ('MTK Budapest FC', 'MTK Budapest FC'),
            ('Diósgyőri VTK', 'Diósgyőri VTK'),
            ('Ferencvárosi TC', 'Ferencvárosi TC'),
            ('Budafoki MTE', 'Budafoki MTE'),
            ('Kisvárda Master Good', 'Kisvárda Master Good'),
            ('Mezőkövesd Zsóry FC', 'Mezőkövesd Zsóry FC'),
            ('MOL Fehérvár FC', 'MOL Fehérvár FC'),
            ('Paksi FC', 'Paksi FC'),
            ('Puskás Akadémia FC', 'Puskás Akadémia FC'),
            ('Újpest FC', 'Újpest FC'),
            ('Zalaegerszegi TE', 'Zalaegerszegi TE')
        )
        widgets = {
            'answer': forms.Select(choices=TEAMS, attrs={'class': 'form-control'}),
        }


# class NQForm(forms.ModelForm):
#     class Meta:
#         model = NumericQuestion
#         fields = ('name', 'description', 'due', 'award', 'changes', 'penalty', 'tournament')
#
#
# class NQ_update_form(forms.ModelForm):
#     class Meta:
#         model = NumericQuestion
#         fields = ('correct_answer', )
#
#
# class NAForm(forms.ModelForm):
#     class Meta:
#         model = NumericAnswer
#         fields = ('answer', )
