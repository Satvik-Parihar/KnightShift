class MoveHistory:
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
        pairs = []
        for i in range(0, len(self._entries), 2):
            move_number = i // 2 + 1
            white_san = self._entries[i]
            black_san = self._entries[i + 1] if i + 1 < len(self._entries) else None
            pairs.append((move_number, white_san, black_san))
        return pairs
