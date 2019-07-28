from django.contrib import admin
from tippelde.models import Game, Bet, Tournament, Score, StringQuestion, StringAnswer, SurvivorRound, SurvivorGuess, \
    Post

# Register your models here.
admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(Tournament)
admin.site.register(Score)
admin.site.register(StringQuestion)
admin.site.register(StringAnswer)
admin.site.register(SurvivorRound)
admin.site.register(SurvivorGuess)
admin.site.register(Post)
