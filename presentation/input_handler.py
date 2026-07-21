"""
presentation/input_handler.py

Converts raw mouse input into chess moves via a two-click pattern:
click a square with your piece on it (selects it, shows legal
destinations), then click a destination square (attempts the move).

This module owns UI-only state (which square is currently selected) --
it never mutates GameState directly except by calling its public
make_move() method, keeping GameState as the single source of truth.
"""

import chess

from presentation.board_renderer import BoardRenderer


class InputHandler:
    """Tracks click-to-move selection state and applies moves to a GameState."""

    def __init__(self, game_state):
        self._game_state = game_state
        self._selected_square = None
        self._last_move = None

    @property
    def selected_square(self):
        return self._selected_square

    @property
    def last_move(self):
        return self._last_move

    def legal_move_targets(self):
        """
        Return the list of destination squares the currently selected
        piece can legally move to. Empty if nothing is selected.
        """
        if self._selected_square is None:
            return []

        return [
            move.to_square
            for move in self._game_state.get_legal_moves()
            if move.from_square == self._selected_square
        ]

    def handle_click(self, pixel_x, pixel_y):
        """
        Process a mouse click at the given pixel position (relative to the
        board surface's top-left corner). Handles both selecting a piece
        and attempting a move, depending on current state.
        """
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
            self._game_state.make_move(move)
            self._last_move = move
            self._selected_square = None
            return

        board = self._game_state.get_board()
        piece = board.piece_at(clicked_square)
        if piece is not None and piece.color == self._game_state.turn():
            self._selected_square = clicked_square
        else:
            self._selected_square = None

    def _find_legal_move(self, from_square, to_square):
        """
        Find the legal move from from_square to to_square, if one exists.
        Defaults to queen promotion when multiple candidate moves exist
        (i.e. when the move is a pawn promotion).
        """
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
        """Clear the current selection without making a move."""
        self._selected_square = None
