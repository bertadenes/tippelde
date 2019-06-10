from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from tippelde.models import Game, Bet
from tippelde.forms import Bet_form, Game_form
from tippelde.extras import player_group, is_manager

# Create your views here.


def index(request):
    return render(request, 'index.html')


def games(request):
    now = timezone.now()
    upcoming = Game.objects.order_by('kickoff').filter(kickoff__gte=now)
    results = Game.objects.order_by('-kickoff').exclude(kickoff__gte=now)
    context = {'results': results, 'upcoming': upcoming}
    return render(request, 'games.html', context)


@login_required
@user_passes_test(player_group)
def guesses(request):
    now = timezone.now()
    upcoming = Bet.objects.filter(user=request.user).filter(game__kickoff__gte=now).order_by('game__kickoff')
    results = Bet.objects.filter(user=request.user).exclude(game__kickoff__gte=now).order_by('-game__kickoff')
    context = {'results': results, 'upcoming': upcoming}
    return render(request, 'guesses.html', context)


@login_required
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
                    return HttpResponseRedirect('/guesses/')
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


@login_required
@user_passes_test(is_manager)
def manage(request):
    context = {}
    if request.method == 'POST':
        form = Game_form(request.POST)
        if form.is_valid():
            game = Game.objects.create_Game(home=form.cleaned_data['home_team'], away=form.cleaned_data['away_team'],
                                            kickoff=form.cleaned_data['kickoff'])
            game.save()
            return HttpResponseRedirect('/games/')
    else:
        form = Game_form()
    context['form'] = form
    return render(request, 'management.html', context)
