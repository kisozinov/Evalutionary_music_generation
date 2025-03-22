import shutil

from django.views import View
from django.views.generic import TemplateView

from battle.core.utils import generate_random_melodies, save_melodies, random_pairs, crossover, mutation
from django.shortcuts import render, redirect
from battle.core.convertor import convert_mid_to_mp3
import os
from Evalutionary_music_generation import settings
from battle.forms import Manual


class MidiPairView(View):
    def get(self, request):
        algorithm_dir = 'manual'
        if 'initial' in request.session:
            initial_form_data = request.session['initial']
            form = Manual(initial=initial_form_data)
        else:
            form = Manual()
        context = {'form': form}

        pairs = request.session.get('pairs', [])
        winners = request.session.get('winners', [])
        if pairs:
            current_pair_index = len(winners)
            pair = pairs[current_pair_index]
            context.update(
                {
                    'mp3_file_url_0': os.path.join(settings.MEDIA_URL, algorithm_dir, f'melody_{pair[0]}.mp3'),
                    'mp3_file_url_1': os.path.join(settings.MEDIA_URL, algorithm_dir, f'melody_{pair[1]}.mp3'),
                    'melody_0_index': pair[0],
                    'melody_1_index': pair[1]
                }
            )

        return render(request, 'battle/battle.html', context)

    def post(self, request):
        algorithm_dir = "manual"
        form = Manual(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            request.session['initial'] = form_data
            n_melodies = form_data['n_melodies']
            n_melody_notes = form_data['n_melody_notes']

            melodies = generate_random_melodies(n_melodies, n_melody_notes)
            save_melodies(melodies, algorithm_dir)

            pairs = random_pairs(n_melodies)
            for index in range(len(melodies)):
                convert_mid_to_mp3(f'melody_{index}', algorithm_dir)
            request.session['melodies'] = melodies
            request.session['pairs'] = pairs
            request.session['winners'] = []

        selected_melody = request.POST.get('selected_melody')
        if selected_melody:
            request.session['winners'].append(int(selected_melody))
            request.session.modified = True

        if len(request.session.get('winners', [])) == request.session['initial']['n_melodies'] / 2:
            winners = request.session['winners']
            melodies = request.session['melodies']
            melodies = {int(key): value for key, value in melodies.items()}

            source_folder = os.path.join(settings.MEDIA_ROOT, algorithm_dir)
            destination_folder = os.path.join(settings.MEDIA_ROOT, "previous")
            if os.path.exists(destination_folder):
                shutil.rmtree(destination_folder)
            os.makedirs(destination_folder)
            winners_file_names = [f"melody_{num}.mp3" for num in winners]
            for file in winners_file_names:
                shutil.move(os.path.join(source_folder, file), os.path.join(destination_folder, file))
            if os.path.exists(source_folder):
                shutil.rmtree(source_folder)
            os.makedirs(source_folder)

            melodies = crossover(melodies, winners, request.session['initial']['n_melody_notes'])
            melodies = mutation(melodies)
            save_melodies(melodies, algorithm_dir)
            pairs = random_pairs(request.session['initial']['n_melodies'])
            for index in range(len(melodies)):
                convert_mid_to_mp3(f'melody_{index}', algorithm_dir)
            request.session['pairs'] = pairs
            request.session['winners'] = []

        return redirect('midi-pair')


class ManualResultView(TemplateView):
    template_name = 'battle/manual_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_winners = []
        folder = os.path.join(settings.MEDIA_ROOT, "previous")
        for file in os.listdir(folder):
            previous_winners.append(os.path.join(settings.MEDIA_URL, "previous", file))
        context['previous_winners'] = previous_winners
        return context
