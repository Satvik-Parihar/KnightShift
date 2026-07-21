"""
presentation/game_screen.py

Owns the Pygame window and the main game loop. For now (before the
controller and input handler exist), it holds a GameState directly and
simply renders the current position each frame. Once controller/game_controller.py
and presentation/input_handler.py exist, this class will delegate move
logic to them instead of touching GameState directly.
"""

import pygame

from config import settings
from domain.game_state import GameState
from presentation.board_renderer import BoardRenderer
from presentation.input_handler import InputHandler


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
        self._game_state = GameState()
        self._input_handler = InputHandler(self._game_state)

        self._running = False

    def run(self):
        """Start the main loop. Blocks until the window is closed."""
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
                self._input_handler.handle_click(pixel_x, pixel_y)

    def _draw_frame(self):
        self._window.fill(settings.COLOR_PANEL_BACKGROUND)
        self._renderer.draw_board(
            self._board_surface,
            self._game_state,
            selected_square=self._input_handler.selected_square,
            legal_move_targets=self._input_handler.legal_move_targets(),
            last_move=self._input_handler.last_move,
        )
        self._draw_side_panel_placeholder()
        pygame.display.flip()

    def _draw_side_panel_placeholder(self):
        font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PANEL_HEADING)
        text = font.render("KnightShift", True, settings.COLOR_PANEL_HEADING)
        self._window.blit(text, (settings.BOARD_PIXELS + 20, 20))
