"""
config/settings.py

Central location for all constants used across the project: window
dimensions, colors, board geometry, and difficulty presets. Nothing in
this file should contain logic — only values. If a number is used in more
than one place (or might need tuning later), it belongs here, not
hardcoded inline in the module that uses it.
"""

# ---------------------------------------------------------------------------
# Window / board geometry
# ---------------------------------------------------------------------------

BOARD_SIZE = 8                     # 8x8 chess board
SQUARE_SIZE = 80                   # pixels per square
BOARD_PIXELS = BOARD_SIZE * SQUARE_SIZE   # 640

SIDE_PANEL_WIDTH = 300              # move history / commentary / controls
WINDOW_WIDTH = BOARD_PIXELS + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_PIXELS

FPS = 60

# ---------------------------------------------------------------------------
# Colors (RGB)
# ---------------------------------------------------------------------------

COLOR_LIGHT_SQUARE = (238, 238, 210)
COLOR_DARK_SQUARE = (118, 150, 86)

COLOR_HIGHLIGHT_SELECTED = (246, 246, 105)   # selected piece's square
COLOR_HIGHLIGHT_LEGAL_MOVE = (106, 168, 79)  # dot/marker on legal destination squares
COLOR_HIGHLIGHT_LAST_MOVE = (255, 215, 0)    # last move played, both squares
COLOR_HIGHLIGHT_CHECK = (220, 60, 60)        # king's square when in check

COLOR_PANEL_BACKGROUND = (30, 30, 30)
COLOR_PANEL_TEXT = (230, 230, 230)
COLOR_PANEL_HEADING = (255, 255, 255)

COLOR_WHITE_PIECE_TEXT = (255, 255, 255)     # fallback if using text glyphs instead of images
COLOR_BLACK_PIECE_TEXT = (0, 0, 0)

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

FONT_NAME = "arial"
FONT_SIZE_PANEL_TEXT = 18
FONT_SIZE_PANEL_HEADING = 22
FONT_SIZE_COMMENTARY = 16

# ---------------------------------------------------------------------------
# Asset paths
# ---------------------------------------------------------------------------

PIECES_ASSET_PATH = "assets/pieces"
SOUNDS_ASSET_PATH = "assets/sounds"

# ---------------------------------------------------------------------------
# AI difficulty presets
# ---------------------------------------------------------------------------
# Maps a difficulty name to Minimax search depth. Higher depth = stronger
# play but slower move generation. Tune these once the AI is implemented
# and we can measure actual move-generation time per depth.

DIFFICULTY_PRESETS = {
    "Easy": {"depth": 1},
    "Medium": {"depth": 2},
    "Hard": {"depth": 3},
    "Expert": {"depth": 4},
}

DEFAULT_DIFFICULTY = "Medium"

# ---------------------------------------------------------------------------
# AI personalities
# ---------------------------------------------------------------------------

AI_PERSONALITIES = ["Coach", "Competitive", "Funny"]

DEFAULT_PERSONALITY = "Coach"
