from django.urls import path
from simulated_annealing.views import SimulatedAnnealingView

urlpatterns = [
    path("simulated_annealing/", SimulatedAnnealingView.as_view(), name="simulated_annealing")
]
