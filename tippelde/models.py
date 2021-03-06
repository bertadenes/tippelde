from django.db import models
from django.conf import settings
from tinymce.models import HTMLField
from tippelde.exceptions import EvaluatedException, CannotMultiply
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
class Post(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=10000)
    added = models.DateTimeField()


class Tournament(models.Model):
    name = models.CharField(max_length=200, unique=True)
    # objects = Tournament_Manager

    def __str__(self):
        return self.name


class Score(models.Model):
    score = models.SmallIntegerField(default=0)
    mult4left = models.SmallIntegerField(default=5)
    survivor_fails = models.SmallIntegerField(default=0)
    survivor_died = models.SmallIntegerField(default=-1)
    double_team = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    # objects = Score_Manager

    def __str__(self):
        return "{0:s} in {1:s}".format(self.user.__str__(), self.tournament.__str__())


# Game-Bet is the first pair of objects
class Game_Manager(models.Manager):
    def create_Game(self, home, away, kickoff, due, tour, mult, md):
        game = self.create(home_team=home, away_team=away, kickoff=kickoff, due=due, tournament=tour, multiplier=mult,
                           matchday=md)
        return game


class Bookmaker(models.Manager):
    def create_Bet(self, user, game, home_guess, away_guess, mult4):
        exclude = ['Ferencvárosi TC', 'MOL Fehérvár FC']
        if not Score.objects.filter(user=user, tournament=game.tournament).exists():
            score = Score.objects.create(user=user, tournament=game.tournament)
            score.save()
        else:
            score = Score.objects.get(user=user, tournament=game.tournament)
        if mult4 and score.mult4left == 0:
            raise CannotMultiply("You have no tokens left.")
        elif mult4:
            if game.home_team in exclude or game.away_team in exclude:
                raise CannotMultiply("The token cannot be applied for this game.")
            else:
                Score.objects.filter(user=user, tournament=game.tournament).update(mult4left=models.F('mult4left')-1)
        bet = self.create(user=user, game=game, home_guess=home_guess, away_guess=away_guess, mult4=mult4)
        return bet


# Abstraction object to hold basic question attributes
class Question(models.Model):
    due = models.DateTimeField()
    name = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True, max_length=1000)
    award = models.PositiveSmallIntegerField(default=10)
    changes = models.PositiveSmallIntegerField(default=0)
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
    matchday = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return "{0:s}-{1:s}".format(self.home_team, self.away_team)

    def get_result(self):
        if self.home_goals is not None and self.away_goals is not None:
            return "{0:d}-{1:d}".format(self.home_goals, self.away_goals)
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
            award = ev(self.home_goals, self.away_goals, bet.home_guess, bet.away_guess) * self.multiplier
            if bet.mult4:
                award = award * 4
            score = Score.objects.get(user=bet.user, tournament=self.tournament)
            if score.double_team in [self.home_team, self.away_team]:
                award = award * 2
            Score.objects.filter(user=bet.user, tournament=self.tournament).update(score=models.F('score')+award)
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
    changed = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return "Answer by {0:s}".format(self.user.__str__())


class Bet(Answer):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    home_guess = models.SmallIntegerField()
    away_guess = models.SmallIntegerField()
    mult4 = models.BooleanField(default=False)
    # obsolete with storing the actual score
    # outcomes = [(0, "Draw"), (1, "Home"), (2, "Away")]
    # value = models.SmallIntegerField(default=0, choices=outcomes, verbose_name='outcome')

    objects = Bookmaker()

    def __str__(self):
        return "{0:s} {1:d}-{2:d} by {3:s}".format(self.game.__str__(), self.home_guess,
                                                   self.away_guess, self.user.__str__())

    def get_outcome(self):
        return "{0:d}-{1:d}".format(self.home_guess, self.away_guess)


class StringQuestion(Question):
    correct_answer = models.CharField(blank=True, null=True, max_length=200)

    def evaluate(self):
        if self.tournament is None:
            StringQuestion.objects.filter(id=self.id).update(evaluated=True)
            return
        if self.evaluated:
            raise EvaluatedException("This question has already been evaluated.")
        answers = StringAnswer.objects.filter(question=self)
        for a in answers:
            if a.answer == self.correct_answer:
                award = self.award - (a.changed * self.penalty)
                Score.objects.filter(user=a.user, tournament=self.tournament).update(score=models.F('score')+award)
        StringQuestion.objects.filter(id=self.id).update(evaluated=True)
        return


class StringAnswer(Answer):
    question = models.ForeignKey(StringQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)

    def __str__(self):
        return "Answer to {1:s} by {0:s}".format(self.user.__str__(), self.question.__str__())


class SurvivorRound(Question):
    matchday = models.PositiveSmallIntegerField(unique=True)
    correct_answer = models.CharField(blank=True, null=True, max_length=200)

    def evaluate(self):
        if self.tournament is None:
            SurvivorRound.objects.filter(id=self.id).update(evaluated=True)
            return
        if self.evaluated:
            raise EvaluatedException("This question has already been evaluated.")
        answers = SurvivorGuess.objects.filter(question=self)
        for a in answers:
            teams = self.correct_answer.split(',')
            if a.answer in teams:
                if Score.objects.filter(user=a.user, tournament=self.tournament).values('survivor_fails') < 6:
                    award = 20
                else:
                    award = 10
                Score.objects.filter(user=a.user, tournament=self.tournament).update(score=models.F('score') + award)
            else:
                Score.objects.filter(user=a.user, tournament=self.tournament).\
                    update(survivor_fails=models.F('survivor_fails') + 1)
                if Score.objects.filter(user=a.user, tournament=self.tournament).values('survivor_fails') == 6:
                    Score.objects.filter(user=a.user, tournament=self.tournament).update(survivor_died=self.matchday)
        SurvivorRound.objects.filter(id=self.id).update(evaluated=True)
        return


class SurvivorGuess(Answer):
    question = models.ForeignKey(SurvivorRound, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)

    def __str__(self):
        return "{0:s} in round {1:d} by {2:s}".format(self.answer, self.question.matchday, self.user.__str__())


# class NumericQuestion(Question):
#     correct_answer = models.PositiveSmallIntegerField(blank=True, null=True)
#
#     def evaluate(self):
#         if self.tournament is None:
#             NumericQuestion.objects.filter(id=self.id).update(evaluated=True)
#             return
#         if self.evaluated:
#             raise EvaluatedException("This question has already been evaluated.")
#         answers = NumericAnswer.objects.filter(question=self)
#         for a in answers:
#             if a.answer == self.correct_answer:
#                 award = self.award - (a.changed * self.penalty)
#                 Score.objects.filter(user=a.user, tournament=self.tournament).update(score=models.F('score')+award)
#         NumericQuestion.objects.filter(id=self.id).update(evaluated=True)
#         return
#
#
# class NumericAnswer(Answer):
#     question = models.ForeignKey(NumericQuestion, on_delete=models.CASCADE)
#     answer = models.PositiveSmallIntegerField()
#
#     def __str__(self):
#         return "Answer to {1:s} by {0:s}".format(self.user.__str__(), self.question.__str__())
