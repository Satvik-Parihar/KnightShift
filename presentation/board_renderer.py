import os

import chess
import pygame
import pygame.gfxdraw

from config import settings

PIECE_FILE_NAMES = {
    "P": "wP", "N": "wN", "B": "wB", "R": "wR", "Q": "wQ", "K": "wK",
    "p": "bP", "n": "bN", "b": "bB", "r": "bR", "q": "bQ", "k": "bK",
}


class BoardRenderer:
    def __init__(self):
        self._piece_images = self._load_piece_images()

    def _load_piece_images(self):
        images = {}
        target_size = int(settings.SQUARE_SIZE * 0.88)
        for symbol, file_name in PIECE_FILE_NAMES.items():
            path = os.path.join(settings.PIECES_ASSET_PATH, f"{file_name}.png")
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                images[symbol] = pygame.transform.smoothscale(raw, (target_size, target_size))
        return images

    @staticmethod
    def square_to_pixel(square, flipped=False):
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)
        if flipped:
            col = 7 - file_index
            row = rank_index
        else:
            col = file_index
            row = 7 - rank_index
        x = col * settings.SQUARE_SIZE
        y = row * settings.SQUARE_SIZE
        return x, y

    @staticmethod
    def pixel_to_square(pixel_x, pixel_y, flipped=False):
        if not (0 <= pixel_x < settings.BOARD_PIXELS and 0 <= pixel_y < settings.BOARD_PIXELS):
            return None
        col = pixel_x // settings.SQUARE_SIZE
        row = pixel_y // settings.SQUARE_SIZE
        if flipped:
            file_index = 7 - col
            rank_index = row
        else:
            file_index = col
            rank_index = 7 - row
        return chess.square(file_index, rank_index)

    def draw_board(self, surface, game_state, selected_square=None,
                    legal_move_targets=None, last_move=None, flipped=False):
        legal_move_targets = legal_move_targets or []
        self._draw_squares(surface, flipped)
        self._draw_last_move_highlight(surface, last_move, flipped)
        self._draw_check_highlight(surface, game_state, flipped)
        self._draw_selected_highlight(surface, selected_square, flipped)
        self._draw_legal_move_markers(surface, legal_move_targets, flipped)
        self._draw_pieces(surface, game_state, flipped)
        self._draw_board_border(surface)
        self._draw_coordinates(surface, flipped)

    def _draw_squares(self, surface, flipped):
        for rank_index in range(8):
            for file_index in range(8):
                square = chess.square(file_index, rank_index)
                x, y = self.square_to_pixel(square, flipped)
                is_light = (file_index + rank_index) % 2 == 1
                color = settings.COLOR_LIGHT_SQUARE if is_light else settings.COLOR_DARK_SQUARE
                pygame.draw.rect(surface, color, (x, y, settings.SQUARE_SIZE, settings.SQUARE_SIZE))

    def _draw_coordinates(self, surface, flipped):
        label_font = pygame.font.SysFont(settings.FONT_NAME, 12, bold=True)
        files = "abcdefgh"
        for file_index in range(8):
            square = chess.square(file_index, 0)
            x, y = self.square_to_pixel(square, flipped)
            is_light = (file_index + 0) % 2 == 1
            color = settings.COLOR_DARK_SQUARE if is_light else settings.COLOR_LIGHT_SQUARE
            label = files[file_index]
            text = label_font.render(label, True, color)
            surface.blit(text, (x + settings.SQUARE_SIZE - 12, y + settings.SQUARE_SIZE - 15))

    def _draw_board_border(self, surface):
        pygame.draw.rect(
            surface, settings.COLOR_BOARD_BORDER,
            (0, 0, settings.BOARD_PIXELS, settings.BOARD_PIXELS), width=4
        )

    def _draw_last_move_highlight(self, surface, last_move, flipped):
        if last_move is None:
            return
        for square in (last_move.from_square, last_move.to_square):
            x, y = self.square_to_pixel(square, flipped)
            highlight = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill((*settings.COLOR_HIGHLIGHT_LAST_MOVE, 160))
            surface.blit(highlight, (x, y))

    def _draw_check_highlight(self, surface, game_state, flipped):
        if not game_state.is_check():
            return
        board = game_state.get_board()
        king_square = board.king(game_state.turn())
        if king_square is None:
            return
        x, y = self.square_to_pixel(king_square, flipped)
        highlight = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill((*settings.COLOR_HIGHLIGHT_CHECK, 160))
        surface.blit(highlight, (x, y))

    def _draw_selected_highlight(self, surface, selected_square, flipped):
        if selected_square is None:
            return
        x, y = self.square_to_pixel(selected_square, flipped)
        highlight = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill((*settings.COLOR_HIGHLIGHT_SELECTED, 190))
        surface.blit(highlight, (x, y))

    def _draw_legal_move_markers(self, surface, legal_move_targets, flipped):
        radius = settings.SQUARE_SIZE // 7
        for square in legal_move_targets:
            x, y = self.square_to_pixel(square, flipped)
            marker = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
            center_x = settings.SQUARE_SIZE // 2
            center_y = settings.SQUARE_SIZE // 2

            fill_color = (40, 40, 40, 90)
            pygame.gfxdraw.filled_circle(marker, center_x, center_y, radius, fill_color)
            pygame.gfxdraw.aacircle(marker, center_x, center_y, radius, fill_color)

            surface.blit(marker, (x, y))

    def _draw_pieces(self, surface, game_state, flipped):
        board = game_state.get_board()
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            symbol = piece.symbol()
            image = self._piece_images.get(symbol)
            x, y = self.square_to_pixel(square, flipped)
            if image is not None:
                rect = image.get_rect(
                    center=(x + settings.SQUARE_SIZE // 2, y + settings.SQUARE_SIZE // 2)
                )
                surface.blit(image, rect)
