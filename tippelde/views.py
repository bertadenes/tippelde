from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from tippelde.models import Game, Bet, Tournament, Score, StringQuestion, StringAnswer
from tippelde.forms import Bet_form, Game_form, Game_update_form, Tournament_form, Evaluate, SQForm, SAForm,\
    SQ_update_form
from tippelde.extras import player_group, is_manager, ev


# Create your views here.
class Game_delete(DeleteView):
    model = Game
    success_url = reverse_lazy('management/games/')


class Bet_delete(DeleteView):
    model = Bet
    success_url = reverse_lazy('guesses')


class SADel(DeleteView):
    model = StringAnswer
    success_url = reverse_lazy('guesses')


class SQDel(DeleteView):
    model = StringQuestion
    success_url = reverse_lazy('management/sq/')


def index(request):
    context = {}
    if request.method == "POST":
        form = Evaluate(request.POST)
        if form.is_valid():
            context['score'] = ev(form.cleaned_data['home_goals'], form.cleaned_data['away_goals'],
                                  form.cleaned_data['home_guess'], form.cleaned_data['away_guess'])
    else:
        form = Evaluate()
    context['form'] = form
    return render(request, 'index.html', context)


def games(request):
    now = timezone.now()
    upcoming = Game.objects.order_by('kickoff').filter(kickoff__gte=now)
    results = Game.objects.order_by('-kickoff').exclude(kickoff__gte=now)
    sqs = StringQuestion.objects.order_by('due').filter(due__gte=now)
    context = {'results': results, 'upcoming': upcoming, 'sqs': sqs}
    return render(request, 'games.html', context)


@login_required
@user_passes_test(player_group)
def guesses(request):
    now = timezone.now()
    upcoming = Bet.objects.filter(user=request.user).filter(game__kickoff__gte=now).order_by('game__kickoff')
    results = Bet.objects.filter(user=request.user).exclude(game__kickoff__gte=now).order_by('-game__kickoff')
    sas = StringAnswer.objects.filter(user=request.user).order_by('question__due')
    context = {'results': results, 'upcoming': upcoming, 'sas': sas}
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
                    Bet.objects.filter(user=request.user, game=game).update(home_guess=form.cleaned_data['home_guess'],
                                                                            away_guess=form.cleaned_data['away_guess'])
                    return HttpResponseRedirect('/guesses/')
            else:
                bet = Bet.objects.filter(user=request.user, game=game).get()
                form = Bet_form(instance=bet)
        else:
            if request.method == 'POST':
                form = Bet_form(request.POST)
                if form.is_valid():
                    bet = Bet.objects.create_Bet(game=game, user=request.user,
                                                 home_guess=form.cleaned_data['home_guess'],
                                                 away_guess=form.cleaned_data['away_guess'])
                    bet.save()
                    return HttpResponseRedirect('/guesses/')
            else:
                form = Bet_form()
        context['form'] = form
    elif game.kickoff < now:
        bets = Bet.objects.filter(game=game)
        context['bets'] = bets
        context['past'] = True
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
                    Game.objects.filter(id=game_id).update(home_goals=form.cleaned_data['home_goals'],
                                                           away_goals=form.cleaned_data['away_goals'])
                    return HttpResponseRedirect('/management/games/')
            else:
                form = Game_update_form(instance=game)
        context['form'] = form
    return render(request, 'details.html', context)


@login_required
def tables(request):
    context = {}
    if request.method == "POST":
        form = Tournament_form(request.POST)
        if form.is_valid():
            tour = Tournament.objects.filter(name=form.cleaned_data['name']).get()
            scores = Score.objects.filter(tournament=tour).order_by('-score')
            context['scores'] = scores
            form = Tournament_form()
    else:
        form = Tournament_form()
    context['form'] = form
    return render(request, 'table.html', context)


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
            return HttpResponseRedirect('management/games.html')
    else:
        form = Game_form()
    context['form'] = form
    return render(request, 'management/games.html', context)


@login_required
@user_passes_test(is_manager)
def evaluate(request, game_id):
    game = Game.objects.get(id=game_id)
    if game.get_result is "Not registered" or game.evaluated:
        return HttpResponseRedirect('/management/games/')
    bets = Bet.objects.filter(game=game)
    context = {'game': game, 'bets': bets}
    if request.method == 'POST':
        game.evaluate()
        messages.info(request, "Bets for this game have been evaluated.")
        return HttpResponseRedirect('/management/games/')
    else:
        return render(request, 'evaluate.html', context)


@login_required
@user_passes_test(is_manager)
def manage_sq(request):
    sqs = StringQuestion.objects.order_by('due')
    context = {'sqs': sqs}
    if request.method == 'POST':
        form = SQForm(request.POST)
        if form.is_valid():
            sq = StringQuestion.objects.create(name=form.cleaned_data['name'],
                                               description=form.cleaned_data['description'],
                                               due=form.cleaned_data['due'],
                                               award=form.cleaned_data['award'],
                                               changed=form.cleaned_data['changed'],
                                               penalty=form.cleaned_data['penalty'],
                                               tournament=form.cleaned_data['tournament'])
            sq.save()
            return HttpResponseRedirect('/management/sq')
    else:
        form = SQForm()
    context['form'] = form
    return render(request, 'management/string.html', context)


@login_required
def sq(request, sq_id):
    now = timezone.now()
    sq = StringQuestion.objects.get(id=sq_id)
    context = {'sq': sq}
    if player_group(request.user) and sq.due > now:
        if StringAnswer.objects.filter(user=request.user, question=sq).exists():
            if request.method == 'POST':
                form = SAForm(request.POST)
                if form.is_valid():
                    StringAnswer.objects.filter(user=request.user,
                                                question=sq).update(answer=form.cleaned_data['answer'])
                    return HttpResponseRedirect('/guesses/')
            else:
                sa = StringAnswer.objects.filter(user=request.user, question=sq).get()
                form = SAForm(instance=sa)
        else:
            if request.method == 'POST':
                form = SAForm(request.POST)
                if form.is_valid():
                    sa = StringAnswer.objects.create_answer(request.user, sq, form.cleaned_data['answer'])
                    sa.save()
                    return HttpResponseRedirect('/guesses/')
            else:
                form = SAForm()
        context['form'] = form
    elif sq.due < now:
        sas = StringAnswer.objects.filter(question=sq)
        context['sas'] = sas
        context['past'] = True
    if is_manager(request.user):
        if sq.due >= now:
            if request.method == 'POST':
                form = SQForm(request.POST)
                if form.is_valid():
                    StringQuestion.objects.filter(id=sq_id).update(name=form.cleaned_data['name'],
                                                                   description=form.cleaned_data['description'],
                                                                   due=form.cleaned_data['due'],
                                                                   award=form.cleaned_data['award'],
                                                                   changed=form.cleaned_data['changed'],
                                                                   penalty=form.cleaned_data['penalty'],
                                                                   tournament=form.cleaned_data['tournament'])
                    return HttpResponseRedirect('/management/sq/')
            else:
                form = SQForm(instance=sq)
        else:
            if request.method == 'POST':
                form = SQ_update_form(request.POST)
                if form.is_valid():
                    StringQuestion.objects.filter(id=sq_id).update(correct_answer=form.cleaned_data['correct_answer'])
                    return HttpResponseRedirect('/management/sq/')
            else:
                form = SQ_update_form(instance=sq)
        context['form'] = form
    return render(request, 'management/string.html', context)
