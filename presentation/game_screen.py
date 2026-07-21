"""
presentation/game_screen.py

Owns the Pygame window and the main game loop. Delegates all game
logic to GameController; only handles input events, rendering, and
timing.
"""

import pygame

from config import settings
from controller.game_controller import GameController
from presentation.board_renderer import BoardRenderer
from presentation.ui_panel import UIPanel


class GameScreen:
    """Creates the game window and runs the main render loop."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("KnightShift")

        self._window = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        )
        self._clock = pygame.time.Clock()

        self._board_surface = self._window.subsurface(
            pygame.Rect(0, 0, settings.BOARD_PIXELS, settings.BOARD_PIXELS)
        )

        self._renderer = BoardRenderer()
        self._ui_panel = UIPanel()
        self._controller = GameController()

        self._running = False

    def run(self):
        self._running = True
        while self._running:
            self._handle_events()
            self._draw_frame()
            self._clock.tick(settings.FPS)

        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pixel_x, pixel_y = event.pos
                self._controller.handle_click(pixel_x, pixel_y)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    self._controller.undo()
                elif event.key == pygame.K_r:
                    self._controller.restart()

    def _draw_frame(self):
        self._window.fill(settings.COLOR_PANEL_BACKGROUND)

        self._renderer.draw_board(
            self._board_surface,
            self._controller.game_state,
            selected_square=self._controller.selected_square,
            legal_move_targets=self._controller.legal_move_targets(),
            last_move=self._controller.last_move,
        )

        self._ui_panel.draw(self._window, self._controller)

        pygame.display.flip()
