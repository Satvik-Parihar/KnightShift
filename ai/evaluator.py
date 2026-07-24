import random

import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]

DEFAULT_WEIGHTS = {
    "mobility": 0.1,
    "center": 5,
    "king_safety": 10,
    "pawn_structure": 10,
    "aggression": 0,
    "randomness": 0,
}


def evaluate(board: chess.Board, weights: dict = None) -> float:
    if weights is None:
        weights = DEFAULT_WEIGHTS

    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    score += _material_score(board)
    score += _mobility_score(board) * weights["mobility"]
    score += _center_control_score(board) * weights["center"]
    score += _king_safety_score(board) * weights["king_safety"]
    score += _pawn_structure_score(board) * weights["pawn_structure"]
    score += _threat_score(board) * weights["aggression"]
    score += _personality_jitter(board, weights["randomness"])
    return score


def _material_score(board):
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * len(board.pieces(piece_type, chess.WHITE))
        score -= value * len(board.pieces(piece_type, chess.BLACK))
    return score


def _mobility_score(board):
    return _count_moves_for(board, chess.WHITE) - _count_moves_for(board, chess.BLACK)


def _count_moves_for(board, color):
    if board.turn == color:
        return board.legal_moves.count()
    mirrored = board.copy(stack=False)
    mirrored.turn = color
    return mirrored.legal_moves.count()


def _center_control_score(board):
    score = 0
    for square in CENTER_SQUARES:
        score += len(board.attackers(chess.WHITE, square))
        score -= len(board.attackers(chess.BLACK, square))
    return score


def _king_safety_score(board):
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)
    white_danger = _attacks_near_king(board, white_king, chess.BLACK) if white_king is not None else 0
    black_danger = _attacks_near_king(board, black_king, chess.WHITE) if black_king is not None else 0
    return black_danger - white_danger


def _attacks_near_king(board, king_square, attacking_color):
    danger = 0
    for square in board.attacks(king_square):
        danger += len(board.attackers(attacking_color, square))
    return danger


def _pawn_structure_score(board):
    return _pawn_score_for(board, chess.WHITE) - _pawn_score_for(board, chess.BLACK)


def _pawn_score_for(board, color):
    pawns = board.pieces(chess.PAWN, color)
    file_counts = [0] * 8
    for square in pawns:
        file_counts[chess.square_file(square)] += 1

    penalty = 0
    for file_index, count in enumerate(file_counts):
        if count > 1:
            penalty += (count - 1)
        if count > 0:
            has_left = file_index > 0 and file_counts[file_index - 1] > 0
            has_right = file_index < 7 and file_counts[file_index + 1] > 0
            if not has_left and not has_right:
                penalty += count
    return -penalty


def _threat_score(board):
    score = 0.0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        attackers = board.attackers(not piece.color, square)
        if attackers:
            value = PIECE_VALUES[piece.piece_type] * 0.01
            score += -value if piece.color == chess.WHITE else value
    return score


def _personality_jitter(board, amount):
    if not amount:
        return 0.0
    rng = random.Random(hash(board.board_fen()))
    return rng.uniform(-amount, amount)
