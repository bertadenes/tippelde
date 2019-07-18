from django.contrib import admin
from tippelde.models import Game, Bet, Tournament, Score, StringQuestion, StringAnswer

# Register your models here.
admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(Tournament)
admin.site.register(Score)
admin.site.register(StringQuestion)
admin.site.register(StringAnswer)
