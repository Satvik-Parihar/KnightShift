import chess


class GameState:
    def __init__(self):
        self._board = chess.Board()

    def get_legal_moves(self):
        return list(self._board.legal_moves)

    def make_move(self, move):
        if move not in self._board.legal_moves:
            return False
        self._board.push(move)
        return True

    def undo_move(self):
        if not self._board.move_stack:
            return False
        self._board.pop()
        return True

    def is_game_over(self):
        return self._board.is_game_over()

    def get_result(self):
        if not self._board.is_game_over():
            return "In progress"
        if self._board.is_checkmate():
            winner = "Black" if self._board.turn == chess.WHITE else "White"
            return f"Checkmate - {winner} wins"
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
        return self._board.is_check()

    def turn(self):
        return self._board.turn

    def get_board(self):
        return self._board
