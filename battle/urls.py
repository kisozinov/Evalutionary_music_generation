from django.urls import path
from battle.views import MidiPairView, ManualResultView

urlpatterns = [
    path("battle/", MidiPairView.as_view(), name="midi-pair"),
    path("manual_result/", ManualResultView.as_view(), name="manual_result"),
]
