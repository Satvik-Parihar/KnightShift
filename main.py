import sys

from presentation.game_screen import GameScreen


def _fix_windows_dpi_scaling():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    _fix_windows_dpi_scaling()
    screen = GameScreen()
    screen.run()


if __name__ == "__main__":
    main()
