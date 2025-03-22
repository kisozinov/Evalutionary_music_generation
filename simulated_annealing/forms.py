import os

from django import forms
from django.core.exceptions import ValidationError


class SimulatedAnnealing(forms.Form):
    """SimulatedAnnealing form."""

    config = forms.FileField(required=False, label="config")
    n_melodies = forms.IntegerField(min_value=2, max_value=20, step_size=2, initial=6, label="melodies num")
    n_melody_notes = forms.IntegerField(min_value=5, max_value=100, step_size=1, initial=8, label="notes num")
    n_iterations = forms.IntegerField(min_value=1, max_value=1000000, step_size=1, initial=1000, label="iterations num")

    def clean_config(self):
        file = self.cleaned_data.get("config")
        if file:
            ext = os.path.splitext(file.name)[1].lower()  # Получаем расширение файла
            if ext != ".json":
                raise ValidationError("Ошибка: загрузите файл формата .json!")
        return file

