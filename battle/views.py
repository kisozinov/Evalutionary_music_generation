import os

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from Evalutionary_music_generation import settings
from battle.core.auto_generation import generate_random_melodies, save_melodies, random_pairs
from django.shortcuts import render
from midi2audio import FluidSynth
import os
from django.conf import settings


# class BattleView(TemplateView):
#     template_name = 'battle/battle.html'


class MidiPairView(View):
    def get(self, request):
        n_melodies = 6
        n_melody_notes = 8
        melodies = generate_random_melodies(n_melodies)
        save_melodies(melodies)
        pairs = random_pairs(n_melodies)
        pair = pairs[0]

        soundfont_path = os.path.join(settings.BASE_DIR, 'soundfont', 'GeneralUser-GS.sf2')
        midi_file_path_0 = os.path.join(settings.MEDIA_ROOT, f'melody_{pair[0]}.mid')
        mp3_file_path_0 = os.path.join(settings.MEDIA_ROOT, f'melody_{pair[0]}.mp3')

        # Проверяем, существует ли уже MP3-файл
        if not os.path.exists(mp3_file_path_0):
            # Конвертация MIDI в MP3 с использованием FluidSynth и SoundFont
            fs = FluidSynth(soundfont_path)
            fs.midi_to_audio(midi_file_path_0, mp3_file_path_0)

        midi_file_path_1 = os.path.join(settings.MEDIA_ROOT, f'melody_{pair[1]}.mid')
        mp3_file_path_1 = os.path.join(settings.MEDIA_ROOT, f'melody_{pair[1]}.mp3')

        # Проверяем, существует ли уже MP3-файл
        if not os.path.exists(mp3_file_path_1):
            # Конвертация MIDI в MP3 с использованием FluidSynth и SoundFont
            fs = FluidSynth(soundfont_path)
            fs.midi_to_audio(midi_file_path_1, mp3_file_path_1)

        print()
        print('PAIR PAIR PAIR PAIR PAIR PAIR PAIR PAIR PAIR PAIR')
        print(pair)
        print('PAIR PAIR PAIR PAIR PAIR PAIR PAIR PAIR PAIR PAIR')
        print()

        context = {
            # 'mp3_file_url_0': os.path.join(settings.MEDIA_URL, f'melody_{pair[0]}.mp3'),
            'mp3_file_url_0': os.path.join(settings.MEDIA_URL, f'fonk.mp3'),
            'mp3_file_url_1': os.path.join(settings.MEDIA_URL, f'melody_{pair[1]}.mp3')
        }
        return render(request, 'battle/battle.html', context)