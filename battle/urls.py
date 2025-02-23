from django.urls import path
from battle.views import BattleView

urlpatterns = [
    path('battle/', BattleView.as_view(), name='battle'),
]
