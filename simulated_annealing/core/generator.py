from __future__ import annotations

import copy
import os
import random
import json
from typing import Optional, Union

import numpy as np
from mido import MidiFile, MidiTrack, Message

from simulated_annealing.core.heuristics import Heuristic
from simulated_annealing.core.utils import pair_round, random_pairs

import os
from Evalutionary_music_generation import settings


class BaseMelodyGenerator:
    """
    Base class for generating and evolving melodies using heuristic evaluation
    """

    def __init__(self, n_melodies=6, n_melody_notes=8, n_crossover_split=4, heuristic: Optional[Union[str, Heuristic]] = None):
        """
        Initializes the melody generator with a given number of melodies and notes.

        :param n_melodies: Number of melodies to generate. Default is 6.
        :param n_melody_notes: Number of notes per melody. Default is 8.
        :param heuristic: A heuristic function for evaluating melodies. Can be a string, 
                          a Heuristic object, or None for manual selection.
        """
        self.n_melodies = n_melodies
        self.n_melody_notes = n_melody_notes
        self.n_crossover_split = n_crossover_split
        
        self.heuristic = None
        if isinstance(heuristic, str):
            self.heuristic = Heuristic(heuristic)
        elif isinstance(heuristic, Heuristic):
            self.heuristic = heuristic
        else:
            print("Manual melody selection")

        self.melodies = self.generate_random_melodies()

    def generate_random_melodies(self) -> dict:
        """
        Generates a set of random melodies with notes and durations.

        :return: A dictionary where keys are melody indices and values contain 'notes' and 'durations'.
        """
        melodies = {}
        for i in range(self.n_melodies):
            notes = [random.randint(48, 83) for _ in range(self.n_melody_notes)]
            durations = random.choices([220, 260, 300, 360], k=self.n_melody_notes)
            melodies[i] = {"notes": notes, "durations": durations}
        return melodies
    
    def save_melodies(self) -> None:
        """Saves the generated melodies to MIDI files and a JSON file."""
        algorithm_dir = 'simulated_annealing' if self.heuristic else 'manual'
        for i, melody in self.melodies.items():
            mid = MidiFile()
            track = MidiTrack()
            mid.tracks.append(track)

            notes, durations = melody["notes"], melody["durations"]
            for note, duration in zip(notes, durations):
                track.append(Message("note_on", note=note, velocity=64, time=0))
                track.append(Message("note_off", note=note, velocity=64, time=duration))
                mid.save(os.path.join(settings.MEDIA_ROOT, algorithm_dir, f"melody_{i}.mid"))

        save_path = os.path.join(settings.MEDIA_ROOT, algorithm_dir, "melodies.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.melodies, f, indent=4)

    def load_melodies(self, load_path: str = "melodies.json") -> dict:
        """
        Loads melodies from a JSON file.

        :param load_path: The file path of the JSON file containing stored melodies.
        :return: A dictionary with loaded melodies where keys are integers and values contain 'notes' and 'durations'.
        """
        with open(load_path, encoding="utf-8") as f:
            melodies = json.load(f)

        keys = list(melodies.keys())
        for key in keys:
            melodies[int(key)] = melodies[key]

        for key in keys:
            del melodies[key]

        return melodies

    def mutation(self, melodies: dict, chance: float = 0.05) -> dict:
        """
        Introduces random mutations to the melodies by modifying notes and durations.

        :param melodies: The dictionary of melodies to mutate.
        :param chance: The probability of a mutation occurring for each note or duration.
        :return: The mutated melodies.
        """
        for melody in melodies.values():
            for j in range(len(melody['notes'])):
                if random.random() < chance:
                    p_dist = [0.45, 0.2, 0.1, 0.05, 0.05, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01]
                    sign = random.choice([-1, 1])
                    change_note_number = np.random.choice(list(range(1, 12 + 1)), p=p_dist)
                    melody['notes'][j] = int(melody['notes'][j] + sign*change_note_number)
                    melody['notes'][j] = min(max(melody['notes'][j], 48), 83)
                if random.random() < chance:
                    scalar = random.choice([2, 0.5])
                    melody['durations'][j] = int(melody['durations'][j]*scalar)
                    melody['durations'][j] = min(max(melody['durations'][j], 240), 1920)
        return melodies

    def run(self, generations: int = 1000) -> BaseMelodyGenerator:
        """
        Runs the evolutionary algorithm for a given number of generations.

        :param generations: Number of iterations to evolve melodies.
        :return: The evolved melody generator instance.
        :raises NotImplementedError: This method must be implemented in a subclass.
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def evaluate(self, melody_idx: int, generation: Optional[dict] = None) -> float:
        """
        Evaluates a melody using the heuristic function.

        :param melody_idx: The index of the melody to evaluate.
        :param generation: An optional alternative set of melodies for evaluation.
        :return: The heuristic evaluation score of the melody.
        """
        if generation is None:
            return self.heuristic.evaluate(self.melodies[melody_idx]["notes"])
        else:
            return self.heuristic.evaluate(generation[melody_idx]["notes"])

    @property
    def best_melody(self):
        """
        Finds the index of the best melody based on heuristic evaluation.

        :return: The index of the best melody.
        """
        return max(self.melodies.keys(), key=self.evaluate)

class MelodyGenerator(BaseMelodyGenerator):
    """
    Melody generator that evolves melodies using heuristic or manual selection.

    This class extends BaseMelodyGenerator and implements selection, crossover,
    and mutation to evolve melodies over multiple generations.
    """

    def heuristic_selection(self) -> list[int]:
        """
        Selects the top 50% of melodies based on heuristic evaluation.

        :return: A list of indices representing the selected melodies.
        """
        sorted_melodies = sorted(self.melodies.keys(), key=self.evaluate, reverse=True)
        return sorted_melodies[:len(sorted_melodies) // 2]

    def manual_selection(self) -> list[int]:
        """
        Performs manual selection of melodies through pairwise comparisons.

        :return: A list of indices representing the winning melodies.
        """
        winners = []
        pairs = random_pairs(self.n_melodies)
        for i, pair in enumerate(pairs):
            winners.append(pair_round(i, pair))
        return winners

    def crossover(self, winners) -> list[int]:
        """
        Generates a new generation of melodies by combining random parts of selected winners.
        Melodies are split into self.n_crossover_split equal parts.

        :param winners: A list of melody indices selected for reproduction.
        """
        new_generation = {}
        segment_length = self.n_melody_notes // self.n_crossover_split

        for i in range(self.n_melodies):
            new_notes = []
            new_durations = []

            for segment in range(self.n_crossover_split):
                parent_idx = random.choice(winners)

                start = segment * segment_length
                end = start + segment_length

                new_notes.extend(self.melodies[parent_idx]['notes'][start:end])
                new_durations.extend(self.melodies[parent_idx]['durations'][start:end])

            new_generation[i] = {
                "notes": new_notes,
                "durations": new_durations,
            }

        self.melodies = new_generation

    def run(self, generations: int = 1000) -> MelodyGenerator:
        """
        Runs the evolutionary process for a given number of generations.

        :param generations: The number of generations to evolve melodies.
        :return: The evolved melody generator instance.
        """
        for _ in range(generations):
            winners = self.heuristic_selection() if self.heuristic is not None else self.manual_selection()
            self.crossover(winners)
            self.melodies = self.mutation(self.melodies)
            self.save_melodies()
        return self


class SimulatedAnnealingGA(BaseMelodyGenerator):
    """
    A melody generator that evolves melodies using a simulated annealing genetic algorithm.

    This class extends BaseMelodyGenerator and uses simulated annealing to control
    acceptance probability when evolving melodies over multiple generations.
    """

    def __init__(
            self,
            n_melodies=6,
            n_melody_notes=8,
            heuristic: Optional[Union[str, Heuristic]] = None,
            initial_temp=1000,
            cooling_rate=0.97
    ):
        """
        Initializes the simulated annealing genetic algorithm for melody generation.

        :param n_melodies: Number of melodies in the population.
        :param n_melody_notes: Number of notes in each melody.
        :param heuristic: The heuristic function for evaluation.
        :param initial_temp: Initial temperature for simulated annealing.
        :param cooling_rate: Cooling rate for temperature decay.
        """
        super().__init__(n_melodies=n_melodies, n_melody_notes=n_melody_notes, heuristic=heuristic)
        self.temperature = initial_temp
        self.cooling_rate = cooling_rate

    def acceptance_probability(self, old_score: float, new_score: float) -> float:
        """
        Computes the acceptance probability for the new melody based on simulated annealing.

        :param old_score: The score of the best melody in the current generation.
        :param new_score: The score of the best melody in the new generation.
        :return: Probability of accepting the new melody.
        """
        if new_score > old_score:
            return 1.0
        return np.exp((new_score - old_score) / self.temperature)

    def run(self, generations: int = 1000) -> SimulatedAnnealingGA:
        """
        Runs the simulated annealing genetic algorithm for a given number of generations.

        :param generations: The number of generations to evolve melodies.
        :return: The evolved melody generator instance.
        """
        self.save_melodies()
        for _ in range(generations):
            best_melody = max(self.melodies.keys(), key=self.evaluate)
            best_score = self.evaluate(best_melody)

            new_generation = self.mutation(copy.deepcopy(self.melodies))
            new_best = max(new_generation.keys(), key=lambda i, gen=new_generation: self.evaluate(i, gen))
            new_score = self.evaluate(new_best, new_generation)

            if random.random() < self.acceptance_probability(best_score, new_score):
                self.melodies[best_melody] = new_generation[new_best]
            
            self.temperature *= self.cooling_rate
        return self
