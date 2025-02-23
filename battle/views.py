from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.

class BattleView(TemplateView):
    template_name = 'battle/battle.html'
