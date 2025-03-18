from django.urls import path
from battle.views import MidiPairView

urlpatterns = [
    path("battle/", MidiPairView.as_view(), name="midi-pair")
]
