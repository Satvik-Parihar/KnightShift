import chess
from ai.evaluator import evaluate


def find_best_move(game_state, depth):
    board = game_state.get_board()
    maximizing = board.turn == chess.WHITE
    best_move = None
    best_score = float("-inf") if maximizing else float("inf")
    alpha = float("-inf")
    beta = float("inf")

    for move in _ordered_moves(board):
        board.push(move)
        score = _minimax(board, depth - 1, alpha, beta, not maximizing)
        board.pop()

        if maximizing and score > best_score:
            best_score, best_move = score, move
            alpha = max(alpha, score)
        elif not maximizing and score < best_score:
            best_score, best_move = score, move
            beta = min(beta, score)

    return best_move


def _minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        best_score = float("-inf")
        for move in _ordered_moves(board):
            board.push(move)
            score = _minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            best_score = max(best_score, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float("inf")
        for move in _ordered_moves(board):
            board.push(move)
            score = _minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            best_score = min(best_score, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return best_score


def _ordered_moves(board):
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: board.is_capture(move), reverse=True)
    return moves


if __name__ == "__main__":
    from domain.game_state import GameState

    state = GameState()
    move = find_best_move(state, depth=2)
    print("Best move at depth 2:", state.get_board().san(move))
