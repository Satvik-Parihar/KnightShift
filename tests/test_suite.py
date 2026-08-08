import unittest
import time
import chess

from domain.game_state import GameState
from domain.move_history import MoveHistory
from ai.evaluator import evaluate, DEFAULT_WEIGHTS, PIECE_VALUES
from ai.personality import get_weights, PERSONALITY_WEIGHTS
from ai.difficulty import get_depth
from ai.minimax import find_best_move, _minimax
from ai.commentary.events import Event
from ai.commentary.comment_bank import COMMENTS, FALLBACK_COMMENTS
from ai.commentary.commentary_engine import generate_comment
from controller.game_controller import GameController
from config import settings


def _unpruned_minimax(board, depth, maximizing, weights):
    if depth == 0 or board.is_game_over():
        return evaluate(board, weights)

    moves = list(board.legal_moves)
    if maximizing:
        best = float("-inf")
        for move in moves:
            board.push(move)
            val = _unpruned_minimax(board, depth - 1, False, weights)
            board.pop()
            best = max(best, val)
        return best
    else:
        best = float("inf")
        for move in moves:
            board.push(move)
            val = _unpruned_minimax(board, depth - 1, True, weights)
            board.pop()
            best = min(best, val)
        return best


class TestRulesCorrectness(unittest.TestCase):
    def test_initial_board_legal_moves(self):
        gs = GameState()
        moves = gs.get_legal_moves()
        self.assertEqual(len(moves), 20)

    def test_castling_kingside_and_queenside(self):
        # White kingside castling
        board_fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
        gs = GameState()
        gs._board = chess.Board(board_fen)
        legal_sans = [gs._board.san(m) for m in gs.get_legal_moves()]
        self.assertIn("O-O", legal_sans)
        self.assertIn("O-O-O", legal_sans)

        # Execute Kingside castling O-O
        move_oo = gs._board.parse_san("O-O")
        gs.make_move(move_oo)
        self.assertEqual(gs._board.piece_at(chess.G1).symbol(), "K")
        self.assertEqual(gs._board.piece_at(chess.F1).symbol(), "R")

    def test_en_passant(self):
        # Position with en passant capture available on e6
        gs = GameState()
        gs._board = chess.Board("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq e6 0 3")
        legal_sans = [gs._board.san(m) for m in gs.get_legal_moves()]
        self.assertIn("fxe6", legal_sans)

        ep_move = gs._board.parse_san("fxe6")
        gs.make_move(ep_move)
        self.assertEqual(gs._board.piece_at(chess.E6).symbol(), "P")
        self.assertIsNone(gs._board.piece_at(chess.E5))  # Captured black pawn removed

    def test_pawn_promotion(self):
        # White pawn on a7 advancing to a8
        gs = GameState()
        gs._board = chess.Board("8/P7/8/8/8/8/8/4K3 w - - 0 1")
        legal_sans = [gs._board.san(m) for m in gs.get_legal_moves()]
        self.assertIn("a8=Q", legal_sans)

        prom_move = gs._board.parse_san("a8=Q")
        gs.make_move(prom_move)
        self.assertEqual(gs._board.piece_at(chess.A8).symbol(), "Q")

    def test_input_handler_promotion_choices(self):
        from presentation.input_handler import InputHandler
        from presentation.board_renderer import BoardRenderer

        gs = GameState()
        gs._board = chess.Board("8/P7/8/8/8/8/8/4K3 w - - 0 1")
        ih = InputHandler(gs)

        # Select pawn on a7
        ih.handle_click(*BoardRenderer.square_to_pixel(chess.A7))
        self.assertEqual(ih.selected_square, chess.A7)

        # Click target square a8 -> triggers pending promotion
        ih.handle_click(*BoardRenderer.square_to_pixel(chess.A8))
        self.assertIsNotNone(ih.pending_promotion)

        # Click Knight option button
        rects = BoardRenderer.get_promotion_option_rects()
        knight_rect = rects[chess.KNIGHT]
        ih.handle_click(knight_rect.centerx, knight_rect.centery)

        # Verified promoted piece on a8 is Knight
        self.assertIsNone(ih.pending_promotion)
        self.assertEqual(gs._board.piece_at(chess.A8).symbol(), "N")

    def test_board_renderer_promotion_overlay_rendering(self):
        import pygame
        pygame.init()
        from presentation.board_renderer import BoardRenderer

        renderer = BoardRenderer()
        surface = pygame.Surface((settings.BOARD_PIXELS, settings.BOARD_PIXELS))

        # Test White promotion overlay rendering
        pending_white = {"turn": chess.WHITE}
        renderer._draw_promotion_overlay(surface, pending_white)

        # Test Black promotion overlay rendering
        pending_black = {"turn": chess.BLACK}
        renderer._draw_promotion_overlay(surface, pending_black)

    def test_check_checkmate_stalemate_detection(self):
        # Scholar's mate position before final move
        gs = GameState()
        gs._board = chess.Board("r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4")
        self.assertFalse(gs.is_check())
        self.assertFalse(gs.is_game_over())

        # Execute Qxf7#
        gs.make_move(gs._board.parse_san("Qxf7#"))
        self.assertTrue(gs.is_check())
        self.assertTrue(gs.is_game_over())
        self.assertIn("Checkmate", gs.get_result())
        self.assertIn("White wins", gs.get_result())

    def test_draw_conditions(self):
        # Stalemate
        gs = GameState()
        gs._board = chess.Board("k7/8/1Q6/8/8/8/8/4K3 b - - 0 1")
        self.assertTrue(gs.is_game_over())
        self.assertEqual(gs.get_result(), "Draw by stalemate")

        # Insufficient material (King vs King)
        gs2 = GameState()
        gs2._board = chess.Board("8/8/8/4k3/8/8/4K3/8 w - - 0 1")
        self.assertTrue(gs2.is_game_over())
        self.assertEqual(gs2.get_result(), "Draw by insufficient material")


class TestMoveHistoryAndUndo(unittest.TestCase):
    def test_move_history_and_formatting(self):
        mh = MoveHistory()
        mh.add("e4")
        mh.add("e5")
        mh.add("Nf3")
        pairs = mh.formatted_pairs()
        self.assertEqual(len(pairs), 2)
        self.assertEqual(pairs[0], (1, "e4", "e5"))
        self.assertEqual(pairs[1], (2, "Nf3", None))

    def test_undo_vs_human(self):
        gc = GameController(vs_ai=False)
        gc.handle_click(*self._square_to_pixels(chess.E2, flipped=False))
        gc.handle_click(*self._square_to_pixels(chess.E4, flipped=False))
        self.assertEqual(len(gc.move_history_pairs()), 1)

        res = gc.undo()
        self.assertTrue(res)
        self.assertEqual(len(gc.move_history_pairs()), 0)
        self.assertEqual(gc.game_state.get_board().fen(), chess.Board().fen())

    def test_undo_vs_ai_white_and_black(self):
        # Player as White vs AI
        gc_white = GameController(vs_ai=True, player_color="White")
        gc_white.handle_click(*self._square_to_pixels(chess.E2, flipped=False))
        gc_white.handle_click(*self._square_to_pixels(chess.E4, flipped=False))
        # Wait for AI turn processing
        gc_white.update()
        time.sleep(0.7)
        gc_white.update()

        # Undo should clear both moves or current state cleanly
        gc_white.undo()
        self.assertEqual(len(gc_white.move_history_pairs()), 0)

        # Player as Black vs AI
        gc_black = GameController(vs_ai=True, player_color="Black")
        # AI moves as White first
        time.sleep(0.7)
        gc_black.update()
        self.assertEqual(len(gc_black.move_history_pairs()), 1)

        # Player (Black) makes move
        black_legal = gc_black.game_state.get_legal_moves()
        self.assertTrue(len(black_legal) > 0)
        move = black_legal[0]
        gc_black.handle_click(*self._square_to_pixels(move.from_square, flipped=True))
        gc_black.handle_click(*self._square_to_pixels(move.to_square, flipped=True))

        # Undo in vs AI mode
        gc_black.undo()
        # Should clear both or return to AI thinking state cleanly
        self.assertFalse(gc_black.is_game_over())

    def test_undo_after_castling_and_en_passant(self):
        # Castling undo
        gs = GameState()
        gs._board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        initial_fen = gs._board.fen()
        gs.make_move(gs._board.parse_san("O-O"))
        gs.undo_move()
        self.assertEqual(gs._board.fen(), initial_fen)

        # En passant undo
        gs_ep = GameState()
        gs_ep._board = chess.Board("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq e6 0 3")
        initial_ep_fen = gs_ep._board.fen()
        gs_ep.make_move(gs_ep._board.parse_san("fxe6"))
        gs_ep.undo_move()
        self.assertEqual(gs_ep._board.fen(), initial_ep_fen)

    def _square_to_pixels(self, square, flipped=False):
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        col = (7 - file_idx) if flipped else file_idx
        row = rank_idx if flipped else (7 - rank_idx)
        return col * settings.SQUARE_SIZE + 10, row * settings.SQUARE_SIZE + 10


class TestAISearchAndMinimax(unittest.TestCase):
    def test_forced_checkmate_detection(self):
        # Scholar's mate opportunity for White: Qxf7#
        gs = GameState()
        gs._board = chess.Board("r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4")
        best_move = find_best_move(gs, depth=2)
        self.assertEqual(gs._board.san(best_move), "Qxf7#")

    def test_alphabeta_pruning_equivalence_to_unpruned_minimax(self):
        test_fens = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "r1bqk2r/pppp1ppp/2n2n2/4p3/1b2P3/2NP1N2/PPP2PPP/R1BQKB1R w KQkq - 1 5",
            "r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4",
            "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
            "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
            "8/2p5/8/1p6/1P6/8/2P5/k1K5 w - - 0 1",
            "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
            "8/8/4k3/8/8/4K3/8/8 w - - 0 1",
        ]

        for fen in test_fens:
            board = chess.Board(fen)
            gs = GameState()
            gs._board = board

            for depth in (1, 2):
                maximizing = board.turn == chess.WHITE
                unpruned_score = _unpruned_minimax(board.copy(), depth, maximizing, DEFAULT_WEIGHTS)
                ab_move = find_best_move(gs, depth=depth, weights=DEFAULT_WEIGHTS)

                board.push(ab_move)
                ab_score = _minimax(board, depth - 1, float("-inf"), float("inf"), not maximizing, DEFAULT_WEIGHTS)
                board.pop()

                self.assertEqual(ab_score, unpruned_score,
                                 f"Score mismatch at depth {depth} for FEN {fen}: AB={ab_score}, Unpruned={unpruned_score}")

    def test_time_bounded_search_cutoff(self):
        gs = GameState()

        # Extremely tight time budget of 1ms must unwinds quickly and return a legal move
        start = time.monotonic()
        move = find_best_move(gs, depth=4, time_budget_ms=1)
        elapsed_ms = (time.monotonic() - start) * 1000

        self.assertIsNotNone(move)
        self.assertIn(move, gs.get_legal_moves())
        self.assertLess(elapsed_ms, 500)

    def test_difficulty_depths(self):
        self.assertEqual(get_depth("Easy"), 1)
        self.assertEqual(get_depth("Medium"), 2)
        self.assertEqual(get_depth("Hard"), 3)
        self.assertEqual(get_depth("Expert"), 4)


class TestPersonalitiesAndEvaluator(unittest.TestCase):
    def test_personality_weights(self):
        coach_w = get_weights("Coach")
        comp_w = get_weights("Competitive")
        funny_w = get_weights("Funny")

        self.assertEqual(coach_w["aggression"], 0)
        self.assertEqual(comp_w["aggression"], 25)
        self.assertEqual(funny_w["randomness"], 40)

    def test_deterministic_funny_jitter(self):
        board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/4p3/1b2P3/2NP1N2/PPP2PPP/R1BQKB1R w KQkq - 1 5")
        funny_w = get_weights("Funny")

        eval1 = evaluate(board, funny_w)
        eval2 = evaluate(board, funny_w)

        self.assertEqual(eval1, eval2, "Funny personality jitter must be 100% deterministic for identical board FEN")


class TestCommentaryEngineAndEvents(unittest.TestCase):
    def test_event_classification_and_comment_generation(self):
        all_events = [
            Event.OPENING, Event.GOOD_MOVE, Event.BRILLIANT_MOVE, Event.BLUNDER,
            Event.CAPTURE, Event.CAPTURE_QUEEN, Event.CAPTURE_ROOK, Event.CHECK,
            Event.CHECKMATE, Event.STALEMATE, Event.PROMOTION
        ]
        personalities = ["Coach", "Competitive", "Funny"]

        for p in personalities:
            for ev in all_events:
                comment = generate_comment(p, ev)
                self.assertIsNotNone(comment)
                self.assertIsInstance(comment, str)
                self.assertTrue(len(comment) > 0)

    def test_fallback_comment_pool(self):
        comment = generate_comment("UnknownPersonality", Event.CHECKMATE)
        self.assertIn(comment, FALLBACK_COMMENTS[Event.CHECKMATE])


class TestForfeitAndOngoingControls(unittest.TestCase):
    def test_ongoing_state_and_forfeit_vs_human(self):
        gc = GameController(vs_ai=False)
        self.assertFalse(gc.is_ongoing)
        self.assertFalse(gc.forfeit())

        gc.handle_click(*self._square_to_pixels(chess.E2))
        gc.handle_click(*self._square_to_pixels(chess.E4))
        self.assertTrue(gc.is_ongoing)

        forfeited = gc.forfeit()
        self.assertTrue(forfeited)
        self.assertTrue(gc.is_game_over())
        self.assertFalse(gc.is_ongoing)
        self.assertIn("Forfeit", gc.get_result())
        self.assertIn("White wins", gc.get_result())

    def test_forfeit_vs_ai(self):
        gc = GameController(vs_ai=True, player_color="White")
        gc.handle_click(*self._square_to_pixels(chess.E2))
        gc.handle_click(*self._square_to_pixels(chess.E4))
        self.assertTrue(gc.is_ongoing)

        forfeited = gc.forfeit()
        self.assertTrue(forfeited)
        self.assertTrue(gc.is_game_over())
        self.assertIn("Forfeit - Black wins", gc.get_result())

    def _square_to_pixels(self, square, flipped=False):
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        col = (7 - file_idx) if flipped else file_idx
        row = rank_idx if flipped else (7 - rank_idx)
        return col * settings.SQUARE_SIZE + 10, row * settings.SQUARE_SIZE + 10


if __name__ == "__main__":
    unittest.main()
