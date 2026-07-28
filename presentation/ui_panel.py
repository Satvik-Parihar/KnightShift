import os
import math

import pygame
import pygame.gfxdraw

from config import settings
from config.settings import DIFFICULTY_PRESETS, AI_PERSONALITIES
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
        self._section_font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_SECTION_LABEL, bold=True)
        self._segment_font = pygame.font.SysFont(settings.FONT_NAME, 12)

        self._king_icons = self._load_king_icons()

        self.undo_button_rect = None
        self.restart_button_rect = None
        self.vs_ai_button_rect = None
        self.vs_human_button_rect = None
        self.difficulty_button_rects = {}
        self.personality_button_rects = {}
        self.play_white_button_rect = None
        self.play_black_button_rect = None
        self.play_random_button_rect = None

    def _load_king_icons(self):
        icons = {}
        icon_size = 26
        for key, filename in (("white", "wK.png"), ("black", "bK.png")):
            path = os.path.join(settings.PIECES_ASSET_PATH, filename)
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                icons[key] = pygame.transform.smoothscale(raw, (icon_size, icon_size))
        return icons

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
        y += 10

        y = self._draw_buttons_card(surface, controller, x_offset, panel_width, y)
        y += 12

        self._draw_move_history_card(surface, controller, x_offset, panel_width, y)

    def _draw_avatar_section(self, surface, controller, x_offset, panel_width, y):
        avatar_radius = 22
        avatar_center = (x_offset + avatar_radius, y + avatar_radius)
        draw_avatar(surface, avatar_center, avatar_radius, controller.personality)

        name_surface = self._text_font.render(controller.personality, True, settings.COLOR_PANEL_HEADING)
        surface.blit(name_surface, (x_offset + avatar_radius * 2 + 12, y + avatar_radius - 9))

        bubble_top = y + avatar_radius * 2 + 10
        comment = controller.latest_comment or IDLE_LINES.get(controller.personality, "")
        bubble_bottom = self._draw_speech_bubble(surface, comment, x_offset, panel_width, bubble_top, avatar_center[0])

        return bubble_bottom + 12

    def _draw_speech_bubble(self, surface, text, x_offset, panel_width, top, tail_x):
        max_lines = 2
        lines = self._wrap_text(text, self._commentary_font, panel_width - 28)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            last = lines[-1]
            while self._commentary_font.size(last + "...")[0] > panel_width - 28 and len(last) > 1:
                last = last[:-1]
            lines[-1] = last + "..."

        line_height = settings.FONT_SIZE_COMMENTARY + 6
        bubble_height = line_height * len(lines) + 16
        bubble_rect = pygame.Rect(x_offset, top + 8, panel_width, bubble_height)

        pygame.draw.rect(surface, settings.COLOR_SPEECH_BUBBLE_BG, bubble_rect, border_radius=10)
        pygame.draw.rect(surface, settings.COLOR_SPEECH_BUBBLE_BORDER, bubble_rect, width=2, border_radius=10)

        tail_points = [
            (tail_x - 8, top + 8),
            (tail_x + 10, top + 8),
            (tail_x - 2, top - 2),
        ]
        pygame.draw.polygon(surface, settings.COLOR_SPEECH_BUBBLE_BG, tail_points)
        pygame.draw.polygon(surface, settings.COLOR_SPEECH_BUBBLE_BORDER, tail_points, width=2)
        pygame.draw.rect(surface, settings.COLOR_SPEECH_BUBBLE_BG, (tail_x - 6, top + 6, 16, 5))

        text_y = bubble_rect.top + 11
        for line in lines:
            line_surface = self._commentary_font.render(line, True, settings.COLOR_SPEECH_BUBBLE_TEXT)
            surface.blit(line_surface, (bubble_rect.left + 14, text_y))
            text_y += line_height

        return bubble_rect.bottom

    def _draw_status_badge(self, surface, controller, x_offset, panel_width, y):
        status_text = self._status_text(controller)
        badge_height = 30
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

    def _section_label(self, surface, text, x, y):
        label = self._section_font.render(text.upper(), True, settings.COLOR_SECTION_LABEL)
        surface.blit(label, (x, y))
        return y + label.get_height() + 4

    def _draw_buttons_card(self, surface, controller, x_offset, panel_width, y):
        button_height = 30
        spacing = 6
        card_padding = 10
        section_gap = 4
        label_block = self._section_font.get_height() + 3

        button_width = (panel_width - card_padding * 2 - spacing) // 2
        row_width = panel_width - card_padding * 2

        section_count = 2 if not controller.vs_ai else 5
        card_height = card_padding * 2 + section_count * (label_block + button_height) \
            + (section_count - 1) * section_gap

        card_rect = pygame.Rect(x_offset, y, panel_width, card_height)
        pygame.draw.rect(surface, settings.COLOR_CARD_BACKGROUND, card_rect, border_radius=10)
        pygame.draw.rect(surface, settings.COLOR_CARD_BORDER, card_rect, width=1, border_radius=10)

        bx = x_offset + card_padding
        by = y + card_padding

        by = self._section_label(surface, "Game", bx, by)
        self.undo_button_rect = pygame.Rect(bx, by, button_width, button_height)
        self.restart_button_rect = pygame.Rect(bx + button_width + spacing, by, button_width, button_height)
        self._draw_button(surface, self.undo_button_rect, "Undo")
        self._draw_button(surface, self.restart_button_rect, "New Game")
        by += button_height + section_gap

        by = self._section_label(surface, "Mode", bx, by)
        self.vs_ai_button_rect = pygame.Rect(bx, by, button_width, button_height)
        self.vs_human_button_rect = pygame.Rect(bx + button_width + spacing, by, button_width, button_height)
        self._draw_button(surface, self.vs_ai_button_rect, "vs AI", active=controller.vs_ai)
        self._draw_button(surface, self.vs_human_button_rect, "vs Human", active=not controller.vs_ai)
        by += button_height + section_gap

        if controller.vs_ai:
            by = self._section_label(surface, "Play as", bx, by)
            triple_width = (row_width - spacing * 2) // 3

            self.play_white_button_rect = pygame.Rect(bx, by, triple_width, button_height)
            self.play_black_button_rect = pygame.Rect(bx + triple_width + spacing, by, triple_width, button_height)
            self.play_random_button_rect = pygame.Rect(
                bx + (triple_width + spacing) * 2, by, triple_width, button_height
            )

            self._draw_color_button(surface, self.play_white_button_rect, "white",
                                     active=controller.player_color_choice == "White")
            self._draw_color_button(surface, self.play_black_button_rect, "black",
                                     active=controller.player_color_choice == "Black")
            self._draw_random_button(surface, self.play_random_button_rect,
                                      active=controller.player_color_choice == "Random")
            by += button_height + section_gap

            by = self._section_label(surface, "Difficulty", bx, by)
            difficulty_names = list(DIFFICULTY_PRESETS.keys())
            self.difficulty_button_rects = self._draw_segmented_row(
                surface, bx, by, row_width, button_height, spacing,
                difficulty_names, controller.difficulty
            )
            by += button_height + section_gap

            by = self._section_label(surface, "Personality", bx, by)
            self.personality_button_rects = self._draw_segmented_row(
                surface, bx, by, row_width, button_height, spacing,
                AI_PERSONALITIES, controller.personality
            )
        else:
            self.difficulty_button_rects = {}
            self.personality_button_rects = {}
            self.play_white_button_rect = None
            self.play_black_button_rect = None
            self.play_random_button_rect = None

        return card_rect.bottom

    def _draw_segmented_row(self, surface, bx, by, row_width, button_height, spacing, options, active_value):
        count = len(options)
        segment_width = (row_width - spacing * (count - 1)) // count
        rects = {}
        x = bx
        for option in options:
            rect = pygame.Rect(x, by, segment_width, button_height)
            rects[option] = rect
            self._draw_segment_button(surface, rect, option, active=(option == active_value))
            x += segment_width + spacing
        return rects

    def _draw_segment_button(self, surface, rect, label, active=False):
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
        text_surface = self._segment_font.render(label, True, settings.COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

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

    def _draw_color_button(self, surface, rect, color_key, active=False):
        mouse_pos = pygame.mouse.get_pos()
        if active:
            bg = settings.COLOR_BUTTON_ACTIVE
        elif rect.collidepoint(mouse_pos):
            bg = settings.COLOR_BUTTON_HOVER
        else:
            bg = settings.COLOR_BUTTON_BACKGROUND
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        if active:
            pygame.draw.rect(surface, settings.COLOR_BUTTON_ACTIVE_BORDER, rect, width=2, border_radius=6)

        icon = self._king_icons.get(color_key)
        if icon is not None:
            icon_rect = icon.get_rect(center=rect.center)
            surface.blit(icon, icon_rect)

    def _draw_random_button(self, surface, rect, active=False):
        mouse_pos = pygame.mouse.get_pos()
        if active:
            bg = settings.COLOR_BUTTON_ACTIVE
        elif rect.collidepoint(mouse_pos):
            bg = settings.COLOR_BUTTON_HOVER
        else:
            bg = settings.COLOR_BUTTON_BACKGROUND
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        if active:
            pygame.draw.rect(surface, settings.COLOR_BUTTON_ACTIVE_BORDER, rect, width=2, border_radius=6)

        radius = 12
        cx, cy = rect.center

        pygame.gfxdraw.filled_circle(surface, cx, cy, radius, (255, 255, 255))
        pygame.gfxdraw.aacircle(surface, cx, cy, radius, (255, 255, 255))

        half_points = []
        steps = 20
        for i in range(steps + 1):
            angle = -math.pi / 2 + math.pi * i / steps
            half_points.append((cx + radius * math.sin(angle), cy - radius * math.cos(angle)))
        pygame.gfxdraw.filled_polygon(surface, half_points, (30, 30, 30))
        pygame.gfxdraw.aapolygon(surface, half_points, (30, 30, 30))

        pygame.gfxdraw.aacircle(surface, cx, cy, radius, (200, 200, 200))

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
