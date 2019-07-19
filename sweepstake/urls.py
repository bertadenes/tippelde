"""sweepstake URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from tippelde import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^games/', views.games, name='games'),
    url(r'^tables/', views.tables, name='tables'),
    url(r'^management/home/', views.manage, name='management'),
    url(r'^management/games/', views.manage_games, name='manage_games'),
    url(r'^management/sq/', views.manage_sq, name='manage_sq'),
    url(r'^guesses/', views.guesses, name='guesses'),
    url(r'^guess_delete/(?P<pk>\d+)/$', views.Bet_delete.as_view(template_name='confirm_delete.html'),
        name='delete_guess'),
    url(r'^sq_delete/(?P<pk>\d+)/$', views.SQDel.as_view(template_name='confirm_delete.html'), name='delete_sq'),
    # url(r'^sa_delete/(?P<pk>\d+)/$', views.SADel.as_view(template_name='confirm_delete.html'), name='delete_sa'),
    url(r'^sq/(?P<sq_id>[0-9]+)/$', views.sq, name='sq'),
    url(r'^details/(?P<game_id>[0-9]+)/$', views.details, name='details'),
    url(r'^evaluate/(?P<game_id>[0-9]+)/$', views.evaluate, name='evaluate'),
    url(r'^evaluate_sq/(?P<sq_id>[0-9]+)/$', views.evaluate_sq, name='evaluate_sq'),
    url(r'^game_delete/(?P<pk>\d+)/$', views.Game_delete.as_view(template_name='confirm_delete.html'),
        name='delete_game'),
]
"""
accounts routing:
accounts/ login/ [name='login']
accounts/ logout/ [name='logout']
accounts/ password_change/ [name='password_change']
accounts/ password_change/done/ [name='password_change_done']
accounts/ password_reset/ [name='password_reset']
accounts/ password_reset/done/ [name='password_reset_done']
accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
accounts/ reset/done/ [name='password_reset_complete']
"""