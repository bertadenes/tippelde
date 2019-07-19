from django.db import models
from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from tippelde.models import Game, Bet, Tournament, Score, StringQuestion, StringAnswer, NumericQuestion, NumericAnswer
from tippelde.forms import Bet_form, Game_form, Game_update_form, Tournament_form, Evaluate, SQForm, SAForm, \
    SQ_update_form, NQForm, NAForm
from tippelde.extras import player_group, is_manager, ev


# Create your views here.
# General views
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
    nqs = NumericQuestion.objects.order_by('due').filter(due__gte=now)
    context = {'results': results, 'upcoming': upcoming, 'sqs': sqs, 'nqs': nqs}
    return render(request, 'games.html', context)


@login_required
@user_passes_test(player_group)
def guesses(request):
    now = timezone.now()
    upcoming = Bet.objects.filter(user=request.user).filter(game__kickoff__gte=now).order_by('game__kickoff')
    results = Bet.objects.filter(user=request.user).exclude(game__kickoff__gte=now).order_by('-game__kickoff')
    sas = StringAnswer.objects.filter(user=request.user).order_by('question__due')
    nas = NumericAnswer.objects.filter(user=request.user).order_by('question__due')
    context = {'results': results, 'upcoming': upcoming, 'sas': sas, 'nas': nas}
    return render(request, 'guesses.html', context)


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


# Management views
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
def manage_sq(request):
    qs = StringQuestion.objects.order_by('due')
    context = {'qs': qs}
    if request.method == 'POST':
        form = SQForm(request.POST)
        if form.is_valid():
            q = StringQuestion.objects.create(name=form.cleaned_data['name'],
                                              description=form.cleaned_data['description'],
                                              due=form.cleaned_data['due'],
                                              award=form.cleaned_data['award'],
                                              changes=form.cleaned_data['changes'],
                                              penalty=form.cleaned_data['penalty'],
                                              tournament=form.cleaned_data['tournament'])
            q.save()
            return HttpResponseRedirect('/management/sq')
    else:
        form = SQForm()
    context['form'] = form
    context['type'] = "string"
    return render(request, 'management/questions.html', context)


@login_required
@user_passes_test(is_manager)
def manage_nq(request):
    qs = NumericQuestion.objects.order_by('due')
    context = {'qs': qs}
    if request.method == 'POST':
        form = NQForm(request.POST)
        if form.is_valid():
            q = NumericQuestion.objects.create(name=form.cleaned_data['name'],
                                               description=form.cleaned_data['description'],
                                               due=form.cleaned_data['due'],
                                               award=form.cleaned_data['award'],
                                               changes=form.cleaned_data['changes'],
                                               penalty=form.cleaned_data['penalty'],
                                               tournament=form.cleaned_data['tournament'])
            q.save()
            return HttpResponseRedirect('/management/nq')
    else:
        form = NQForm()
    context['form'] = form
    context['type'] = "numeric"
    return render(request, 'management/questions.html', context)


# Detail views
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
def sq(request, q_id):
    now = timezone.now()
    q = StringQuestion.objects.get(id=q_id)
    context = {'q': q}
    if player_group(request.user) and q.due > now:
        if StringAnswer.objects.filter(user=request.user, question=q).exists():
            a = StringAnswer.objects.filter(user=request.user, question=q).get()
            if request.method == 'POST':
                form = SAForm(request.POST)
                context['form'] = form
                if form.is_valid():
                    if a.answer != form.cleaned_data['answer']:
                        StringAnswer.objects.filter(user=request.user,
                                                    question=q).update(answer=form.cleaned_data['answer'],
                                                                       changed=models.F('changed')+1)
                    return HttpResponseRedirect('/guesses/')
            else:
                context['changed'] = a.changed
                if a.changed < q.changes:
                    form = SAForm(instance=a)
                    context['form'] = form
        else:
            if request.method == 'POST':
                form = SAForm(request.POST)
                if form.is_valid():
                    a = StringAnswer.objects.create_answer(request.user, q, form.cleaned_data['answer'])
                    a.save()
                    return HttpResponseRedirect('/guesses/')
            else:
                context['changed'] = -1
                form = SAForm()
            context['form'] = form
    elif q.due < now:
        ans = StringAnswer.objects.filter(question=q)
        context['ans'] = ans
        context['past'] = True
    if is_manager(request.user):
        if q.due >= now:
            if request.method == 'POST':
                form = SQForm(request.POST)
                if form.is_valid():
                    StringQuestion.objects.filter(id=q_id).update(name=form.cleaned_data['name'],
                                                                  description=form.cleaned_data['description'],
                                                                  due=form.cleaned_data['due'],
                                                                  award=form.cleaned_data['award'],
                                                                  changed=form.cleaned_data['changes'],
                                                                  penalty=form.cleaned_data['penalty'],
                                                                  tournament=form.cleaned_data['tournament'])
                    return HttpResponseRedirect('/management/sq/')
            else:
                form = SQForm(instance=q)
        else:
            if request.method == 'POST':
                form = SQ_update_form(request.POST)
                if form.is_valid():
                    StringQuestion.objects.filter(id=q_id).update(correct_answer=form.cleaned_data['correct_answer'])
                    return HttpResponseRedirect('/management/sq/')
            else:
                form = SQ_update_form(instance=q)
        context['form'] = form
    context['type'] = "string"
    return render(request, 'question.html', context)


@login_required
def nq(request, q_id):
    now = timezone.now()
    q = NumericQuestion.objects.get(id=q_id)
    context = {'q': q}
    if player_group(request.user) and q.due > now:
        if NumericAnswer.objects.filter(user=request.user, question=q).exists():
            a = NumericAnswer.objects.filter(user=request.user, question=q).get()
            if request.method == 'POST':
                form = NAForm(request.POST)
                context['form'] = form
                if form.is_valid():
                    if a.answer != form.cleaned_data['answer']:
                        NumericAnswer.objects.filter(user=request.user,
                                                     question=q).update(answer=form.cleaned_data['answer'],
                                                                        changed=models.F('changed') + 1)
                    return HttpResponseRedirect('/guesses/')
            else:
                context['changed'] = a.changed
                if a.changed < q.changes:
                    form = NAForm(instance=a)
                    context['form'] = form
        else:
            if request.method == 'POST':
                form = NAForm(request.POST)
                if form.is_valid():
                    a = NumericAnswer.objects.create_answer(request.user, q, form.cleaned_data['answer'])
                    a.save()
                    return HttpResponseRedirect('/guesses/')
            else:
                context['changed'] = -1
                form = NAForm()
            context['form'] = form
    elif q.due < now:
        ans = NumericAnswer.objects.filter(question=q)
        context['ans'] = ans
        context['past'] = True
    if is_manager(request.user):
        if q.due >= now:
            if request.method == 'POST':
                form = SQForm(request.POST)
                if form.is_valid():
                    NumericQuestion.objects.filter(id=q_id).update(name=form.cleaned_data['name'],
                                                                   description=form.cleaned_data['description'],
                                                                   due=form.cleaned_data['due'],
                                                                   award=form.cleaned_data['award'],
                                                                   changed=form.cleaned_data['changes'],
                                                                   penalty=form.cleaned_data['penalty'],
                                                                   tournament=form.cleaned_data['tournament'])
                    return HttpResponseRedirect('/management/nq/')
            else:
                form = SQForm(instance=q)
        else:
            if request.method == 'POST':
                form = SQ_update_form(request.POST)
                if form.is_valid():
                    NumericQuestion.objects.filter(id=q_id).update(correct_answer=form.cleaned_data['correct_answer'])
                    return HttpResponseRedirect('/management/nq/')
            else:
                form = SQ_update_form(instance=q)
        context['form'] = form
    context['type'] = "numeric"
    return render(request, 'question.html', context)


# Deletion views
class Game_delete(DeleteView):
    model = Game
    success_url = reverse_lazy('manage_games')


class Bet_delete(DeleteView):
    model = Bet
    success_url = reverse_lazy('guesses')


class SQDel(DeleteView):
    model = StringQuestion
    success_url = reverse_lazy('manage_sq')
#
#
# removed to avoid multiple changes
# @login_required
# @user_passes_test(is_manager)
# class SADel(DeleteView):
#     model = StringAnswer
#     success_url = reverse_lazy('guesses')


class NQDel(DeleteView):
    model = NumericQuestion
    success_url = reverse_lazy('manage_nq')


# Evaluation views
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
def evaluate_sq(request, q_id):
    q = StringQuestion.objects.get(id=q_id)
    if q.correct_answer is None or q.evaluated:
        return HttpResponseRedirect('/management/sq/')
    answers = StringAnswer.objects.filter(question=q)
    context = {'q': q, 'answers': answers}
    if request.method == 'POST':
        q.evaluate()
        messages.info(request, "Answers for this question have been evaluated.")
        return HttpResponseRedirect('/management/sq/')
    else:
        return render(request, 'evaluate_question.html', context)


@login_required
@user_passes_test(is_manager)
def evaluate_nq(request, q_id):
    q = NumericQuestion.objects.get(id=q_id)
    if q.correct_answer is None or q.evaluated:
        return HttpResponseRedirect('/management/nq/')
    answers = NumericAnswer.objects.filter(question=q)
    context = {'q': q, 'answers': answers}
    if request.method == 'POST':
        q.evaluate()
        messages.info(request, "Answers for this question have been evaluated.")
        return HttpResponseRedirect('/management/nq/')
    else:
        return render(request, 'evaluate_question.html', context)
