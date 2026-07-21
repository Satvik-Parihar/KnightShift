"""
controller/game_controller.py

Mediates between GameState, InputHandler, and MoveHistory. This is the
only place that owns and coordinates all three -- presentation code
(GameScreen) should talk to GameController, not to GameState or
InputHandler directly.
"""

from domain.game_state import GameState
from domain.move_history import MoveHistory
from presentation.input_handler import InputHandler


class GameController:
    """Owns the current game session: board state, input state, move history."""

    def __init__(self):
        self._game_state = None
        self._move_history = None
        self._input_handler = None
        self._start_new_game()

    def _start_new_game(self):
        self._game_state = GameState()
        self._move_history = MoveHistory()
        self._input_handler = InputHandler(self._game_state, on_move=self._on_move_played)

    def _on_move_played(self, move, san):
        self._move_history.add(san)

    # --- Input delegation -------------------------------------------------

    def handle_click(self, pixel_x, pixel_y):
        self._input_handler.handle_click(pixel_x, pixel_y)

    @property
    def selected_square(self):
        return self._input_handler.selected_square

    def legal_move_targets(self):
        return self._input_handler.legal_move_targets()

    @property
    def last_move(self):
        return self._input_handler.last_move

    # --- Game state accessors ---------------------------------------------

    @property
    def game_state(self):
        return self._game_state

    def is_game_over(self):
        return self._game_state.is_game_over()

    def get_result(self):
        return self._game_state.get_result()

    def move_history_pairs(self):
        return self._move_history.formatted_pairs()

    # --- Actions ------------------------------------------------------------

    def undo(self):
        """Undo the last move played, if any."""
        undone = self._game_state.undo_move()
        if undone:
            self._move_history.pop()
            self._input_handler.deselect()
            self._input_handler.reset_last_move()
        return undone

    def restart(self):
        """Start a brand new game, discarding all current progress."""
        self._start_new_game()
