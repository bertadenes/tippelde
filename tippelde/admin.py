from django.contrib import admin
from tippelde.models import Game, Bet, Tournament, Score

# Register your models here.
admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(Tournament)
admin.site.register(Score)
