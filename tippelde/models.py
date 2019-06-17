from django.db import models
from django.conf import settings
from tippelde.exceptions import EvaluatedException


# Create your models here.
# Custom Managers
# Tournament and score are for question organizing
# class Tournament_Manager(models.Manager):
#     def create_Tournament(self, name):
#         tour = self.create(name=name)
#         return tour
#
#
# class Score_Manager(models.Manager):
#     def create_Score(self, user, tour):
#         score = self.create(user=user, tournament=tour)
#         return score


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    # objects = Tournament_Manager

    def __str__(self):
        return self.name


class Score(models.Model):
    score = models.SmallIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    # objects = Score_Manager


# Game-Bet is the first pair of objects
class Game_Manager(models.Manager):
    def create_Game(self, home, away, kickoff, due):
        game = self.create(home_team=home, away_team=away, kickoff=kickoff, due=due)
        return game


class Bookmaker(models.Manager):
    def create_Bet(self, user, game, value):
        bet = self.create(user=user, game=game, value=value)
        if not Score.objects.filter(user=user, tournament=game.tournament).exists():
            score = Score.objects.create(user=user, tournament=game.tournament)
            score.save()
        return bet


# Abstraction object to hold basic question attributes
class Question(models.Model):
    due = models.DateTimeField()
    name = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True, max_length=1000)
    award = models.PositiveSmallIntegerField(default=10)
    changed = models.PositiveSmallIntegerField(default=0)
    penalty = models.PositiveSmallIntegerField(default=3)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.CASCADE)
    evaluated = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Game(Question):
    home_team = models.CharField(max_length=200)
    away_team = models.CharField(max_length=200)
    kickoff = models.DateTimeField()
    outcomes = [(0, "Draw"), (1, "Home"), (2, "Away")]
    result = models.SmallIntegerField(blank=True, null=True, choices=outcomes)
    objects = Game_Manager()

    def __str__(self):
        return "{0:s}-{1:s}".format(self.home_team, self.away_team)

    def get_result(self):
        outcomes = ["Draw", "Home", "Away"]
        try:
            return "{0:s}".format(outcomes[self.result])
        except TypeError:
            return "Not registered"

    def evaluate(self):
        if self.tournament is None:
            Game.objects.filter(id=self.id).update(evaluated=True)
            return
        if self.evaluated:
            raise EvaluatedException("This game has already been evaluated.")
        bets = Bet.objects.filter(game=self)
        for bet in bets:
            if bet.value == self.result:
                Score.objects.filter(user=bet.user, tournament=self.tournament).update(score=models.F('score')+self.award)
        Game.objects.filter(id=self.id).update(evaluated=True)
        return


class Bet(models.Model):
    outcomes = [(0, "Draw"), (1, "Home"), (2, "Away")]
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=0, choices=outcomes, verbose_name='outcome')
    objects = Bookmaker()

    def __str__(self):
        outcomes = ["Draw", "Home", "Away"]
        return "{0:s} {1:s}".format(self.game.__str__(), outcomes[self.value])

    def get_outcome(self):
        outcomes = ["Draw", "Home", "Away"]
        return "{0:s}".format(outcomes[self.value])
