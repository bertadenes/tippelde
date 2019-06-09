from django.shortcuts import render
from django.utils import timezone
from tippelde.models import Game, Bet
from django.http import HttpResponse

# Create your views here.


def index(request):
    return render(request, 'index.html')


def games(request):
    now = timezone.now()
    upcoming = Game.objects.order_by('kickoff').filter(kickoff__gte=now)
    results = Game.objects.order_by('-kickoff').exclude(kickoff__gte=now)
    context = {'results': results, 'upcoming': upcoming}
    return render(request, 'games.html', context)


def guesses(request):
    guesses = Bet.objects.filter(user=request.user)
    context = {'guesses': guesses}
    return render(request, 'guesses.html', context)


def detail(request, game_id):
    return HttpResponse("You're looking at question {:s}.".format(game_id))