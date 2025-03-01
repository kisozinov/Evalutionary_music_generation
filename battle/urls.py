from django.urls import path
from battle.views import MidiPairView

urlpatterns = [
    path("battle/", MidiPairView.as_view(), name="midi-pair")
]

# from django.urls import path
# from .views import play_midi
#
# urlpatterns = [
#     path('battle/', play_midi, name='play_midi'),
# ]
