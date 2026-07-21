"""
domain/move_history.py

Tracks the sequence of moves played, in Standard Algebraic Notation
(SAN), for display and for supporting undo. This class only stores
strings -- it does not itself talk to python-chess or GameState.
"""


class MoveHistory:
    """Ordered record of moves played, as SAN strings (one per ply)."""

    def __init__(self):
        self._entries = []

    def add(self, san):
        self._entries.append(san)

    def pop(self):
        if self._entries:
            self._entries.pop()

    def clear(self):
        self._entries.clear()

    def get_entries(self):
        return list(self._entries)

    def formatted_pairs(self):
        """
        Return [(move_number, white_san, black_san_or_None), ...] for
        display in a two-column move list, matching how chess notation
        is conventionally shown (e.g. "1. e4 e5").
        """
        pairs = []
        for i in range(0, len(self._entries), 2):
            move_number = i // 2 + 1
            white_san = self._entries[i]
            black_san = self._entries[i + 1] if i + 1 < len(self._entries) else None
            pairs.append((move_number, white_san, black_san))
        return pairs
