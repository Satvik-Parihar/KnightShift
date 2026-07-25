import pygame

from config import settings


def draw_avatar(surface, center, radius, personality):
    color = settings.AVATAR_COLORS.get(personality, settings.AVATAR_COLORS["Coach"])
    cx, cy = center

    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, (255, 255, 255), center, radius, width=3)

    if personality == "Coach":
        _draw_coach_face(surface, cx, cy, radius)
    elif personality == "Competitive":
        _draw_competitive_face(surface, cx, cy, radius)
    elif personality == "Funny":
        _draw_funny_face(surface, cx, cy, radius)
    else:
        _draw_coach_face(surface, cx, cy, radius)


def _draw_coach_face(surface, cx, cy, r):
    eye_offset_x = r * 0.35
    eye_offset_y = r * 0.15
    eye_radius = max(2, int(r * 0.09))
    pygame.draw.circle(surface, (30, 30, 30), (int(cx - eye_offset_x), int(cy - eye_offset_y)), eye_radius)
    pygame.draw.circle(surface, (30, 30, 30), (int(cx + eye_offset_x), int(cy - eye_offset_y)), eye_radius)

    mouth_rect = pygame.Rect(0, 0, r * 0.9, r * 0.5)
    mouth_rect.center = (cx, int(cy + r * 0.25))
    pygame.draw.arc(surface, (30, 30, 30), mouth_rect, 3.6, 5.9, width=max(2, int(r * 0.06)))


def _draw_competitive_face(surface, cx, cy, r):
    eye_offset_x = r * 0.35
    eye_offset_y = r * 0.12
    eye_w, eye_h = int(r * 0.22), int(r * 0.08)

    pygame.draw.line(surface, (30, 30, 30),
                      (cx - eye_offset_x - eye_w // 2, cy - eye_offset_y - eye_h),
                      (cx - eye_offset_x + eye_w // 2, cy - eye_offset_y), width=max(2, int(r * 0.06)))
    pygame.draw.line(surface, (30, 30, 30),
                      (cx + eye_offset_x + eye_w // 2, cy - eye_offset_y - eye_h),
                      (cx + eye_offset_x - eye_w // 2, cy - eye_offset_y), width=max(2, int(r * 0.06)))

    eye_radius = max(2, int(r * 0.07))
    pygame.draw.circle(surface, (30, 30, 30), (int(cx - eye_offset_x), int(cy)), eye_radius)
    pygame.draw.circle(surface, (30, 30, 30), (int(cx + eye_offset_x), int(cy)), eye_radius)

    mouth_rect = pygame.Rect(0, 0, r * 0.7, r * 0.35)
    mouth_rect.center = (cx, int(cy + r * 0.4))
    pygame.draw.arc(surface, (30, 30, 30), mouth_rect, 3.5, 6.0, width=max(2, int(r * 0.06)))


def _draw_funny_face(surface, cx, cy, r):
    eye_offset_x = r * 0.33
    eye_offset_y = r * 0.15
    eye_radius = max(2, int(r * 0.1))
    pygame.draw.circle(surface, (30, 30, 30), (int(cx - eye_offset_x), int(cy - eye_offset_y)), eye_radius)

    wink_y = int(cy - eye_offset_y)
    pygame.draw.arc(
        surface, (30, 30, 30),
        pygame.Rect(int(cx + eye_offset_x - eye_radius), wink_y - eye_radius // 2, eye_radius * 2, eye_radius * 2),
        3.4, 6.0, width=max(2, int(r * 0.05))
    )

    mouth_rect = pygame.Rect(0, 0, r * 1.0, r * 0.7)
    mouth_rect.center = (cx, int(cy + r * 0.2))
    pygame.draw.arc(surface, (30, 30, 30), mouth_rect, 3.5, 6.0, width=max(2, int(r * 0.07)))
