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


class Bet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=0)

    def __str__(self):
        return "{0:s} {1:d}".format(self.game.__str__(), self.value)
