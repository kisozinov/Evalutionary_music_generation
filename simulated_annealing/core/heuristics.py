import inspect
import os
from typing import Optional
import numpy as np
import json

from Evalutionary_music_generation import settings


class HeuristicConfig:
    """ Manages heuristic weights and additional parameters, allowing dynamic loading from a JSON file. """

    DEFAULT_CONFIG = {
        "monotony": { "weight": 0.1 },
        "ascending_scale": { "weight": 0.1 },
        "descending_scale": { "weight": 0.1 },
        "arpeggio": { "weight": 0.15 },
        "repetition": { "weight": 0.1 },
        "interval_variety": { "weight": 0.1 },
        "smoothness": { "weight": 0.1 },
        "symmetry": { "weight": 0.1 },
        "tonic_stability": { "weight": 0.1 },
        "tonal_purity": {
            "weight": 0.05,
            "scale": [48, 50, 52, 53, 55, 57, 59, 60]  # Default: C major scale
        }
    }

    default_config_path = os.path.join(settings.MEDIA_ROOT, 'simulated_annealing', 'default_config.json')

    def __init__(self, config_path=default_config_path):
        """
        Initializes the heuristic configuration, loading from a JSON file if available.
        
        :param config_path: Path to the JSON file containing heuristic settings.
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """ Loads heuristic configuration from a JSON file or falls back to default settings. """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Ensure all heuristic keys exist in the loaded config
                for heuristic, default_values in self.DEFAULT_CONFIG.items():
                    if heuristic not in data:
                        continue
                    else:
                        # Ensure all default keys exist within each heuristic config
                        for key, value in default_values.items():
                            if key not in data[heuristic]:
                                data[heuristic][key] = value

                return data

        except FileNotFoundError:
            print(f"Warning: Configuration file '{self.config_path}' not found. Using default configuration.")
        except json.JSONDecodeError:
            print(f"Error: Failed to read configuration file '{self.config_path}'. Using default configuration.")

        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """ Saves the current heuristic configuration to a JSON file. """
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get_weight(self, heuristic_name):
        """ Retrieves the weight of a specified heuristic. """
        return self.config.get(heuristic_name, {}).get("weight", 0.0)

    def update_weight(self, heuristic_name: str, value: float):
        """
        Updates a heuristic weight and saves the configuration.

        :param heuristic_name: Name of the heuristic to update.
        :param value: New weight value (must be a float between 0 and 1).
        """
        if heuristic_name in self.config and 0 <= value <= 1:
            self.config[heuristic_name]["weight"] = value
            self.save_config()
        else:
            raise ValueError(f"Invalid heuristic name or weight: {heuristic_name} -> {value}")

    def get_parameters(self, heuristic_name):
        """ Retrieves additional parameters for a heuristic (excluding weight). """
        heuristic_data = self.config.get(heuristic_name, {})
        return {k: v for k, v in heuristic_data.items() if k != "weight"}

    def update_parameters(self, heuristic_name: str, params: dict):
        """
        Updates parameters for a specific heuristic and saves the configuration.

        :param heuristic_name: Name of the heuristic.
        :param params: Dictionary of parameters to update.
        """
        if heuristic_name not in self.config:
            self.config[heuristic_name] = {}

        self.config[heuristic_name].update(params)
        self.save_config()


class Heuristic:
    """ Evaluates melodies using weighted heuristic scores with optional metric filtering. """

    def __init__(self, config_path="heuristics_config.json"):
        """ Initializes the heuristic evaluator, loads configuration, and dynamically registers heuristics. """
        self.config = HeuristicConfig(config_path)
        self.AVAILABLE_METRICS = self._initialize_metrics()

    # def __init__(self, config_path):
    #     """ Initializes the heuristic evaluator, loads configuration, and dynamically registers heuristics. """
    #     if not config_path:
    #         config_path = os.path.join(settings.MEDIA_ROOT, f'dgjj.mid')
    #     self.config = HeuristicConfig(config_path)
    #     self.AVAILABLE_METRICS = self._initialize_metrics()

    def _initialize_metrics(self):
        """ Dynamically finds all heuristic methods ending with '_score' and registers them. """
        return {
            name[:-6]: method  # Remove '_score' suffix
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.endswith("_score")
        }

    def validate_metrics(self, metrics):
        """ Ensures all requested metrics exist in the system. """
        invalid_metrics = [m for m in metrics if m not in self.AVAILABLE_METRICS]
        if invalid_metrics:
            raise ValueError(f"Invalid metric names: {invalid_metrics}")

    def normalize_weights(self, selected_metrics: list[str]):
        """
        Adjusts heuristic weights so that their absolute values sum to 1.
        This ensures proper weighting even when some weights are negative.
        
        :param selected_metrics: List of metric names to be used in evaluation.
        :return: Normalized weight dictionary.
        """
        selected_weights = {m: self.config.get_weight(m) for m in selected_metrics}
        total_abs_weight = sum(abs(w) for w in selected_weights.values())

        if total_abs_weight == 0:
            raise ValueError("Total absolute weight of selected metrics is zero. Adjust weights in config.")

        return {m: w / total_abs_weight for m, w in selected_weights.items()}

    def evaluate(self, melody: list[int], metrics: Optional[list[str]] = None):
        """
        Evaluates a single melody based on the given or all available heuristics.
        
        :param melody: List of note values (e.g., [60, 62, 64, 65, ...]).
        :param metrics: Optional list of heuristic names to evaluate on.
        :return: Normalized heuristic score.
        """
        if metrics is None:
            metrics = list(self.AVAILABLE_METRICS.keys() & self.config.config.keys())  # Используем все метрики
        else:
            self.validate_metrics(metrics)  # Проверяем, что метрики существуют

        # Получаем нормализованные веса для выбранных метрик
        normalized_weights = self.normalize_weights(metrics)

        # Вычисляем общий score
        total_score = 0
        for metric in metrics:
            heuristic_func = self.AVAILABLE_METRICS[metric]
            config_params = self.config.get_parameters(metric)
            signature = inspect.signature(heuristic_func)
            signature_params = {name: param.default for name, param in signature.parameters.items()}
            kwargs = {key: config_params[key] for key in signature_params if key in config_params}
            total_score += heuristic_func(melody, **kwargs) * normalized_weights[metric]

        return total_score
    
    # === Heuristic Functions (auto-registered via inspect) === #

    def monotony_score(self, melody):
        """ Scores how monotonous the melody is. 1 if all notes are the same, 0 if all are unique. """
        unique_notes = len(set(melody))
        min_val, max_val = 1, len(melody)
        return 1 - (unique_notes - min_val) / (max_val - min_val)

    def ascending_scale_score(self, melody):
        """ Scores how closely the melody follows an ascending scale pattern. """
        diffs = np.diff(melody)
        ascending_steps = sum(1 for d in diffs if d > 0)
        min_val, max_val = 0, len(diffs)
        return (ascending_steps - min_val) / (max_val - min_val) if max_val > min_val else 0

    def descending_scale_score(self, melody):
        """ Scores how closely the melody follows a descending scale pattern. """
        diffs = np.diff(melody)
        descending_steps = sum(1 for d in diffs if d < 0)
        min_val, max_val = 0, len(diffs)
        return (descending_steps - min_val) / (max_val - min_val) if max_val > min_val else 0

    def arpeggio_score(self, melody):
        """ Scores how closely the melody follows an arpeggio pattern (broken chord). """
        chord_intervals = {3, 4, 7, 8}
        diffs = np.abs(np.diff(melody))
        arpeggio_steps = sum(1 for d in diffs if d in chord_intervals)
        min_val, max_val = 0, len(diffs)
        return (arpeggio_steps - min_val) / (max_val - min_val) if max_val > min_val else 0

    def repetition_score(self, melody):
        """ Scores how many repeated patterns exist in the melody. """
        pattern_size = 2
        repeated_patterns = sum(
            1 for i in range(len(melody) - pattern_size)
            if melody[i:i+pattern_size] == melody[i+pattern_size:i+2*pattern_size]
        )
        min_val, max_val = 0, len(melody) // pattern_size
        return (repeated_patterns - min_val) / (max_val - min_val) if max_val > min_val else 0

    def interval_variety_score(self, melody):
        """ Scores how diverse the intervals between notes are. """
        diffs = np.abs(np.diff(melody))
        unique_intervals = len(set(diffs))
        min_val, max_val = 1, len(diffs)
        return (unique_intervals - min_val) / (max_val - min_val) if max_val > min_val else 0

    def smoothness_score(self, melody):
        """ Scores how smoothly the melody moves, preferring stepwise motion. """
        diffs = np.abs(np.diff(melody))
        smooth_steps = sum(1 for d in diffs if d <= 2)
        min_val, max_val = 0, len(diffs)
        return (smooth_steps - min_val) / (max_val - min_val) if max_val > min_val else 0

    def symmetry_score(self, melody):
        """ Scores how symmetrical the melody is. """
        first_half = melody[:len(melody)//2]
        second_half = melody[len(melody)//2:]
        sym_match = sum(1 for i in range(len(first_half)) if first_half[i] == second_half[i])
        min_val, max_val = 0, len(first_half)
        return (sym_match - min_val) / (max_val - min_val) if max_val > min_val else 0

    def tonic_stability_score(self, melody):
        """ Scores how often the melody returns to the tonic (first note). """
        tonic = melody[0]
        tonic_occurrences = melody.count(tonic)
        min_val, max_val = 1, len(melody)
        return (tonic_occurrences - min_val) / (max_val - min_val) if max_val > min_val else 0

    def tonal_purity_score(self, melody, scale):
        """ Scores how well the melody fits within a given scale. """
        in_scale_notes = sum(1 for note in melody if note in scale)
        min_val, max_val = 0, len(melody)
        return (in_scale_notes - min_val) / (max_val - min_val) if max_val > min_val else 0
