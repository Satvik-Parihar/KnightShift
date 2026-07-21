"""
presentation/ui_panel.py

Draws the side panel: title, whose turn it is (or the game result if
finished), and the move history list. Reads only from GameController --
never mutates it.
"""

import pygame

from config import settings


class UIPanel:
    """Renders the side panel contents onto a given surface."""

    def __init__(self):
        self._heading_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_HEADING)
        self._text_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_TEXT)

    def draw(self, surface, controller):
        x_offset = settings.BOARD_PIXELS + 20
        y = 20

        title = self._heading_font.render("KnightShift", True, settings.COLOR_PANEL_HEADING)
        surface.blit(title, (x_offset, y))
        y += 45

        status_text = self._status_text(controller)
        status_surface = self._text_font.render(status_text, True, settings.COLOR_PANEL_TEXT)
        surface.blit(status_surface, (x_offset, y))
        y += 40

        y = self._draw_move_history(surface, controller, x_offset, y)

    def _status_text(self, controller):
        if controller.is_game_over():
            return controller.get_result()

        board = controller.game_state.get_board()
        turn_name = "White" if board.turn else "Black"
        check_suffix = " (in check)" if controller.game_state.is_check() else ""
        return f"{turn_name} to move{check_suffix}"

    def _draw_move_history(self, surface, controller, x_offset, y):
        heading = self._text_font.render("Move History:", True, settings.COLOR_PANEL_HEADING)
        surface.blit(heading, (x_offset, y))
        y += 30

        line_height = settings.FONT_SIZE_PANEL_TEXT + 6
        max_y = settings.WINDOW_HEIGHT - 20

        for move_number, white_san, black_san in controller.move_history_pairs():
            if y > max_y:
                break

            black_part = black_san if black_san else ""
            line = f"{move_number}. {white_san}  {black_part}"
            line_surface = self._text_font.render(line, True, settings.COLOR_PANEL_TEXT)
            surface.blit(line_surface, (x_offset, y))
            y += line_height

        return y
