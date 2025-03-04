from Evalutionary_music_generation import settings
from midi2audio import FluidSynth
import os
from django.conf import settings


def convert_mid_to_mp3(file_name):
    soundfont_path = os.path.join(settings.BASE_DIR, 'soundfont', 'GeneralUser-GS.sf2')
    mid_file_path = os.path.join(settings.MEDIA_ROOT, f'{file_name}.mid')
    mp3_file_path = os.path.join(settings.MEDIA_ROOT, f'{file_name}.mp3')
    fs = FluidSynth(soundfont_path)
    fs.midi_to_audio(mid_file_path, mp3_file_path)
