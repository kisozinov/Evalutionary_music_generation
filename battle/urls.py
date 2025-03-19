from django.urls import path
from battle.views import MidiPairView

urlpatterns = [
    path("battle/", MidiPairView.as_view(), name="midi-pair")
]

# from django.urls import path
# from battle.views import GenerateView, SelectionView
#
# urlpatterns = [
#     path("generate/", GenerateView.as_view(), name="generate"),
#     path("select/", SelectionView.as_view(), name="select"),
# ]

