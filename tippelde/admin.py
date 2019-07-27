from django.contrib import admin
from tippelde.models import Game, Bet, Tournament, Score, StringQuestion, StringAnswer
# from tippelde.models import NumericQuestion, NumericAnswer

# Register your models here.
admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(Tournament)
admin.site.register(Score)
admin.site.register(StringQuestion)
admin.site.register(StringAnswer)
# admin.site.register(NumericQuestion)
# admin.site.register(NumericAnswer)
