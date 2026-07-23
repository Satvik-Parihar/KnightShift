import time
import chess

from domain.game_state import GameState
from domain.move_history import MoveHistory
from presentation.input_handler import InputHandler
from ai.minimax import find_best_move
from ai.difficulty import get_depth
from config.settings import DEFAULT_DIFFICULTY, AI_THINK_DELAY_MS


class GameController:
    def __init__(self, vs_ai=True, ai_color=chess.BLACK, difficulty=DEFAULT_DIFFICULTY):
        self._vs_ai = vs_ai
        self._ai_color = ai_color
        self._difficulty = difficulty
        self._ai_thinking = False
        self._ai_think_deadline = None
        self._game_state = None
        self._move_history = None
        self._input_handler = None
        self._start_new_game()

    def _start_new_game(self):
        self._game_state = GameState()
        self._move_history = MoveHistory()
        self._input_handler = InputHandler(self._game_state, on_move=self._on_move_played)
        self._ai_thinking = False
        self._ai_think_deadline = None

    def _on_move_played(self, move, san):
        self._move_history.add(san)
        self._maybe_start_ai_thinking()

    def _maybe_start_ai_thinking(self):
        if not self._vs_ai or self._game_state.is_game_over():
            return
        if self._game_state.turn() != self._ai_color:
            return
        self._ai_thinking = True
        self._ai_think_deadline = time.monotonic() * 1000 + AI_THINK_DELAY_MS

    def update(self):
        if not self._ai_thinking:
            return
        if time.monotonic() * 1000 < self._ai_think_deadline:
            return
        self._play_ai_move_now()

    def _play_ai_move_now(self):
        depth = get_depth(self._difficulty)
        ai_move = find_best_move(self._game_state, depth)
        self._ai_thinking = False
        self._ai_think_deadline = None
        if ai_move is None:
            return
        san = self._game_state.get_board().san(ai_move)
        self._game_state.make_move(ai_move)
        self._move_history.add(san)
        self._input_handler.set_last_move(ai_move)

    @property
    def is_ai_thinking(self):
        return self._ai_thinking

    @property
    def vs_ai(self):
        return self._vs_ai

    def toggle_mode(self):
        self._vs_ai = not self._vs_ai
        self._start_new_game()

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

    @property
    def game_state(self):
        return self._game_state

    def is_game_over(self):
        return self._game_state.is_game_over()

    def get_result(self):
        return self._game_state.get_result()

    def move_history_pairs(self):
        return self._move_history.formatted_pairs()

    def undo(self):
        undone = self._game_state.undo_move()
        if undone:
            self._move_history.pop()
            self._input_handler.deselect()
            self._input_handler.reset_last_move()
        return undone

    def restart(self):
        self._start_new_game()
