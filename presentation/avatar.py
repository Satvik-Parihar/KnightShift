import os

import pygame
import pygame.gfxdraw

from config import settings

_AVATAR_FILES = {
    "Coach": "coach.png",
    "Competitive": "competitive.png",
    "Funny": "funny.png",
}

_avatar_cache = {}


def _load_avatar(personality, diameter):
    cache_key = (personality, diameter)
    if cache_key in _avatar_cache:
        return _avatar_cache[cache_key]

    filename = _AVATAR_FILES.get(personality, _AVATAR_FILES["Coach"])
    path = os.path.join(settings.AVATARS_ASSET_PATH, filename)

    if not os.path.exists(path):
        _avatar_cache[cache_key] = None
        return None

    raw = pygame.image.load(path).convert_alpha()
    scaled = pygame.transform.smoothscale(raw, (diameter, diameter))
    _avatar_cache[cache_key] = scaled
    return scaled


def draw_avatar(surface, center, radius, personality):
    diameter = radius * 2
    image = _load_avatar(personality, diameter)

    cx, cy = int(center[0]), int(center[1])
    bg_color = settings.AVATAR_COLORS.get(personality, settings.AVATAR_COLORS["Coach"])

    pygame.gfxdraw.filled_circle(surface, cx, cy, radius + 3, bg_color)
    pygame.gfxdraw.aacircle(surface, cx, cy, radius + 3, bg_color)
    pygame.gfxdraw.aacircle(surface, cx, cy, radius + 3, (255, 255, 255))
    pygame.gfxdraw.aacircle(surface, cx, cy, radius + 2, (255, 255, 255))

    if image is not None:
        rect = image.get_rect(center=(cx, cy))
        surface.blit(image, rect)

