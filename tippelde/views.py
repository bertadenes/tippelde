from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
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
        if Bet.objects.filter(user=request.user, game=game).exists():
            if request.method == 'POST':
                form = Bet_form(request.POST)
                if form.is_valid():
                    Bet.objects.filter(user=request.user, game=game).update(value=form.cleaned_data['value'])
            else:
                bet = Bet.objects.filter(user=request.user, game=game).get()
                form = Bet_form(instance=bet)
        else:
            if request.method == 'POST':
                form = Bet_form(request.POST)
                if form.is_valid():
                    bet = Bet.objects.create_Bet(game=game, user=request.user, value=form.cleaned_data['value'])
                    bet.save()
                    return HttpResponseRedirect('/guesses/')
            else:
                form = Bet_form()
        context['form'] = form
    return render(request, 'details.html', context)
