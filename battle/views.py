from django.views import View
from battle.core.auto_generation import generate_random_melodies, save_melodies, random_pairs
from django.shortcuts import render, redirect
from battle.core.convertor import convert_mid_to_mp3
import os
from Evalutionary_music_generation import settings


class MidiPairView(View):
    def get(self, request):
        n_melodies = 6
        if 'melodies' not in request.session or len(request.session.get('winners', [])) == n_melodies/2:
            n_melody_notes = 8
            melodies = generate_random_melodies(n_melodies)
            save_melodies(melodies)
            pairs = random_pairs(n_melodies)
            request.session['melodies'] = list(range(n_melodies))  # Сохраняем индексы мелодий
            request.session['pairs'] = pairs
            request.session['winners'] = []
            for index in range(len(melodies)):
                convert_mid_to_mp3(f'melody_{index}')

        print('WINNERS')
        print(request.session['winners'])
        print('WINNERS')

        pairs = request.session['pairs']
        winners = request.session['winners']
        current_pair_index = len(winners)
        if current_pair_index >= len(pairs):
            del request.session['melodies']
            del request.session['pairs']
            del request.session['winners']
            return redirect('battle')
        pair = pairs[current_pair_index]

        print('PAIR')
        print(pair)
        print('PAIR')

        context = {
            'mp3_file_url_0': os.path.join(settings.MEDIA_URL, f'melody_{pair[0]}.mp3'),
            'mp3_file_url_1': os.path.join(settings.MEDIA_URL, f'melody_{pair[1]}.mp3'),
            'melody_0_index': pair[0],
            'melody_1_index': pair[1]
        }
        return render(request, 'battle/battle.html', context)

    def post(self, request):
        selected_melody = request.POST.get('selected_melody')
        if selected_melody is not None:
            request.session['winners'].append(int(selected_melody))

        return redirect('midi-pair')
