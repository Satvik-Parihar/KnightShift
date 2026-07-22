import chess
import pygame

from config import settings

PIECE_GLYPHS = {
    "P": "\u2659", "N": "\u2658", "B": "\u2657",
    "R": "\u2656", "Q": "\u2655", "K": "\u2654",
    "p": "\u265F", "n": "\u265E", "b": "\u265D",
    "r": "\u265C", "q": "\u265B", "k": "\u265A",
}

FONT_CANDIDATES = ["segoeuisymbol", "dejavusans", "arialunicodems", "arial"]


class BoardRenderer:
    def __init__(self):
        self._font = self._load_piece_font()

    def _load_piece_font(self):
        size = int(settings.SQUARE_SIZE * 0.75)
        for name in FONT_CANDIDATES:
            font = pygame.font.SysFont(name, size)
            test_surface = font.render(PIECE_GLYPHS["K"], True, (0, 0, 0))
            if test_surface.get_width() > 0:
                return font
        return pygame.font.Font(None, size)

    @staticmethod
    def square_to_pixel(square):
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)
        col = file_index
        row = 7 - rank_index
        x = col * settings.SQUARE_SIZE
        y = row * settings.SQUARE_SIZE
        return x, y

    @staticmethod
    def pixel_to_square(pixel_x, pixel_y):
        if not (0 <= pixel_x < settings.BOARD_PIXELS and 0 <= pixel_y < settings.BOARD_PIXELS):
            return None
        col = pixel_x // settings.SQUARE_SIZE
        row = pixel_y // settings.SQUARE_SIZE
        file_index = col
        rank_index = 7 - row
        return chess.square(file_index, rank_index)

    def draw_board(self, surface, game_state, selected_square=None,
                    legal_move_targets=None, last_move=None):
        legal_move_targets = legal_move_targets or []
        self._draw_squares(surface)
        self._draw_last_move_highlight(surface, last_move)
        self._draw_check_highlight(surface, game_state)
        self._draw_selected_highlight(surface, selected_square)
        self._draw_legal_move_markers(surface, legal_move_targets)
        self._draw_pieces(surface, game_state)

    def _draw_squares(self, surface):
        for rank_index in range(8):
            for file_index in range(8):
                square = chess.square(file_index, rank_index)
                x, y = self.square_to_pixel(square)
                is_light = (file_index + rank_index) % 2 == 1
                color = settings.COLOR_LIGHT_SQUARE if is_light else settings.COLOR_DARK_SQUARE
                pygame.draw.rect(surface, color, (x, y, settings.SQUARE_SIZE, settings.SQUARE_SIZE))

    def _draw_last_move_highlight(self, surface, last_move):
        if last_move is None:
            return
        for square in (last_move.from_square, last_move.to_square):
            x, y = self.square_to_pixel(square)
            highlight = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill((*settings.COLOR_HIGHLIGHT_LAST_MOVE, 100))
            surface.blit(highlight, (x, y))

    def _draw_check_highlight(self, surface, game_state):
        if not game_state.is_check():
            return
        board = game_state.get_board()
        king_square = board.king(game_state.turn())
        if king_square is None:
            return
        x, y = self.square_to_pixel(king_square)
        highlight = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill((*settings.COLOR_HIGHLIGHT_CHECK, 120))
        surface.blit(highlight, (x, y))

    def _draw_selected_highlight(self, surface, selected_square):
        if selected_square is None:
            return
        x, y = self.square_to_pixel(selected_square)
        highlight = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill((*settings.COLOR_HIGHLIGHT_SELECTED, 140))
        surface.blit(highlight, (x, y))

    def _draw_legal_move_markers(self, surface, legal_move_targets):
        radius = settings.SQUARE_SIZE // 6
        for square in legal_move_targets:
            x, y = self.square_to_pixel(square)
            marker = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(
                marker, (*settings.COLOR_HIGHLIGHT_LEGAL_MOVE, 160),
                (settings.SQUARE_SIZE // 2, settings.SQUARE_SIZE // 2), radius
            )
            surface.blit(marker, (x, y))

    def _draw_pieces(self, surface, game_state):
        board = game_state.get_board()
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            glyph = PIECE_GLYPHS[piece.symbol()]
            text_color = (
                settings.COLOR_WHITE_PIECE_TEXT if piece.color == chess.WHITE
                else settings.COLOR_BLACK_PIECE_TEXT
            )
            rendered = self._font.render(glyph, True, text_color)
            x, y = self.square_to_pixel(square)
            rect = rendered.get_rect(
                center=(x + settings.SQUARE_SIZE // 2, y + settings.SQUARE_SIZE // 2)
            )
            surface.blit(rendered, rect)
