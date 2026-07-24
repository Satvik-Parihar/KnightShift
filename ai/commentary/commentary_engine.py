import random

from ai.commentary.comment_bank import COMMENTS, FALLBACK_COMMENTS


def generate_comment(personality, event):
    if event is None:
        return None

    pool = COMMENTS.get(personality, {}).get(event)
    if not pool:
        pool = FALLBACK_COMMENTS.get(event, ["Interesting move."])

    return random.choice(pool)
