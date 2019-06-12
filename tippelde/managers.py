from django.db import models


class Game_Manager(models.Manager):
    def create_Game(self, home, away, kickoff):
        game = self.create(home_team=home, away_team=away, kickoff=kickoff)
        return game


class Bookmaker(models.Manager):
    def create_Bet(self, user, game, value):
        bet = self.create(user=user, game=game, value=value)
        return bet
