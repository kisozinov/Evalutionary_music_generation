from django.views import View
from battle.core.auto_generation import generate_random_melodies, save_melodies, random_pairs, crossover, mutation, \
    load_melodies_data
from django.shortcuts import render, redirect
from battle.core.convertor import convert_mid_to_mp3
import os
from Evalutionary_music_generation import settings


class MidiPairView(View):
    def get(self, request):
        n_melodies = 6
        if not os.listdir(settings.MEDIA_ROOT):
            melodies = generate_random_melodies(n_melodies)
            save_melodies(melodies)
            melodies = load_melodies_data()

            pairs = random_pairs(n_melodies)
            for index in range(len(melodies)):
                convert_mid_to_mp3(f'melody_{index}')
            request.session['melodies'] = melodies
            request.session['pairs'] = pairs
            request.session['winners'] = []

        if len(request.session.get('winners', [])) == n_melodies/2:
            print("new_loop")
            winners = request.session['winners']
            melodies = request.session['melodies']
            melodies = {int(key): value for key, value in melodies.items()}

            melodies = crossover(melodies, winners)
            melodies = mutation(melodies)
            save_melodies(melodies)
            pairs = random_pairs(n_melodies)
            for index in range(len(melodies)):
                convert_mid_to_mp3(f'melody_{index}')
            request.session['pairs'] = pairs
            request.session['winners'] = []

        pairs = request.session['pairs']
        winners = request.session['winners']
        current_pair_index = len(winners)

        if current_pair_index >= len(pairs):
            del request.session['pairs']
            return redirect('battle')
        pair = pairs[current_pair_index]
        print(pair)

        context = {
            'mp3_file_url_0': os.path.join(settings.MEDIA_URL, f'melody_{pair[0]}.mp3'),
            'mp3_file_url_1': os.path.join(settings.MEDIA_URL, f'melody_{pair[1]}.mp3'),
            'melody_0_index': pair[0],
            'melody_1_index': pair[1]
        }
        return render(request, 'battle/battle.html', context)

    def post(self, request):
        selected_melody = request.POST.get('selected_melody')
        print(selected_melody)
        if selected_melody is not None:
            request.session['winners'].append(int(selected_melody))
            request.session.modified = True
        return redirect('midi-pair')
