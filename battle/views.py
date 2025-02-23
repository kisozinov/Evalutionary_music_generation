# import os
#
# from django.http import JsonResponse
# from django.views import View
# from django.views.generic import TemplateView
#
# from Evalutionary_music_generation import settings
# from battle.core.auto_generation import generate_random_melodies, save_melodies, random_pairs
# #
# #
# # # Create your views here.
# #
# class BattleView(TemplateView):
#     template_name = 'battle/battle.html'
#
#
# class MidiPairView(View):
#     def get(self, request):
#         n_melodies = 6
#         n_melody_notes = 8
#         melodies = generate_random_melodies(n_melodies)
#         save_melodies(melodies)
#         pairs = random_pairs(n_melodies)
#         pair = pairs[0]
#
#         return JsonResponse({
#             "midi_1": os.path.join(settings.MEDIA_URL, f"melody_{pair[0]}.mid"),
#             "midi_2": os.path.join(settings.MEDIA_URL, f"melody_{pair[1]}.mid")
#         })



import os
from django.shortcuts import render
from midi2audio import FluidSynth
from django.conf import settings

def play_midi(request):
    midi_file_path = os.path.join(settings.MEDIA_ROOT, 'melody_1.mid')
    mp3_file_path = os.path.join(settings.MEDIA_ROOT, 'melody_1.mp3')

    # Конвертация MIDI в MP3
    fs = FluidSynth()
    fs.midi_to_audio(midi_file_path, mp3_file_path)

    context = {
        'mp3_file_url': os.path.join(settings.MEDIA_URL, 'melody_1.mp3')
    }
    return render(request, 'battle.html', context)

