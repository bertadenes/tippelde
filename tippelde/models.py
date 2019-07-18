from django.db import models
from django.conf import settings
from tippelde.exceptions import EvaluatedException
from tippelde.extras import ev


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
    name = models.CharField(max_length=200, unique=True)
    # objects = Tournament_Manager

    def __str__(self):
        return self.name


class Score(models.Model):
    score = models.SmallIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    # objects = Score_Manager

    def __str__(self):
        return "{0:s} in {1:s}".format(self.user.__str__(), self.tournament.__str__())


# Game-Bet is the first pair of objects
class Game_Manager(models.Manager):
    def create_Game(self, home, away, kickoff, due):
        game = self.create(home_team=home, away_team=away, kickoff=kickoff, due=due)
        return game


class Bookmaker(models.Manager):
    def create_Bet(self, user, game, home_guess, away_guess):
        bet = self.create(user=user, game=game, home_guess=home_guess, away_guess=away_guess)
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
    # obsolete with storing the actual score
    # outcomes = [(0, "Draw"), (1, "Home"), (2, "Away")]
    # result = models.SmallIntegerField(blank=True, null=True, choices=outcomes)
    home_goals = models.SmallIntegerField(blank=True, null=True)
    away_goals = models.SmallIntegerField(blank=True, null=True)
    objects = Game_Manager()
    multiplier = models.SmallIntegerField(default=1)

    def __str__(self):
        return "{0:s}-{1:s}".format(self.home_team, self.away_team)

    def get_result(self):
        if self.home_goals is not None and self.away_goals is not None:
            if self.home_goals == self.away_goals:
                return "Draw"
            elif self.home_goals > self.away_goals:
                return "Home"
            elif self.home_goals < self.away_goals:
                return "Away"
        else:
            return "Not registered"
        # obsolete with storing the actual score
        # outcomes = ["Draw", "Home", "Away"]
        # try:
        #     return "{0:s}".format(outcomes[self.result])
        # except TypeError:
        #     return "Not registered"

    def evaluate(self):
        if self.tournament is None:
            Game.objects.filter(id=self.id).update(evaluated=True)
            return
        if self.evaluated:
            raise EvaluatedException("This game has already been evaluated.")
        bets = Bet.objects.filter(game=self)
        for bet in bets:
            # obsolete with storing the actual score
            # if bet.value == self.result:
            self.award = ev(self.home_goals, self.away_goals, bet.home_guess, bet.away_guess) * self.multiplier
            Score.objects.filter(user=bet.user, tournament=self.tournament).update(score=models.F('score')+self.award)
        Game.objects.filter(id=self.id).update(evaluated=True)
        return


class AnswerManager(models.Manager):
    def create_answer(self, user, question, answer):
        bet = self.create(user=user, question=question, answer=answer)
        if not Score.objects.filter(user=user, tournament=question.tournament).exists():
            score = Score.objects.create(user=user, tournament=question.tournament)
            score.save()
        return bet


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    objects = AnswerManager()

    class Meta:
        abstract = True

    def __str__(self):
        return "Answer by {0:s}".format(self.user.__str__())


class Bet(Answer):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    home_guess = models.SmallIntegerField()
    away_guess = models.SmallIntegerField()
    # obsolete with storing the actual score
    # outcomes = [(0, "Draw"), (1, "Home"), (2, "Away")]
    # value = models.SmallIntegerField(default=0, choices=outcomes, verbose_name='outcome')

    objects = Bookmaker()

    def __str__(self):
        return "{0:s} {1:d}-{2:d} by {3:s}".format(self.game.__str__(), self.home_guess,
                                                   self.away_guess, self.user.__str__())

    def get_outcome(self):
        if self.home_guess == self.away_guess:
            return "Draw"
        elif self.home_guess > self.away_guess:
            return "Home"
        elif self.home_guess < self.away_guess:
            return "Away"


class StringQuestion(Question):
    correct_answer = models.CharField(blank=True, null=True, max_length=200)


class StringAnswer(Answer):
    question = models.ForeignKey(StringQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
