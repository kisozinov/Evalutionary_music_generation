from django.views import View
from battle.core.auto_generation import generate_random_melodies, save_melodies, random_pairs, crossover, mutation
from django.shortcuts import render, redirect
from battle.core.convertor import convert_mid_to_mp3
import os
from Evalutionary_music_generation import settings
from battle.forms import Manual


# class GenerateView(View):
#     def get(self, request):
#         if 'initial' in request.session:
#             initial_form_data = request.session['initial']
#             form = Manual(initial=initial_form_data)
#             n_melodies = initial_form_data['n_melodies']
#             n_melody_notes = initial_form_data['n_melody_notes']
#         else:
#             form = Manual()
#         context = {'form': form}
#         return render(request, 'battle/battle.html', context)
#
#     def post(self, request):
#         form = Manual(request.POST)
#         if form.is_valid():
#             form_data = form.cleaned_data
#             request.session['initial'] = form_data
#
#
# class SelectionView(View):


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
            print("new_loop")
            winners = request.session['winners']
            melodies = request.session['melodies']
            melodies = {int(key): value for key, value in melodies.items()}
            melodies = crossover(melodies, winners, request.session['initial']['n_melody_notes'])
            melodies = mutation(melodies)
            save_melodies(melodies, algorithm_dir)
            pairs = random_pairs(request.session['initial']['n_melodies'])
            for index in range(len(melodies)):
                convert_mid_to_mp3(f'melody_{index}', algorithm_dir)
            request.session['pairs'] = pairs
            request.session['winners'] = []

        return redirect('midi-pair')
