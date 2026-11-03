"""
Componente gráfico interactivo de la Rueda Solar (Gracia del Faraón).
Renderiza dos anillos concéntricos con los símbolos del Sol y los Nombres de Dioses.
"""
from __future__ import annotations
import math
import pygame
from typing import Tuple, Dict, Any, Optional
from scourge_egypt.ui.theme import (
    FontManager, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_LAPIS, COLOR_LAPIS_LIGHT, COLOR_BG_PANEL, COLOR_BG_DARK,
    COLOR_PAPYRUS, COLOR_CRIMSON, COLOR_WHITE, COLOR_BLACK, COLOR_GRAY_LIGHT
)
from scourge_egypt.rules import SOLAR_WHEEL_INNER, SOLAR_WHEEL_OUTER


class SolarWheelUI:
    def __init__(self, center: Tuple[int, int], radius: int = 110):
        self.center = center
        self.radius = radius
        self.inner_radius = int(radius * 0.58)

        self.current_inner_idx: int = 0
        self.current_outer_idx: int = 0

        self.angle_inner: float = 0.0
        self.angle_outer: float = 0.0
        self.target_angle_inner: float = 0.0
        self.target_angle_outer: float = 0.0

        self.is_animating: bool = False

    def update_indices(self, inner_idx: int, outer_idx: int, animate: bool = True):
        self.current_inner_idx = inner_idx % len(SOLAR_WHEEL_INNER)
        self.current_outer_idx = outer_idx % len(SOLAR_WHEEL_OUTER)

        # Cada sección tiene un ángulo en radianes
        step_inner = (2 * math.pi) / len(SOLAR_WHEEL_INNER)
        step_outer = (2 * math.pi) / len(SOLAR_WHEEL_OUTER)

        self.target_angle_inner = -self.current_inner_idx * step_inner
        self.target_angle_outer = -self.current_outer_idx * step_outer

        if not animate:
            self.angle_inner = self.target_angle_inner
            self.angle_outer = self.target_angle_outer
        else:
            self.is_animating = True

    def update(self):
        if self.is_animating:
            diff_in = self.target_angle_inner - self.angle_inner
            diff_out = self.target_angle_outer - self.angle_outer

            self.angle_inner += diff_in * 0.15
            self.angle_outer += diff_out * 0.15

            if abs(diff_in) < 0.01 and abs(diff_out) < 0.01:
                self.angle_inner = self.target_angle_inner
                self.angle_outer = self.target_angle_outer
                self.is_animating = False

    def draw(self, surface: pygame.Surface, active_god_names: Optional[list] = None):
        cx, cy = self.center
        active_names_lower = [g.lower() for g in (active_god_names or [])]

        # 1. Fondo de la rueda
        pygame.draw.circle(surface, COLOR_BG_PANEL, (cx, cy), self.radius)
        pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), self.radius, width=3)

        # 2. Dibujar Anillo Exterior (8 Dioses)
        num_outer = len(SOLAR_WHEEL_OUTER)
        step_outer = (2 * math.pi) / num_outer
        font_outer = FontManager.get_font(12, bold=True)

        for i, god in enumerate(SOLAR_WHEEL_OUTER):
            # Ángulo de la sección centrado en la parte superior (-pi/2)
            base_angle = -math.pi / 2 + (i * step_outer) + self.angle_outer
            # Línea divisoria
            div_angle = base_angle - (step_outer / 2)
            x1 = cx + math.cos(div_angle) * self.inner_radius
            y1 = cy + math.sin(div_angle) * self.inner_radius
            x2 = cx + math.cos(div_angle) * self.radius
            y2 = cy + math.sin(div_angle) * self.radius
            pygame.draw.line(surface, COLOR_GOLD_DARK, (x1, y1), (x2, y2), 1)

            # Posición del texto del Dios
            mid_r = (self.inner_radius + self.radius) / 2
            tx = cx + math.cos(base_angle) * mid_r
            ty = cy + math.sin(base_angle) * mid_r

            is_active = god.lower() in active_names_lower
            col = COLOR_GOLD_LIGHT if is_active else COLOR_PAPYRUS

            surf = font_outer.render(god, True, col)
            rect = surf.get_rect(center=(tx, ty))
            surface.blit(surf, rect)

        # 3. Separador entre anillo exterior e interior
        pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), self.inner_radius, width=2)
        pygame.draw.circle(surface, (25, 20, 30), (cx, cy), self.inner_radius)

        # 4. Dibujar Anillo Interior (4 Símbolos Solares)
        num_inner = len(SOLAR_WHEEL_INNER)
        step_inner = (2 * math.pi) / num_inner
        font_inner = FontManager.get_font(10, bold=True)

        for j, symbol in enumerate(SOLAR_WHEEL_INNER):
            base_angle = -math.pi / 2 + (j * step_inner) + self.angle_inner
            div_angle = base_angle - (step_inner / 2)
            x1 = cx
            y1 = cy
            x2 = cx + math.cos(div_angle) * self.inner_radius
            y2 = cy + math.sin(div_angle) * self.inner_radius
            pygame.draw.line(surface, COLOR_GOLD_DARK, (x1, y1), (x2, y2), 1)

            mid_r = self.inner_radius * 0.55
            tx = cx + math.cos(base_angle) * mid_r
            ty = cy + math.sin(base_angle) * mid_r

            col = (255, 220, 80) if "RADIANTE" in symbol else COLOR_GRAY_LIGHT
            label = "SOL" if "RADIANTE" in symbol else ("ECLIP" if "ECLIPSE" in symbol else ("NACI" if "NACIENTE" in symbol else "PONI"))
            surf = font_inner.render(label, True, col)
            rect = surf.get_rect(center=(tx, ty))
            surface.blit(surf, rect)

        # 5. Marcador sagrado superior (Puntero del Faraón a las 12h)
        ptr_y = cy - self.radius - 8
        pts = [(cx, ptr_y + 12), (cx - 7, ptr_y), (cx + 7, ptr_y)]
        pygame.draw.polygon(surface, COLOR_GOLD_LIGHT, pts)
        pygame.draw.polygon(surface, COLOR_CRIMSON, pts, width=1)

        # Etiqueta de la Rueda Solar
        font_lbl = FontManager.get_font(12, bold=True)
        lbl_surf = font_lbl.render("RUEDA SOLAR", True, COLOR_GOLD_LIGHT)
        lbl_rect = lbl_surf.get_rect(center=(cx, cy + self.radius + 15))
        surface.blit(lbl_surf, lbl_rect)
