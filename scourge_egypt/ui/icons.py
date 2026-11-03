"""
Sistema de iconos procedurales para The Scourge of Egypt.
Todos los iconos se dibujan con pygame.draw sin recursos externos.
Cada función recibe: surface, center (x,y), size (radio/ancho base), color.
"""
from __future__ import annotations
import pygame
import math
from typing import Tuple

Color = Tuple[int, int, int]


# ─────────────────────────────────────────────────────────────
#  Utilidades internas
# ─────────────────────────────────────────────────────────────

def _poly(surface: pygame.Surface, color: Color, points, width: int = 0):
    if len(points) >= 3:
        pygame.draw.polygon(surface, color, points, width)


def _circle(surface: pygame.Surface, color: Color, center, radius: int, width: int = 0):
    if radius > 0:
        pygame.draw.circle(surface, color, center, radius, width)


def _line(surface: pygame.Surface, color: Color, p1, p2, width: int = 1):
    pygame.draw.line(surface, color, p1, p2, width)


def _rect(surface: pygame.Surface, color: Color, rect: pygame.Rect, border_radius: int = 0, width: int = 0):
    pygame.draw.rect(surface, color, rect, width, border_radius=border_radius)


# ─────────────────────────────────────────────────────────────
#  LLAMA  –  Ira de Dios
# ─────────────────────────────────────────────────────────────

def draw_icon_flame(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Llama estilizada: Ira de Dios."""
    cx, cy = center
    s = size
    # Llama exterior
    pts_outer = [
        (cx, cy - s),
        (cx + s * 0.35, cy - s * 0.45),
        (cx + s * 0.55, cy - s * 0.7),
        (cx + s * 0.4, cy - s * 0.3),
        (cx + s * 0.6, cy + s * 0.1),
        (cx + s * 0.3, cy + s * 0.5),
        (cx, cy + s * 0.5),
        (cx - s * 0.3, cy + s * 0.5),
        (cx - s * 0.6, cy + s * 0.1),
        (cx - s * 0.4, cy - s * 0.3),
        (cx - s * 0.55, cy - s * 0.7),
        (cx - s * 0.35, cy - s * 0.45),
    ]
    pts_outer = [(int(x), int(y)) for x, y in pts_outer]
    _poly(surface, color, pts_outer)
    # Núcleo interior más brillante
    inner = tuple(min(255, c + 80) for c in color)
    pts_inner = [
        (cx, cy - s * 0.4),
        (cx + s * 0.2, cy),
        (cx, cy + s * 0.35),
        (cx - s * 0.2, cy),
    ]
    pts_inner = [(int(x), int(y)) for x, y in pts_inner]
    _poly(surface, inner, pts_inner)


# ─────────────────────────────────────────────────────────────
#  TRIGO / ESPIGA  –  Cosechas / Cosechar
# ─────────────────────────────────────────────────────────────

def draw_icon_wheat(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Espiga de trigo: Cosechas / Cosechar."""
    cx, cy = center
    s = size
    # Tallo central
    _line(surface, color, (cx, cy + s * 0.55), (cx, cy - s * 0.55), max(1, s // 6))
    # Granos alternados
    for i, (dy_ratio, side) in enumerate([
        (-0.4, 1), (-0.4, -1),
        (-0.15, 1), (-0.15, -1),
        (0.1, 1), (0.1, -1),
    ]):
        gx = int(cx + side * s * 0.28)
        gy = int(cy + dy_ratio * s)
        _circle(surface, color, (gx, gy), max(2, s // 5))
    # Punta superior
    pts_top = [
        (cx, int(cy - s * 0.55)),
        (int(cx - s * 0.12), int(cy - s * 0.35)),
        (int(cx + s * 0.12), int(cy - s * 0.35)),
    ]
    _poly(surface, color, pts_top)


# ─────────────────────────────────────────────────────────────
#  VACA  –  Ganado / Ganadería
# ─────────────────────────────────────────────────────────────

def draw_icon_cow(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Cabeza de vaca estilizada: Ganado / Ganadería."""
    cx, cy = center
    s = size
    # Cabeza (elipse)
    head_rect = pygame.Rect(int(cx - s * 0.5), int(cy - s * 0.35), int(s), int(s * 0.7))
    _rect(surface, color, head_rect, border_radius=int(s * 0.3))
    # Hocico
    snout_rect = pygame.Rect(int(cx - s * 0.3), int(cy + s * 0.1), int(s * 0.6), int(s * 0.35))
    dark = tuple(max(0, c - 50) for c in color)
    _rect(surface, dark, snout_rect, border_radius=int(s * 0.15))
    # Ojos
    _circle(surface, (20, 20, 20), (int(cx - s * 0.22), int(cy - s * 0.08)), max(2, s // 7))
    _circle(surface, (20, 20, 20), (int(cx + s * 0.22), int(cy - s * 0.08)), max(2, s // 7))
    # Cuernos
    horn_col = tuple(min(255, c + 60) for c in color)
    _line(surface, horn_col,
          (int(cx - s * 0.35), int(cy - s * 0.35)),
          (int(cx - s * 0.5), int(cy - s * 0.7)), max(1, s // 6))
    _line(surface, horn_col,
          (int(cx + s * 0.35), int(cy - s * 0.35)),
          (int(cx + s * 0.5), int(cy - s * 0.7)), max(1, s // 6))


# ─────────────────────────────────────────────────────────────
#  CASA / PIRÁMIDE  –  Viviendas / Reconstrucción
# ─────────────────────────────────────────────────────────────

def draw_icon_house(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Casa estilo pirámide: Viviendas / Reconstrucción."""
    cx, cy = center
    s = size
    # Base
    base = pygame.Rect(int(cx - s * 0.45), int(cy - s * 0.05), int(s * 0.9), int(s * 0.55))
    _rect(surface, color, base, border_radius=2)
    # Tejado (triángulo)
    roof_pts = [
        (int(cx), int(cy - s * 0.55)),
        (int(cx - s * 0.52), int(cy - s * 0.05)),
        (int(cx + s * 0.52), int(cy - s * 0.05)),
    ]
    bright = tuple(min(255, c + 50) for c in color)
    _poly(surface, bright, roof_pts)
    # Puerta
    door = pygame.Rect(int(cx - s * 0.12), int(cy + s * 0.12), int(s * 0.24), int(s * 0.38))
    dark = tuple(max(0, c - 80) for c in color)
    _rect(surface, dark, door, border_radius=int(s * 0.06))


# ─────────────────────────────────────────────────────────────
#  MANOS EN ORACIÓN  –  Fe / Rezar / Rendir Pleitesía
# ─────────────────────────────────────────────────────────────

def draw_icon_pray(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Símbolo de oración (palmas unidas): Fe / Rezar."""
    cx, cy = center
    s = size
    # Mano izquierda
    l_pts = [
        (int(cx - s * 0.05), int(cy - s * 0.5)),
        (int(cx - s * 0.35), int(cy - s * 0.1)),
        (int(cx - s * 0.35), int(cy + s * 0.5)),
        (int(cx - s * 0.05), int(cy + s * 0.2)),
    ]
    _poly(surface, color, l_pts)
    # Mano derecha
    r_pts = [
        (int(cx + s * 0.05), int(cy - s * 0.5)),
        (int(cx + s * 0.35), int(cy - s * 0.1)),
        (int(cx + s * 0.35), int(cy + s * 0.5)),
        (int(cx + s * 0.05), int(cy + s * 0.2)),
    ]
    _poly(surface, color, r_pts)
    # Rayos de luz
    bright = tuple(min(255, c + 100) for c in color)
    for angle in range(60, 121, 20):
        rad = math.radians(angle)
        ex = int(cx + math.cos(rad) * s * 0.7)
        ey = int(cy - math.sin(rad) * s * 0.7)
        _line(surface, bright, (cx, int(cy - s * 0.3)), (ex, ey), max(1, s // 8))


# ─────────────────────────────────────────────────────────────
#  PERSONA / ACÓLITO  –  Renacimiento / Acólitos
# ─────────────────────────────────────────────────────────────

def draw_icon_person(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Figura humana estilizada: Acólito / Renacimiento."""
    cx, cy = center
    s = size
    head_r = max(3, s // 4)
    # Cabeza
    _circle(surface, color, (cx, int(cy - s * 0.45)), head_r)
    # Cuerpo
    body_top = int(cy - s * 0.28)
    body_bot = int(cy + s * 0.15)
    _line(surface, color, (cx, body_top), (cx, body_bot), max(1, s // 5))
    # Brazos
    _line(surface, color,
          (int(cx - s * 0.3), int(cy - s * 0.05)),
          (int(cx + s * 0.3), int(cy - s * 0.05)), max(1, s // 6))
    # Piernas
    _line(surface, color,
          (cx, body_bot),
          (int(cx - s * 0.25), int(cy + s * 0.5)), max(1, s // 6))
    _line(surface, color,
          (cx, body_bot),
          (int(cx + s * 0.25), int(cy + s * 0.5)), max(1, s // 6))


# ─────────────────────────────────────────────────────────────
#  DADO  –  Dioses Favorables
# ─────────────────────────────────────────────────────────────

def draw_icon_dice(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Dado de 6 caras: Dioses Favorables."""
    cx, cy = center
    s = size
    half = int(s * 0.5)
    # Cuerpo del dado
    dice_rect = pygame.Rect(cx - half, cy - half, half * 2, half * 2)
    dark = tuple(max(0, c - 60) for c in color)
    _rect(surface, dark, dice_rect, border_radius=max(2, s // 6))
    _rect(surface, color, dice_rect, border_radius=max(2, s // 6), width=max(1, s // 8))
    # Puntos del "6" (2 columnas x 3 filas)
    dot_r = max(1, s // 9)
    dot_col = color
    for row in range(3):
        for col in range(2):
            dx = int(cx - s * 0.22 + col * s * 0.44)
            dy = int(cy - s * 0.28 + row * s * 0.28)
            _circle(surface, dot_col, (dx, dy), dot_r)


# ─────────────────────────────────────────────────────────────
#  AGUA / OLAS  –  Regadíos
# ─────────────────────────────────────────────────────────────

def draw_icon_water(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Olas de agua: Regadíos."""
    cx, cy = center
    s = size
    # Tres olas desplazadas verticalmente
    for i, dy_off in enumerate([-s * 0.25, 0, s * 0.25]):
        oy = int(cy + dy_off)
        pts = []
        steps = 16
        for step in range(steps + 1):
            t = step / steps
            x = int(cx - s * 0.55 + t * s * 1.1)
            y = int(oy + math.sin(t * math.pi * 2) * s * 0.15)
            pts.append((x, y))
        for j in range(len(pts) - 1):
            _line(surface, color, pts[j], pts[j + 1], max(1, s // 7))


# ─────────────────────────────────────────────────────────────
#  SOL / RA  –  Rueda Solar
# ─────────────────────────────────────────────────────────────

def draw_icon_sun(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Sol radiante: Ra / Rueda Solar."""
    cx, cy = center
    s = size
    # Núcleo
    _circle(surface, color, (cx, cy), int(s * 0.38))
    # Rayos
    num_rays = 8
    for i in range(num_rays):
        angle = math.radians(i * 360 / num_rays)
        ix = int(cx + math.cos(angle) * s * 0.45)
        iy = int(cy + math.sin(angle) * s * 0.45)
        ox = int(cx + math.cos(angle) * s * 0.75)
        oy = int(cy + math.sin(angle) * s * 0.75)
        _line(surface, color, (ix, iy), (ox, oy), max(1, s // 7))


# ─────────────────────────────────────────────────────────────
#  ANKH  –  Mandamientos / Egipcio
# ─────────────────────────────────────────────────────────────

def draw_icon_ankh(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Cruz ankh: Mandamientos / Simbolismo Egipcio."""
    cx, cy = center
    s = size
    lw = max(2, s // 5)
    # Palo vertical inferior
    _line(surface, color,
          (cx, int(cy + s * 0.55)),
          (cx, int(cy - s * 0.05)), lw)
    # Palo horizontal
    _line(surface, color,
          (int(cx - s * 0.4), int(cy - s * 0.15)),
          (int(cx + s * 0.4), int(cy - s * 0.15)), lw)
    # Anillo superior (óvalo)
    loop_rect = pygame.Rect(int(cx - s * 0.3), int(cy - s * 0.55), int(s * 0.6), int(s * 0.45))
    _rect(surface, color, loop_rect, border_radius=int(s * 0.3), width=lw)


# ─────────────────────────────────────────────────────────────
#  PERGAMINO  –  Carta de Moisés
# ─────────────────────────────────────────────────────────────

def draw_icon_scroll(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Pergamino enrollado: Cartas de Moisés."""
    cx, cy = center
    s = size
    # Cuerpo central del pergamino
    body = pygame.Rect(int(cx - s * 0.4), int(cy - s * 0.45), int(s * 0.8), int(s * 0.9))
    _rect(surface, color, body, border_radius=int(s * 0.1))
    # Rollos superior e inferior
    roll_col = tuple(min(255, c + 40) for c in color)
    top_roll = pygame.Rect(int(cx - s * 0.48), int(cy - s * 0.5), int(s * 0.96), int(s * 0.12))
    bot_roll = pygame.Rect(int(cx - s * 0.48), int(cy + s * 0.38), int(s * 0.96), int(s * 0.12))
    _rect(surface, roll_col, top_roll, border_radius=int(s * 0.06))
    _rect(surface, roll_col, bot_roll, border_radius=int(s * 0.06))
    # Líneas de texto
    line_col = tuple(max(0, c - 80) for c in color)
    for i in range(3):
        lx = int(cx - s * 0.28)
        ly = int(cy - s * 0.22 + i * s * 0.22)
        _line(surface, line_col, (lx, ly), (int(cx + s * 0.28), ly), max(1, s // 9))


# ─────────────────────────────────────────────────────────────
#  CARRO DE GUERRA  –  Éxodo B
# ─────────────────────────────────────────────────────────────

def draw_icon_chariot(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Carro de guerra egipcio: Éxodo B."""
    cx, cy = center
    s = size
    # Rueda izquierda
    _circle(surface, color, (int(cx - s * 0.35), int(cy + s * 0.25)), int(s * 0.28), width=max(2, s // 7))
    # Rueda derecha
    _circle(surface, color, (int(cx + s * 0.35), int(cy + s * 0.25)), int(s * 0.28), width=max(2, s // 7))
    # Eje
    _line(surface, color,
          (int(cx - s * 0.35), int(cy + s * 0.25)),
          (int(cx + s * 0.35), int(cy + s * 0.25)), max(2, s // 7))
    # Caja del carro
    body_pts = [
        (int(cx - s * 0.45), int(cy - s * 0.2)),
        (int(cx + s * 0.45), int(cy - s * 0.2)),
        (int(cx + s * 0.35), int(cy + s * 0.02)),
        (int(cx - s * 0.35), int(cy + s * 0.02)),
    ]
    bright = tuple(min(255, c + 40) for c in color)
    _poly(surface, bright, body_pts)
    # Lanza
    _line(surface, color,
          (int(cx - s * 0.1), int(cy + s * 0.02)),
          (int(cx - s * 0.75), int(cy - s * 0.1)), max(1, s // 8))


# ─────────────────────────────────────────────────────────────
#  ESTRELLA  –  Victoria / Fe general
# ─────────────────────────────────────────────────────────────

def draw_icon_star(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Estrella de 5 puntas: Victoria / Fe."""
    cx, cy = center
    s = size
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = s * 0.55 if i % 2 == 0 else s * 0.25
        pts.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
    _poly(surface, color, pts)


# ─────────────────────────────────────────────────────────────
#  CALAVERA  –  Bolsa Negra / Sacrificio
# ─────────────────────────────────────────────────────────────

def draw_icon_skull(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Calavera: Bolsa Negra / Sacrificio."""
    cx, cy = center
    s = size
    # Cráneo
    skull_rect = pygame.Rect(int(cx - s * 0.4), int(cy - s * 0.5), int(s * 0.8), int(s * 0.7))
    _rect(surface, color, skull_rect, border_radius=int(s * 0.35))
    # Mandíbula
    jaw_rect = pygame.Rect(int(cx - s * 0.28), int(cy + s * 0.18), int(s * 0.56), int(s * 0.28))
    _rect(surface, color, jaw_rect, border_radius=int(s * 0.1))
    # Ojos
    eye_col = (15, 10, 15)
    _circle(surface, eye_col, (int(cx - s * 0.17), int(cy - s * 0.1)), max(2, s // 6))
    _circle(surface, eye_col, (int(cx + s * 0.17), int(cy - s * 0.1)), max(2, s // 6))
    # Nariz
    _circle(surface, eye_col, (cx, int(cy + s * 0.08)), max(1, s // 9))
    # Dientes
    for i in range(3):
        tx = int(cx - s * 0.2 + i * s * 0.2)
        ty = int(cy + s * 0.18)
        _line(surface, eye_col, (tx, ty), (tx, int(ty + s * 0.2)), max(1, s // 9))


# ─────────────────────────────────────────────────────────────
#  BOLSA  –  Bolsas generales
# ─────────────────────────────────────────────────────────────

def draw_icon_bag(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Bolsa atada: Bolsas generales."""
    cx, cy = center
    s = size
    # Cuerpo de la bolsa
    body = pygame.Rect(int(cx - s * 0.42), int(cy - s * 0.25), int(s * 0.84), int(s * 0.75))
    _rect(surface, color, body, border_radius=int(s * 0.35))
    # Nudo
    bright = tuple(min(255, c + 60) for c in color)
    knot = pygame.Rect(int(cx - s * 0.2), int(cy - s * 0.42), int(s * 0.4), int(s * 0.2))
    _rect(surface, bright, knot, border_radius=int(s * 0.1))
    # Lazo
    _line(surface, bright,
          (int(cx - s * 0.2), int(cy - s * 0.35)),
          (int(cx - s * 0.4), int(cy - s * 0.55)), max(1, s // 8))
    _line(surface, bright,
          (int(cx + s * 0.2), int(cy - s * 0.35)),
          (int(cx + s * 0.4), int(cy - s * 0.55)), max(1, s // 8))


# ─────────────────────────────────────────────────────────────
#  OJO DE HORUS  –  Decorativo
# ─────────────────────────────────────────────────────────────

def draw_icon_eye_of_horus(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Color):
    """Ojo de Horus: decorativo menú."""
    cx, cy = center
    s = size
    # Contorno del ojo (amígdala)
    pts_eye = [
        (int(cx - s * 0.6), cy),
        (int(cx - s * 0.1), int(cy - s * 0.4)),
        (int(cx + s * 0.3), int(cy - s * 0.35)),
        (int(cx + s * 0.6), cy),
        (int(cx + s * 0.3), int(cy + s * 0.35)),
        (int(cx - s * 0.1), int(cy + s * 0.4)),
    ]
    _poly(surface, color, pts_eye, width=max(1, s // 7))
    # Iris
    iris_col = tuple(min(255, c + 60) for c in color)
    _circle(surface, iris_col, (cx, cy), int(s * 0.25))
    # Pupila
    _circle(surface, (10, 8, 12), (cx, cy), int(s * 0.13))
    # Trazo inferior derecho de Horus
    _line(surface, color,
          (int(cx + s * 0.35), int(cy + s * 0.25)),
          (int(cx + s * 0.25), int(cy + s * 0.65)), max(1, s // 8))
    _line(surface, color,
          (int(cx + s * 0.25), int(cy + s * 0.65)),
          (int(cx + s * 0.5), int(cy + s * 0.65)), max(1, s // 8))


# ─────────────────────────────────────────────────────────────
#  MAPA / TABLA DE DESPACHO  –  Mapeo de nombre → función
# ─────────────────────────────────────────────────────────────

TILE_ICON_MAP = {
    "COSECHAR":          draw_icon_wheat,
    "REZAR":             draw_icon_pray,
    "GANADERÍA":         draw_icon_cow,
    "REGADÍOS":          draw_icon_water,
    "RENACIMIENTO":      draw_icon_person,
    "RECONSTRUCCIÓN":    draw_icon_house,
    "DIOSES FAVORABLES": draw_icon_dice,
    "RENDIR PLEITESÍA":  draw_icon_pray,
}

CARD_TYPE_ICON_MAP = {
    "plaga":      draw_icon_flame,
    "personaje":  draw_icon_scroll,
    "evento":     draw_icon_sun,
    "edificio":   draw_icon_house,
}


def draw_tile_icon(surface: pygame.Surface, tile_name: str, center: Tuple[int, int], size: int, color: Color):
    """Dibuja el icono asociado al nombre de una loseta de acción."""
    fn = TILE_ICON_MAP.get(tile_name.upper().strip())
    if fn:
        fn(surface, center, size, color)


def draw_card_type_icon(surface: pygame.Surface, card_type: str, center: Tuple[int, int], size: int, color: Color):
    """Dibuja el icono asociado al tipo de carta."""
    fn = CARD_TYPE_ICON_MAP.get(card_type.lower().strip())
    if fn:
        fn(surface, center, size, color)
