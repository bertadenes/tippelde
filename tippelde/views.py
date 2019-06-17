from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from tippelde.models import Game, Bet
from tippelde.forms import Bet_form, Game_form, Game_update_form
from tippelde.extras import player_group, is_manager


# Create your views here.
class Game_delete(DeleteView):
    model = Game
    success_url = reverse_lazy('management/games/')


class Bet_delete(DeleteView):
    model = Bet
    success_url = reverse_lazy('guesses')


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
    if player_group(request.user) and game.kickoff > now:
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
    if is_manager(request.user):
        if game.kickoff >= now:
            if request.method == 'POST':
                form = Game_form(request.POST)
                if form.is_valid():
                    Game.objects.filter(id=game_id).update(home_team=form.cleaned_data['home_team'],
                                                           away_team=form.cleaned_data['away_team'],
                                                           kickoff=form.cleaned_data['kickoff'])
                    return HttpResponseRedirect('/management/games/')
            else:
                form = Game_form(instance=game)
        else:
            if request.method == 'POST':
                form = Game_update_form(request.POST)
                if form.is_valid():
                    Game.objects.filter(id=game_id).update(result=form.cleaned_data['result'])
                    return HttpResponseRedirect('/management/games/')
            else:
                form = Game_update_form(instance=game)
        context['form'] = form
    return render(request, 'details.html', context)


@login_required
@user_passes_test(is_manager)
def manage(request):
    return render(request, 'management/home.html')


@login_required
@user_passes_test(is_manager)
def manage_games(request):
    now = timezone.now()
    upcoming = Game.objects.order_by('kickoff').filter(kickoff__gte=now)
    results = Game.objects.order_by('-kickoff').exclude(kickoff__gte=now)
    context = {'results': results, 'upcoming': upcoming}
    if request.method == 'POST':
        form = Game_form(request.POST)
        if form.is_valid():
            game = Game.objects.create_Game(home=form.cleaned_data['home_team'], away=form.cleaned_data['away_team'],
                                            kickoff=form.cleaned_data['due'], due=form.cleaned_data['due'])
            game.save()
            return HttpResponseRedirect('/games/')
    else:
        form = Game_form()
    context['form'] = form
    print("Renders this")
    return render(request, 'management/games.html', context)


@login_required
@user_passes_test(is_manager)
def evaluate(request, game_id):
    game = Game.objects.get(id=game_id)
    if game.result is None or game.evaluated:
        return HttpResponseRedirect('/management/games/')
    bets = Bet.objects.filter(game=game)
    context = {'game': game, 'bets': bets}
    if request.method == 'POST':
        game.evaluate()
        messages.info(request, "Bets for this game have been evaluated.")
        return HttpResponseRedirect('/management/games/')
    else:
        return render(request, 'evaluate.html', context)
