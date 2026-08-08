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
                raw = pygame.image.load(path)
                if pygame.display.get_surface() is not None:
                    raw = raw.convert_alpha()
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

    PROMOTION_PIECES = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    PIECE_NAMES = {
        chess.QUEEN: "Queen",
        chess.ROOK: "Rook",
        chess.BISHOP: "Bishop",
        chess.KNIGHT: "Knight",
    }

    @staticmethod
    def get_promotion_option_rects():
        card_w, card_h = 400, 140
        modal_left = (settings.BOARD_PIXELS - card_w) // 2
        modal_top = (settings.BOARD_PIXELS - card_h) // 2

        btn_w, btn_h = 78, 80
        spacing = 12
        total_w = 4 * btn_w + 3 * spacing
        start_x = modal_left + (card_w - total_w) // 2
        start_y = modal_top + 42

        rects = {}
        for i, piece_type in enumerate(BoardRenderer.PROMOTION_PIECES):
            rx = start_x + i * (btn_w + spacing)
            rects[piece_type] = pygame.Rect(rx, start_y, btn_w, btn_h)
        return rects

    def draw_board(self, surface, game_state, selected_square=None,
                    legal_move_targets=None, last_move=None, flipped=False,
                    pending_promotion=None):
        legal_move_targets = legal_move_targets or []
        board = game_state.get_board()
        capture_targets = {
            sq for sq in legal_move_targets if board.piece_at(sq) is not None
        }
        # Also mark en passant landing squares as captures
        if board.ep_square is not None and board.ep_square in legal_move_targets:
            capture_targets.add(board.ep_square)
        self._draw_squares(surface, flipped)
        self._draw_last_move_highlight(surface, last_move, flipped)
        self._draw_check_highlight(surface, game_state, flipped)
        self._draw_selected_highlight(surface, selected_square, flipped)
        self._draw_legal_move_markers(surface, legal_move_targets, capture_targets, flipped)
        self._draw_pieces(surface, game_state, flipped)
        self._draw_board_border(surface)
        self._draw_coordinates(surface, flipped)

        if pending_promotion is not None:
            self._draw_promotion_overlay(surface, pending_promotion)

    def _draw_promotion_overlay(self, surface, pending_promotion):
        card_w, card_h = 400, 140
        modal_left = (settings.BOARD_PIXELS - card_w) // 2
        modal_top = (settings.BOARD_PIXELS - card_h) // 2
        modal_rect = pygame.Rect(modal_left, modal_top, card_w, card_h)

        overlay = pygame.Surface((settings.BOARD_PIXELS, settings.BOARD_PIXELS), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (35, 35, 35), modal_rect, border_radius=12)
        pygame.draw.rect(surface, (70, 130, 90), modal_rect, width=2, border_radius=12)

        title_font = pygame.font.SysFont(settings.FONT_NAME, 18, bold=True)
        title_surface = title_font.render("CHOOSE PROMOTION PIECE", True, (240, 240, 240))
        title_rect = title_surface.get_rect(center=(modal_left + card_w // 2, modal_top + 22))
        surface.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        turn_color = pending_promotion.get("turn", chess.WHITE)

        label_font = pygame.font.SysFont(settings.FONT_NAME, 12, bold=True)
        fallback_font = pygame.font.SysFont(settings.FONT_NAME, 24, bold=True)

        option_rects = self.get_promotion_option_rects()
        for piece_type, rect in option_rects.items():
            is_hover = rect.collidepoint(mouse_pos)
            bg = (70, 130, 90) if is_hover else (55, 55, 55)
            border_color = (140, 220, 160) if is_hover else (80, 80, 80)

            pygame.draw.rect(surface, bg, rect, border_radius=8)
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=8)

            piece_symbol = chess.Piece(piece_type, turn_color).symbol()
            piece_img = self._piece_images.get(piece_symbol)

            if piece_img is not None:
                scaled_img = pygame.transform.smoothscale(piece_img, (48, 48))
                img_rect = scaled_img.get_rect(center=(rect.centerx, rect.top + 30))
                surface.blit(scaled_img, img_rect)
            else:
                text_sf = fallback_font.render(piece_symbol.upper(), True, (240, 240, 240))
                text_rect = text_sf.get_rect(center=(rect.centerx, rect.top + 30))
                surface.blit(text_sf, text_rect)

            name_str = self.PIECE_NAMES.get(piece_type, "")
            name_sf = label_font.render(name_str, True, (255, 255, 255) if is_hover else (200, 200, 200))
            name_rect = name_sf.get_rect(center=(rect.centerx, rect.bottom - 13))
            surface.blit(name_sf, name_rect)

    def _draw_squares(self, surface, flipped):
        for rank_index in range(8):
            for file_index in range(8):
                square = chess.square(file_index, rank_index)
                x, y = self.square_to_pixel(square, flipped)
                is_light = (file_index + rank_index) % 2 == 1
                color = settings.COLOR_LIGHT_SQUARE if is_light else settings.COLOR_DARK_SQUARE
                pygame.draw.rect(surface, color, (x, y, settings.SQUARE_SIZE, settings.SQUARE_SIZE))

    def _draw_coordinates(self, surface, flipped):
        label_font = pygame.font.SysFont(settings.FONT_NAME, 13, bold=True)
        files = "abcdefgh"
        light_text = (245, 245, 235)
        dark_text = (40, 40, 40)
        for file_index in range(8):
            square = chess.square(file_index, 0)
            x, y = self.square_to_pixel(square, flipped)
            is_light = (file_index + 0) % 2 == 1
            text_color = dark_text if is_light else light_text
            outline_color = light_text if is_light else dark_text

            label = files[file_index]
            pos = (x + settings.SQUARE_SIZE - 13, y + settings.SQUARE_SIZE - 16)

            outline = label_font.render(label, True, outline_color)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                surface.blit(outline, (pos[0] + dx, pos[1] + dy))

            text = label_font.render(label, True, text_color)
            surface.blit(text, pos)

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

    def _draw_legal_move_markers(self, surface, legal_move_targets, capture_targets, flipped):
        dot_radius = settings.SQUARE_SIZE // 7
        ring_outer = settings.SQUARE_SIZE // 2 - 3
        ring_inner = ring_outer - settings.SQUARE_SIZE // 8
        dot_color = (0, 0, 0, 160)
        ring_color = (0, 0, 0, 160)

        for square in legal_move_targets:
            x, y = self.square_to_pixel(square, flipped)
            marker = pygame.Surface((settings.SQUARE_SIZE, settings.SQUARE_SIZE), pygame.SRCALPHA)
            cx = settings.SQUARE_SIZE // 2
            cy = settings.SQUARE_SIZE // 2

            if square in capture_targets:
                # Draw a hollow ring over capture squares
                for r in range(ring_inner, ring_outer + 1):
                    pygame.gfxdraw.aacircle(marker, cx, cy, r, ring_color)
                pygame.gfxdraw.filled_circle(marker, cx, cy, ring_outer, ring_color)
                pygame.gfxdraw.filled_circle(marker, cx, cy, ring_inner, (0, 0, 0, 0))
            else:
                # Draw a filled dot for empty target squares
                pygame.gfxdraw.filled_circle(marker, cx, cy, dot_radius, dot_color)
                pygame.gfxdraw.aacircle(marker, cx, cy, dot_radius, dot_color)

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
