"""
main.py

Entry point for KnightShift. Keeps startup logic to a minimum: create
the game screen, run it. All real logic lives in the domain, ai,
presentation, and controller packages.
"""

from presentation.game_screen import GameScreen


def main():
    screen = GameScreen()
    screen.run()


if __name__ == "__main__":
    main()
