import pygame

from config import settings


class UIPanel:
    def __init__(self):
        self._heading_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_HEADING)
        self._text_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_TEXT)
        self._button_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_BUTTON)
        self.undo_button_rect = None
        self.restart_button_rect = None
        self.mode_button_rect = None

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

        y = self._draw_buttons(surface, controller, x_offset, y)
        y += 20

        self._draw_move_history(surface, controller, x_offset, y)

    def _status_text(self, controller):
        if controller.is_game_over():
            return controller.get_result()
        if controller.is_ai_thinking:
            return "AI is thinking..."
        board = controller.game_state.get_board()
        turn_name = "White" if board.turn else "Black"
        check_suffix = " (in check)" if controller.game_state.is_check() else ""
        return f"{turn_name} to move{check_suffix}"

    def _draw_buttons(self, surface, controller, x_offset, y):
        button_width = 110
        button_height = 36
        spacing = 10

        self.undo_button_rect = pygame.Rect(x_offset, y, button_width, button_height)
        self.restart_button_rect = pygame.Rect(x_offset + button_width + spacing, y, button_width, button_height)

        self._draw_button(surface, self.undo_button_rect, "Undo")
        self._draw_button(surface, self.restart_button_rect, "New Game")

        y += button_height + spacing

        mode_width = button_width * 2 + spacing
        self.mode_button_rect = pygame.Rect(x_offset, y, mode_width, button_height)
        mode_label = "Mode: 1P (vs AI)" if controller.vs_ai else "Mode: 2P (vs Human)"
        self._draw_button(surface, self.mode_button_rect, mode_label)

        return y + button_height

    def _draw_button(self, surface, rect, label):
        mouse_pos = pygame.mouse.get_pos()
        color = settings.COLOR_BUTTON_HOVER if rect.collidepoint(mouse_pos) else settings.COLOR_BUTTON_BACKGROUND
        pygame.draw.rect(surface, color, rect, border_radius=6)
        text_surface = self._button_font.render(label, True, settings.COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

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
