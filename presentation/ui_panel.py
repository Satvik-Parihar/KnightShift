import pygame

from config import settings
from presentation.avatar import draw_avatar

IDLE_LINES = {
    "Coach": "Let's have a good game. Take your time.",
    "Competitive": "Ready when you are. Let's see what you've got.",
    "Funny": "Hi there! Try not to blunder your queen, okay?",
}


class UIPanel:
    def __init__(self):
        self._heading_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_HEADING)
        self._text_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_TEXT)
        self._button_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_BUTTON)
        self._commentary_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_COMMENTARY)
        self._status_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_TEXT, bold=True)

        self.undo_button_rect = None
        self.restart_button_rect = None
        self.vs_ai_button_rect = None
        self.vs_human_button_rect = None
        self.difficulty_button_rect = None
        self.personality_button_rect = None

    def draw(self, surface, controller):
        x_offset = settings.BOARD_PIXELS + 20
        panel_width = settings.SIDE_PANEL_WIDTH - 40
        y = 18

        if controller.vs_ai:
            y = self._draw_avatar_section(surface, controller, x_offset, panel_width, y)
        else:
            title = self._heading_font.render("KnightShift", True, settings.COLOR_PANEL_HEADING)
            surface.blit(title, (x_offset, y))
            y += 45

        y = self._draw_status_badge(surface, controller, x_offset, panel_width, y)
        y += 14

        y = self._draw_buttons_card(surface, controller, x_offset, panel_width, y)
        y += 16

        self._draw_move_history_card(surface, controller, x_offset, panel_width, y)

    def _draw_avatar_section(self, surface, controller, x_offset, panel_width, y):
        avatar_radius = 30
        avatar_center = (x_offset + avatar_radius, y + avatar_radius)
        draw_avatar(surface, avatar_center, avatar_radius, controller.personality)

        name_surface = self._heading_font.render(controller.personality, True, settings.COLOR_PANEL_HEADING)
        surface.blit(name_surface, (x_offset + avatar_radius * 2 + 14, y + 4))

        bubble_top = y + avatar_radius * 2 + 12
        comment = controller.latest_comment or IDLE_LINES.get(controller.personality, "")
        bubble_bottom = self._draw_speech_bubble(surface, comment, x_offset, panel_width, bubble_top, avatar_center[0])

        return bubble_bottom + 16

    def _draw_speech_bubble(self, surface, text, x_offset, panel_width, top, tail_x):
        lines = self._wrap_text(text, self._commentary_font, panel_width - 28)
        line_height = settings.FONT_SIZE_COMMENTARY + 8
        bubble_height = line_height * len(lines) + 22
        bubble_rect = pygame.Rect(x_offset, top + 10, panel_width, bubble_height)

        pygame.draw.rect(surface, settings.COLOR_SPEECH_BUBBLE_BG, bubble_rect, border_radius=12)
        pygame.draw.rect(surface, settings.COLOR_SPEECH_BUBBLE_BORDER, bubble_rect, width=2, border_radius=12)

        tail_points = [
            (tail_x - 10, top + 10),
            (tail_x + 12, top + 10),
            (tail_x - 2, top - 2),
        ]
        pygame.draw.polygon(surface, settings.COLOR_SPEECH_BUBBLE_BG, tail_points)
        pygame.draw.polygon(surface, settings.COLOR_SPEECH_BUBBLE_BORDER, tail_points, width=2)
        pygame.draw.rect(surface, settings.COLOR_SPEECH_BUBBLE_BG, (tail_x - 8, top + 8, 20, 6))

        text_y = bubble_rect.top + 11
        for line in lines:
            line_surface = self._commentary_font.render(line, True, settings.COLOR_SPEECH_BUBBLE_TEXT)
            surface.blit(line_surface, (bubble_rect.left + 14, text_y))
            text_y += line_height

        return bubble_rect.bottom

    def _draw_status_badge(self, surface, controller, x_offset, panel_width, y):
        status_text = self._status_text(controller)
        badge_height = 34
        badge_rect = pygame.Rect(x_offset, y, panel_width, badge_height)

        if controller.is_game_over():
            bg = (90, 70, 30)
        elif controller.is_ai_thinking:
            bg = (50, 60, 80)
        else:
            bg = settings.COLOR_CARD_BACKGROUND

        pygame.draw.rect(surface, bg, badge_rect, border_radius=8)
        text_surface = self._status_font.render(status_text, True, settings.COLOR_PANEL_TEXT)
        text_rect = text_surface.get_rect(center=badge_rect.center)
        surface.blit(text_surface, text_rect)

        return badge_rect.bottom

    def _status_text(self, controller):
        if controller.is_game_over():
            return controller.get_result()
        if controller.is_ai_thinking:
            return "AI is thinking..."
        board = controller.game_state.get_board()
        turn_name = "White" if board.turn else "Black"
        check_suffix = " - in check" if controller.game_state.is_check() else ""
        return f"{turn_name} to move{check_suffix}"

    def _draw_buttons_card(self, surface, controller, x_offset, panel_width, y):
        button_width = (panel_width - 10) // 2
        button_height = 36
        spacing = 10

        card_top = y
        card_padding = 12

        rows = 2 if not controller.vs_ai else 4
        card_height = card_padding * 2 + rows * button_height + (rows - 1) * spacing

        card_rect = pygame.Rect(x_offset, card_top, panel_width, card_height)
        pygame.draw.rect(surface, settings.COLOR_CARD_BACKGROUND, card_rect, border_radius=10)
        pygame.draw.rect(surface, settings.COLOR_CARD_BORDER, card_rect, width=1, border_radius=10)

        bx = x_offset + card_padding
        by = card_top + card_padding

        self.undo_button_rect = pygame.Rect(bx, by, button_width, button_height)
        self.restart_button_rect = pygame.Rect(bx + button_width + spacing, by, button_width, button_height)
        self._draw_button(surface, self.undo_button_rect, "Undo")
        self._draw_button(surface, self.restart_button_rect, "New Game")
        by += button_height + spacing

        self.vs_ai_button_rect = pygame.Rect(bx, by, button_width, button_height)
        self.vs_human_button_rect = pygame.Rect(bx + button_width + spacing, by, button_width, button_height)
        self._draw_button(surface, self.vs_ai_button_rect, "vs AI", active=controller.vs_ai)
        self._draw_button(surface, self.vs_human_button_rect, "vs Human", active=not controller.vs_ai)
        by += button_height + spacing

        row_width = button_width * 2 + spacing

        if controller.vs_ai:
            self.difficulty_button_rect = pygame.Rect(bx, by, row_width, button_height)
            self._draw_button(surface, self.difficulty_button_rect, f"Difficulty: {controller.difficulty}")
            by += button_height + spacing

            self.personality_button_rect = pygame.Rect(bx, by, row_width, button_height)
            self._draw_button(surface, self.personality_button_rect, f"Personality: {controller.personality}")
        else:
            self.difficulty_button_rect = None
            self.personality_button_rect = None

        return card_rect.bottom

    def _draw_button(self, surface, rect, label, active=False):
        mouse_pos = pygame.mouse.get_pos()
        if active:
            color = settings.COLOR_BUTTON_ACTIVE
        elif rect.collidepoint(mouse_pos):
            color = settings.COLOR_BUTTON_HOVER
        else:
            color = settings.COLOR_BUTTON_BACKGROUND
        pygame.draw.rect(surface, color, rect, border_radius=6)
        if active:
            pygame.draw.rect(surface, settings.COLOR_BUTTON_ACTIVE_BORDER, rect, width=2, border_radius=6)
        text_surface = self._button_font.render(label, True, settings.COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _draw_move_history_card(self, surface, controller, x_offset, panel_width, y):
        max_y = settings.WINDOW_HEIGHT - 16
        card_rect = pygame.Rect(x_offset, y, panel_width, max_y - y)
        pygame.draw.rect(surface, settings.COLOR_CARD_BACKGROUND, card_rect, border_radius=10)
        pygame.draw.rect(surface, settings.COLOR_CARD_BORDER, card_rect, width=1, border_radius=10)

        inner_x = x_offset + 14
        inner_y = y + 12

        heading = self._text_font.render("Move History", True, settings.COLOR_PANEL_HEADING)
        surface.blit(heading, (inner_x, inner_y))
        inner_y += 28

        line_height = settings.FONT_SIZE_PANEL_TEXT + 6
        max_inner_y = card_rect.bottom - 12

        for move_number, white_san, black_san in controller.move_history_pairs():
            if inner_y > max_inner_y:
                break
            black_part = black_san if black_san else ""
            line = f"{move_number}. {white_san}  {black_part}"
            line_surface = self._text_font.render(line, True, settings.COLOR_PANEL_TEXT)
            surface.blit(line_surface, (inner_x, inner_y))
            inner_y += line_height
