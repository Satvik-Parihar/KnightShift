import chess

from presentation.board_renderer import BoardRenderer


class InputHandler:
    def __init__(self, game_state, on_move=None):
        self._game_state = game_state
        self._selected_square = None
        self._last_move = None
        self._on_move = on_move

    @property
    def selected_square(self):
        return self._selected_square

    @property
    def last_move(self):
        return self._last_move

    def reset_last_move(self):
        self._last_move = None

    def set_last_move(self, move):
        self._last_move = move

    def legal_move_targets(self):
        if self._selected_square is None:
            return []
        return [
            move.to_square
            for move in self._game_state.get_legal_moves()
            if move.from_square == self._selected_square
        ]

    def handle_click(self, pixel_x, pixel_y):
        clicked_square = BoardRenderer.pixel_to_square(pixel_x, pixel_y)
        if clicked_square is None:
            return
        if self._selected_square is None:
            self._try_select(clicked_square)
        else:
            self._try_move_or_reselect(clicked_square)

    def _try_select(self, square):
        board = self._game_state.get_board()
        piece = board.piece_at(square)
        if piece is not None and piece.color == self._game_state.turn():
            self._selected_square = square

    def _try_move_or_reselect(self, clicked_square):
        move = self._find_legal_move(self._selected_square, clicked_square)
        if move is not None:
            san = self._game_state.get_board().san(move)
            self._game_state.make_move(move)
            self._last_move = move
            self._selected_square = None
            if self._on_move is not None:
                self._on_move(move, san)
            return
        board = self._game_state.get_board()
        piece = board.piece_at(clicked_square)
        if piece is not None and piece.color == self._game_state.turn():
            self._selected_square = clicked_square
        else:
            self._selected_square = None

    def _find_legal_move(self, from_square, to_square):
        candidates = [
            move for move in self._game_state.get_legal_moves()
            if move.from_square == from_square and move.to_square == to_square
        ]
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        for move in candidates:
            if move.promotion == chess.QUEEN:
                return move
        return candidates[0]

    def deselect(self):
        self._selected_square = None
