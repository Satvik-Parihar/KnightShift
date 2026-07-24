from ai.evaluator import DEFAULT_WEIGHTS

PERSONALITY_WEIGHTS = {
    "Coach": dict(DEFAULT_WEIGHTS),
    "Competitive": {
        "mobility": 0.15,
        "center": 8,
        "king_safety": 6,
        "pawn_structure": 8,
        "aggression": 25,
        "randomness": 0,
    },
    "Funny": {
        "mobility": 0.1,
        "center": 5,
        "king_safety": 8,
        "pawn_structure": 6,
        "aggression": 10,
        "randomness": 40,
    },
}


def get_weights(personality_name):
    return PERSONALITY_WEIGHTS.get(personality_name, DEFAULT_WEIGHTS)
