import os

from django.views import View
from django.shortcuts import render, redirect

from battle.core.convertor import convert_mid_to_mp3
from simulated_annealing.core.generator import SimulatedAnnealingGA
from simulated_annealing.core.heuristics import Heuristic
from simulated_annealing.forms import SimulatedAnnealing
from Evalutionary_music_generation import settings


class SimulatedAnnealingView(View):
    algorithm_dir = 'simulated_annealing'

    def get(self, request):
        if 'initial' in request.session:
            form = SimulatedAnnealing(initial=request.session['initial'])
        else:
            form = SimulatedAnnealing()
        context = {'form': form}

        if 'best_melody' in request.session:
            file_name = f'melody_{request.session['best_melody']}'

            convert_mid_to_mp3(file_name, self.algorithm_dir)
            context.update(
                {'best_melody': os.path.join(settings.MEDIA_URL, self.algorithm_dir, f'{file_name}.mp3')}
            )
        return render(request, 'simulated_annealing/simulated_annealing.html', context)

    def post(self, request):
        form = SimulatedAnnealing(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            n_melodies = form_data["n_melodies"]
            n_melody_notes = form_data["n_melody_notes"]
            initial_temp = form_data["n_iterations"]
            uploaded_file = form_data["config"]

            form_data.pop("config", None)
            request.session['initial'] = form_data

            if uploaded_file:
                file_path = os.path.join(settings.MEDIA_ROOT, 'simulated_annealing', uploaded_file.name)
                with open(file_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
                heuristic = Heuristic(config_path=file_path)
            else:
                heuristic = Heuristic()

            obj = SimulatedAnnealingGA(
                heuristic=heuristic,
                n_melodies=n_melodies,
                n_melody_notes=n_melody_notes,
                initial_temp=initial_temp
            )
            new_obj = obj.run()
            best_melody = new_obj.best_melody
            request.session['best_melody'] = best_melody
            request.session.modified = True
            return redirect("simulated_annealing")

        return render(request, 'simulated_annealing/simulated_annealing.html', {'form': form})
