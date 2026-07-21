"""
domain/game_state.py

GameState is the single source of truth for the current chess position.
It wraps python-chess's chess.Board so that no other module in the project
(AI, presentation, controller) talks to python-chess directly. This keeps
the rules engine swappable and the rest of the codebase decoupled from a
specific third-party library's API.
"""

import chess


class GameState:
    """Owns the authoritative board state for one game of chess."""

    def __init__(self):
        # chess.Board() starts in the standard chess starting position.
        self._board = chess.Board()

    def get_legal_moves(self):
        """
        Return a list of all legal moves in the current position.

        Used by:
        - input_handler.py, to check whether a player's attempted move is legal
        - ai/minimax.py, to know which moves it's allowed to search
        """
        return list(self._board.legal_moves)

    def make_move(self, move):
        """
        Attempt to apply a move to the board.

        `move` must be a chess.Move object that is already confirmed legal
        (callers should check against get_legal_moves() first, or construct
        the move via find_move-style helpers before calling this).

        Returns True if the move was applied, False if it was illegal.
        """
        if move not in self._board.legal_moves:
            return False

        self._board.push(move)
        return True

    def undo_move(self):
        """
        Undo the last move played, if any.

        Returns True if a move was undone, False if there was no move to undo.
        """
        if not self._board.move_stack:
            return False

        self._board.pop()
        return True

    def is_game_over(self):
        """Return True if the game has ended (checkmate, stalemate, or draw)."""
        return self._board.is_game_over()

    def get_result(self):
        """
        Return a human-readable description of the game outcome.
        Only meaningful once is_game_over() is True.
        """
        if not self._board.is_game_over():
            return "In progress"

        if self._board.is_checkmate():
            winner = "Black" if self._board.turn == chess.WHITE else "White"
            return f"Checkmate — {winner} wins"

        if self._board.is_stalemate():
            return "Draw by stalemate"

        if self._board.is_insufficient_material():
            return "Draw by insufficient material"

        if self._board.is_seventyfive_moves():
            return "Draw by seventy-five move rule"

        if self._board.is_fivefold_repetition():
            return "Draw by fivefold repetition"

        return "Draw"

    def is_check(self):
        """Return True if the side to move is currently in check."""
        return self._board.is_check()

    def turn(self):
        """Return chess.WHITE or chess.BLACK — whose turn it currently is."""
        return self._board.turn

    def get_board(self):
        """
        Return the underlying chess.Board for read-only purposes
        (e.g., the renderer needs to know piece positions).

        Callers should treat this as read-only. Mutating moves should
        always go through make_move()/undo_move() on this GameState,
        not by calling .push()/.pop() on the board directly — otherwise
        this class stops being the single source of truth.
        """
        return self._board
