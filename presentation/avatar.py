import math

import pygame
import pygame.gfxdraw

from config import settings

SUPERSAMPLE = 4


def _aa_circle(surface, center, radius, color):
    x, y = int(center[0]), int(center[1])
    pygame.gfxdraw.filled_circle(surface, x, y, radius, color)
    pygame.gfxdraw.aacircle(surface, x, y, radius, color)


def _thick_arc(surface, color, center, radius_x, radius_y, start_angle, end_angle, width, points=48):
    cx, cy = center
    outer = []
    inner = []
    for i in range(points + 1):
        t = start_angle + (end_angle - start_angle) * i / points
        ox = cx + (radius_x + width / 2) * math.cos(t)
        oy = cy + (radius_y + width / 2) * math.sin(t)
        ix = cx + (radius_x - width / 2) * math.cos(t)
        iy = cy + (radius_y - width / 2) * math.sin(t)
        outer.append((ox, oy))
        inner.append((ix, iy))
    polygon = outer + inner[::-1]
    pygame.gfxdraw.filled_polygon(surface, polygon, color)
    pygame.gfxdraw.aapolygon(surface, polygon, color)


def _draw_highlight(surface, cx, cy, r):
    highlight_r = int(r * 0.55)
    hx = cx - r * 0.3
    hy = cy - r * 0.35
    pygame.gfxdraw.filled_circle(surface, int(hx), int(hy), highlight_r, (255, 255, 255, 55))
    pygame.gfxdraw.aacircle(surface, int(hx), int(hy), highlight_r, (255, 255, 255, 55))

    shade_r = int(r * 0.7)
    sx = cx + r * 0.35
    sy = cy + r * 0.4
    pygame.gfxdraw.filled_circle(surface, int(sx), int(sy), shade_r, (0, 0, 0, 25))
    pygame.gfxdraw.aacircle(surface, int(sx), int(sy), shade_r, (0, 0, 0, 25))


def _draw_crown(surface, cx, cy, r):
    band_half_w = r * 0.62
    band_bottom_y = cy - r * 0.62
    band_top_y = cy - r * 0.8
    tip_y = cy - r * 1.18
    center_tip_y = cy - r * 1.28
    valley_y = cy - r * 0.88

    points = [
        (cx - band_half_w, band_bottom_y),
        (cx - band_half_w, band_top_y),
        (cx - band_half_w * 0.6, tip_y),
        (cx - band_half_w * 0.25, valley_y),
        (cx, center_tip_y),
        (cx + band_half_w * 0.25, valley_y),
        (cx + band_half_w * 0.6, tip_y),
        (cx + band_half_w, band_top_y),
        (cx + band_half_w, band_bottom_y),
    ]

    gold = (224, 184, 60)
    outline = (120, 90, 20)
    pygame.gfxdraw.filled_polygon(surface, points, gold)
    pygame.gfxdraw.aapolygon(surface, points, outline)

    jewel_positions = [
        (cx - band_half_w * 0.6, tip_y),
        (cx, center_tip_y),
        (cx + band_half_w * 0.6, tip_y),
    ]
    jewel_radius = max(2, int(r * 0.07))
    for jx, jy in jewel_positions:
        pygame.gfxdraw.filled_circle(surface, int(jx), int(jy), jewel_radius, (190, 40, 55))
        pygame.gfxdraw.aacircle(surface, int(jx), int(jy), jewel_radius, (140, 20, 35))


def draw_avatar(surface, center, radius, personality):
    scaled_radius = radius * SUPERSAMPLE
    size = scaled_radius * 3
    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    scaled_center = (size // 2, int(size * 0.6))

    color = settings.AVATAR_COLORS.get(personality, settings.AVATAR_COLORS["Coach"])
    _aa_circle(temp, scaled_center, scaled_radius, color)
    _aa_circle(temp, scaled_center, scaled_radius - 1, color)

    cx, cy = scaled_center
    r = scaled_radius

    _draw_highlight(temp, cx, cy, r)

    ring_color = (255, 255, 255)
    for offset in range(3 * SUPERSAMPLE // 2):
        pygame.gfxdraw.aacircle(temp, cx, cy, r - offset, ring_color)

    if personality == "Coach":
        _draw_coach_face(temp, cx, cy, r)
    elif personality == "Competitive":
        _draw_competitive_face(temp, cx, cy, r)
    elif personality == "Funny":
        _draw_funny_face(temp, cx, cy, r)
    else:
        _draw_coach_face(temp, cx, cy, r)

    _draw_crown(temp, cx, cy, r)

    final_size = temp.get_width() // SUPERSAMPLE
    downscaled = pygame.transform.smoothscale(temp, (final_size, final_size))
    dest_rect = downscaled.get_rect()
    dest_rect.centerx = int(center[0])
    dest_rect.centery = int(center[1]) - int(radius * 0.3)
    surface.blit(downscaled, dest_rect)


def _draw_coach_face(surface, cx, cy, r):
    eye_offset_x = r * 0.35
    eye_offset_y = r * 0.15
    eye_radius = max(2, int(r * 0.09))
    dark = (30, 30, 30)

    _aa_circle(surface, (cx - eye_offset_x, cy - eye_offset_y), eye_radius, dark)
    _aa_circle(surface, (cx + eye_offset_x, cy - eye_offset_y), eye_radius, dark)

    _thick_arc(
        surface, dark, (cx, cy + r * 0.1),
        r * 0.45, r * 0.35, 0.5, 2.65, width=max(2, int(r * 0.09))
    )


def _draw_competitive_face(surface, cx, cy, r):
    eye_offset_x = r * 0.35
    eye_offset_y = r * 0.12
    dark = (30, 30, 30)
    brow_width = max(2, int(r * 0.07))

    brow_half_w = r * 0.16
    _thick_arc(
        surface, dark, (cx - eye_offset_x, cy - eye_offset_y - r * 0.06),
        brow_half_w, brow_half_w * 0.4, 3.3, 6.2, width=brow_width, points=12
    )
    _thick_arc(
        surface, dark, (cx + eye_offset_x, cy - eye_offset_y - r * 0.06),
        brow_half_w, brow_half_w * 0.4, -0.2, 2.7, width=brow_width, points=12
    )

    eye_radius = max(2, int(r * 0.07))
    _aa_circle(surface, (cx - eye_offset_x, cy), eye_radius, dark)
    _aa_circle(surface, (cx + eye_offset_x, cy), eye_radius, dark)

    _thick_arc(
        surface, dark, (cx, cy + r * 0.28),
        r * 0.35, r * 0.18, 0.4, 2.75, width=max(2, int(r * 0.08))
    )


def _draw_funny_face(surface, cx, cy, r):
    eye_offset_x = r * 0.33
    eye_offset_y = r * 0.15
    eye_radius = max(2, int(r * 0.1))
    dark = (30, 30, 30)

    _aa_circle(surface, (cx - eye_offset_x, cy - eye_offset_y), eye_radius, dark)

    _thick_arc(
        surface, dark, (cx + eye_offset_x, cy - eye_offset_y),
        eye_radius * 1.3, eye_radius * 1.3, 3.5, 6.0, width=max(2, int(r * 0.05))
    )

    _thick_arc(
        surface, dark, (cx, cy + r * 0.05),
        r * 0.5, r * 0.4, 0.35, 2.8, width=max(2, int(r * 0.1))
    )
