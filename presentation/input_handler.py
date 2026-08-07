import chess

from presentation.board_renderer import BoardRenderer


class InputHandler:
    def __init__(self, game_state, on_move=None, flipped=False):
        self._game_state = game_state
        self._selected_square = None
        self._last_move = None
        self._on_move = on_move
        self._flipped = flipped
        self._pending_promotion = None

    @property
    def selected_square(self):
        return self._selected_square

    @property
    def last_move(self):
        return self._last_move

    @property
    def pending_promotion(self):
        return self._pending_promotion

    def cancel_pending_promotion(self):
        self._pending_promotion = None

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

    def legal_capture_squares(self):
        """Returns to_squares that are en passant captures (land on empty square)."""
        if self._selected_square is None:
            return set()
        board = self._game_state.get_board()
        return {
            move.to_square
            for move in self._game_state.get_legal_moves()
            if move.from_square == self._selected_square and board.is_en_passant(move)
        }

    def handle_click(self, pixel_x, pixel_y):
        if self._pending_promotion is not None:
            self._handle_promotion_click(pixel_x, pixel_y)
            return

        clicked_square = BoardRenderer.pixel_to_square(pixel_x, pixel_y, self._flipped)
        if clicked_square is None:
            return
        if self._selected_square is None:
            self._try_select(clicked_square)
        else:
            self._try_move_or_reselect(clicked_square)

    def _handle_promotion_click(self, pixel_x, pixel_y):
        option_rects = BoardRenderer.get_promotion_option_rects()
        clicked_piece_type = None
        for piece_type, rect in option_rects.items():
            if rect.collidepoint(pixel_x, pixel_y):
                clicked_piece_type = piece_type
                break

        if clicked_piece_type is not None:
            from_sq = self._pending_promotion["from_square"]
            to_sq = self._pending_promotion["to_square"]
            candidates = self._pending_promotion["candidates"]
            move = next((m for m in candidates if m.promotion == clicked_piece_type), None)
            if move is not None:
                board = self._game_state.get_board()
                captured_piece = board.piece_at(to_sq)
                captured_piece_type = captured_piece.piece_type if captured_piece is not None else None

                san = board.san(move)
                self._game_state.make_move(move)
                self._last_move = move
                self._selected_square = None
                self._pending_promotion = None
                if self._on_move is not None:
                    self._on_move(move, san, captured_piece_type)
                return

        # Clicked outside promotion selection: cancel promotion
        self._pending_promotion = None
        self._selected_square = None

    def _try_select(self, square):
        board = self._game_state.get_board()
        piece = board.piece_at(square)
        if piece is not None and piece.color == self._game_state.turn():
            self._selected_square = square

    def _try_move_or_reselect(self, clicked_square):
        candidates = [
            move for move in self._game_state.get_legal_moves()
            if move.from_square == self._selected_square and move.to_square == clicked_square
        ]
        if candidates:
            if candidates[0].promotion is not None:
                board = self._game_state.get_board()
                self._pending_promotion = {
                    "from_square": self._selected_square,
                    "to_square": clicked_square,
                    "candidates": candidates,
                    "turn": board.turn,
                }
                return

            move = candidates[0]
            board = self._game_state.get_board()
            captured_piece = board.piece_at(move.to_square)
            captured_piece_type = captured_piece.piece_type if captured_piece is not None else None
            if captured_piece_type is None and board.is_en_passant(move):
                captured_piece_type = chess.PAWN

            san = board.san(move)
            self._game_state.make_move(move)
            self._last_move = move
            self._selected_square = None
            if self._on_move is not None:
                self._on_move(move, san, captured_piece_type)
            return

        board = self._game_state.get_board()
        piece = board.piece_at(clicked_square)
        if piece is not None and piece.color == self._game_state.turn():
            self._selected_square = clicked_square
        else:
            self._selected_square = None

    def deselect(self):
        self._selected_square = None
        self._pending_promotion = None
