import random
import pygame


code2name = {
    48: "C3",
    49: "C#3",
    50: "D3",
    51: "D#3",
    52: "E3",
    53: "F3",
    54: "F#3",
    55: "G3",
    56: "G#3",
    57: "A3",
    58: "A#3",
    59: "B3",
    60: "C4",
    61: "C#4",
    62: "D4",
    63: "D#4",
    64: "E4",
    65: "F4",
    66: "F#4",
    67: "G4",
    68: "G#4",
    69: "A4",
    70: "A#4",
    71: "B4",
    72: "C5",
    73: "C#5",
    74: "D5",
    75: "D#5",
    76: "E5",
    77: "F5",
    78: "F#5",
    79: "G5",
    80: "G#5",
    81: "A5",
    82: "A#5",
    83: "B5",
}

def play_melody(index):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(f'melody_{index}.mid')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def random_pairs(n):
    """ Generates random pairs of melodies for tournament selection. """
    numbers = list(range(n))
    random.shuffle(numbers)

    pairs = list(zip(numbers[::2], numbers[1::2]))

    return pairs


def pair_round(idx, pair):
    """ Handles human-based melody selection. """
    print(f"Pair #{idx + 1}")
    print("Choose the action: \n1.Play the first melody\n2.Play the second melody\n3.Choose the winner")
    action = -1
    while action != 3:
        action = int(input("Action: "))
        if action <= 0 or action > 3:
            print("Choose action between 1 and 3")
        elif action == 1:
            play_melody(pair[0])
        elif action == 2:
            play_melody(pair[1])
            
    winner = int(input("Choose winner(1 or 2): "))
    return pair[winner - 1]
