from django.db import models
from django.conf import settings


# Create your models here.
class Game(models.Model):
    home_team = models.CharField(max_length=200)
    away_team = models.CharField(max_length=200)
    kickoff = models.DateTimeField()
    result = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return "{0:s}-{1:s}".format(self.home_team, self.away_team)

    def get_result(self):
        outcomes = ["Draw", "Home", "Away"]
        try:
            return "{0:s}".format(outcomes[self.result])
        except TypeError:
            return "Not registered"


class Bookmaker(models.Manager):
    def create_Bet(self, user, game, value):
        bet = self.create(user=user, game=game, value=value)
        return bet


class Bet(models.Model):
    outcomes = [
        (0, ("Draw")),
        (1, ("Home")),
        (2, ("Away")),
    ]
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
