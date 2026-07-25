import time
import chess
from ai.evaluator import evaluate


def find_best_move(game_state, depth, weights=None, time_budget_ms=None):
    board = game_state.get_board()
    maximizing = board.turn == chess.WHITE
    best_move = None
    best_score = float("-inf") if maximizing else float("inf")
    alpha = float("-inf")
    beta = float("inf")

    deadline = (time.monotonic() + time_budget_ms / 1000) if time_budget_ms else None

    for move in _ordered_moves(board):
        if deadline is not None and time.monotonic() > deadline and best_move is not None:
            break

        board.push(move)
        score = _minimax(board, depth - 1, alpha, beta, not maximizing, weights, deadline)
        board.pop()

        if maximizing and score > best_score:
            best_score, best_move = score, move
            alpha = max(alpha, score)
        elif not maximizing and score < best_score:
            best_score, best_move = score, move
            beta = min(beta, score)

    return best_move


def _minimax(board, depth, alpha, beta, maximizing, weights, deadline=None):
    if depth == 0 or board.is_game_over():
        return evaluate(board, weights)

    if deadline is not None and time.monotonic() > deadline:
        return evaluate(board, weights)

    if maximizing:
        best_score = float("-inf")
        for move in _ordered_moves(board):
            board.push(move)
            score = _minimax(board, depth - 1, alpha, beta, False, weights, deadline)
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
            score = _minimax(board, depth - 1, alpha, beta, True, weights, deadline)
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
