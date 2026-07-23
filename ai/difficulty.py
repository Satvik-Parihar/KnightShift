from config.settings import DIFFICULTY_PRESETS, DEFAULT_DIFFICULTY


def get_depth(difficulty_name):
    preset = DIFFICULTY_PRESETS.get(difficulty_name, DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY])
    return preset["depth"]
