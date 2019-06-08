from django.shortcuts import render
from tippelde.models import Game, Bet
# from django.http import HttpResponse

# Create your views here.


def index(request):
    return render(request, 'index.html')


def games(request):
    games = Game.objects.order_by('-kickoff')
    context = {'games': games}
    return render(request, 'games.html', context)


def guesses(request):
    guesses = Bet.objects.filter(user=request.user)
    context = {'guesses': guesses}
    return render(request, 'guesses.html', context)