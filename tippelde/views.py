from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from tippelde.models import Game, Bet
from tippelde.forms import Bet_form

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


def details(request, game_id):
    now = timezone.now()
    game = Game.objects.get(id=game_id)
    context = {'game': game}
    if game.kickoff > now:
        if request.method == 'POST':
            form = Bet_form(request.POST)
        else:
            form = Bet_form()
        context['form'] = form
    return render(request, 'details.html', context)
