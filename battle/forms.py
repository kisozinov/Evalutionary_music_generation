from django import forms


class Manual(forms.Form):
    """Manual form."""

    n_melodies = forms.IntegerField(min_value=2, max_value=20, step_size=2, initial=6, label="number of melodies")
    n_melody_notes = forms.IntegerField(min_value=5, max_value=100, step_size=1, initial=8, label="number of notes")
