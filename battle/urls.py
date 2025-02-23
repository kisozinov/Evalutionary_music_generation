# from django.urls import path
# from battle.views import BattleView, MidiPairView
#
# urlpatterns = [
#     path('battle/', BattleView.as_view(), name='battle'),
#     path("midi-pair/", MidiPairView.as_view(), name="midi-pair")
# ]

from django.urls import path
from .views import play_midi

urlpatterns = [
    path('battle/', play_midi, name='play_midi'),
]
