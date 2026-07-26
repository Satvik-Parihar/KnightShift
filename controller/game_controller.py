import time
import random
import chess

from domain.game_state import GameState
from domain.move_history import MoveHistory
from presentation.input_handler import InputHandler
from ai.minimax import find_best_move
from ai.evaluator import evaluate
from ai.difficulty import get_depth
from ai.personality import get_weights
from ai.commentary.events import Event
from ai.commentary.commentary_engine import generate_comment
from config.settings import (
    DEFAULT_DIFFICULTY,
    AI_THINK_DELAY_MS,
    AI_TIME_BUDGET_MS,
    DIFFICULTY_PRESETS,
    AI_PERSONALITIES,
    DEFAULT_PERSONALITY,
    PLAYER_COLOR_OPTIONS,
    DEFAULT_PLAYER_COLOR,
)

BLUNDER_THRESHOLD = -150
GOOD_MOVE_THRESHOLD = 100
BRILLIANT_THRESHOLD = 250


class GameController:
    def __init__(self, vs_ai=True, difficulty=DEFAULT_DIFFICULTY,
                 personality=DEFAULT_PERSONALITY, player_color=DEFAULT_PLAYER_COLOR):
        self._vs_ai = vs_ai
        self._difficulty = difficulty
        self._personality = personality
        self._player_color_choice = player_color
        self._ai_color = chess.BLACK
        self._board_flipped = False
        self._ai_thinking = False
        self._ai_think_deadline = None
        self._last_captured_piece_type = None
        self._latest_comment = None
        self._game_state = None
        self._move_history = None
        self._input_handler = None
        self._start_new_game()

    def _resolve_ai_color(self):
        choice = self._player_color_choice
        if choice == "White":
            return chess.BLACK
        if choice == "Black":
            return chess.WHITE
        return random.choice([chess.WHITE, chess.BLACK])

    def _start_new_game(self):
        self._ai_color = self._resolve_ai_color() if self._vs_ai else chess.BLACK
        self._board_flipped = self._vs_ai and self._ai_color == chess.WHITE

        self._game_state = GameState()
        self._move_history = MoveHistory()
        self._input_handler = InputHandler(
            self._game_state, on_move=self._on_move_played, flipped=self._board_flipped
        )
        self._ai_thinking = False
        self._ai_think_deadline = None
        self._last_captured_piece_type = None
        self._latest_comment = None

        self._maybe_start_ai_thinking()

    def _on_move_played(self, move, san, captured_piece_type):
        self._move_history.add(san)
        self._last_captured_piece_type = captured_piece_type
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
        weights = get_weights(self._personality)
        eval_before = evaluate(self._game_state.get_board())

        ai_move = find_best_move(self._game_state, depth, weights=weights, time_budget_ms=AI_TIME_BUDGET_MS)
        self._ai_thinking = False
        self._ai_think_deadline = None
        if ai_move is None:
            return

        board = self._game_state.get_board()
        captured_piece = board.piece_at(ai_move.to_square)
        captured_piece_type = captured_piece.piece_type if captured_piece is not None else None
        if captured_piece_type is None and board.is_en_passant(ai_move):
            captured_piece_type = chess.PAWN

        san = board.san(ai_move)
        self._game_state.make_move(ai_move)
        self._move_history.add(san)
        self._input_handler.set_last_move(ai_move)
        self._last_captured_piece_type = captured_piece_type

        self._process_move_event(eval_before, self._ai_color)

    def _process_move_event(self, eval_before, mover_color):
        board = self._game_state.get_board()
        eval_after = evaluate(board)
        swing = (eval_after - eval_before) if mover_color == chess.WHITE else (eval_before - eval_after)
        event = self._classify_event(board, swing)
        self._latest_comment = generate_comment(self._personality, event) if event else None

    def _classify_event(self, board, swing):
        if board.is_checkmate():
            return Event.CHECKMATE
        if board.is_stalemate():
            return Event.STALEMATE

        move = self._input_handler.last_move
        if move is not None and move.promotion is not None:
            return Event.PROMOTION

        if self._last_captured_piece_type == chess.QUEEN:
            return Event.CAPTURE_QUEEN
        if self._last_captured_piece_type == chess.ROOK:
            return Event.CAPTURE_ROOK

        if board.is_check():
            return Event.CHECK

        if swing >= BRILLIANT_THRESHOLD:
            return Event.BRILLIANT_MOVE
        if swing <= BLUNDER_THRESHOLD:
            return Event.BLUNDER

        if self._last_captured_piece_type is not None:
            return Event.CAPTURE

        if swing >= GOOD_MOVE_THRESHOLD:
            return Event.GOOD_MOVE

        if len(self._move_history.get_entries()) <= 2:
            return Event.OPENING

        return None

    @property
    def is_ai_thinking(self):
        return self._ai_thinking

    @property
    def vs_ai(self):
        return self._vs_ai

    @property
    def difficulty(self):
        return self._difficulty

    def cycle_difficulty(self):
        names = list(DIFFICULTY_PRESETS.keys())
        current_index = names.index(self._difficulty)
        next_index = (current_index + 1) % len(names)
        self._difficulty = names[next_index]

    @property
    def personality(self):
        return self._personality

    def cycle_personality(self):
        current_index = AI_PERSONALITIES.index(self._personality)
        next_index = (current_index + 1) % len(AI_PERSONALITIES)
        self._personality = AI_PERSONALITIES[next_index]

    @property
    def player_color(self):
        return self._player_color_choice

    @property
    def player_color_choice(self):
        return self._player_color_choice

    def cycle_player_color(self):
        current_index = PLAYER_COLOR_OPTIONS.index(self._player_color_choice)
        next_index = (current_index + 1) % len(PLAYER_COLOR_OPTIONS)
        self._player_color_choice = PLAYER_COLOR_OPTIONS[next_index]
        self._start_new_game()

    @property
    def board_flipped(self):
        return self._board_flipped

    @property
    def latest_comment(self):
        return self._latest_comment

    def set_mode(self, vs_ai):
        if self._vs_ai == vs_ai:
            return
        self._vs_ai = vs_ai
        self._start_new_game()

    def handle_click(self, pixel_x, pixel_y):
        if self._game_state.is_game_over():
            return

        moves_before = len(self._move_history.get_entries())
        eval_before = evaluate(self._game_state.get_board())

        self._input_handler.handle_click(pixel_x, pixel_y)

        if len(self._move_history.get_entries()) > moves_before:
            mover_color = not self._game_state.turn()
            self._process_move_event(eval_before, mover_color)

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
        if not undone:
            return False

        self._move_history.pop()

        if self._vs_ai and self._game_state.turn() == self._ai_color and self._game_state.get_board().move_stack:
            self._game_state.undo_move()
            self._move_history.pop()

        self._ai_thinking = False
        self._ai_think_deadline = None
        self._last_captured_piece_type = None
        self._latest_comment = None
        self._input_handler.deselect()
        self._input_handler.reset_last_move()
        return True

    def restart(self):
        self._start_new_game()
