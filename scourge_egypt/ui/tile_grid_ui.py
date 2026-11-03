"""
Componente UI para el Grid de las 8 Losetas de Acción del jugador activo.
Muestra el estado (activa, usada, destruida), símbolos y permite la selección interactiva.
"""
from __future__ import annotations
import pygame
from typing import List, Optional, Tuple, Callable
from scourge_egypt.models import ActionTile, Player
from scourge_egypt.ui.theme import (
    FontManager, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_PAPYRUS, COLOR_CRIMSON,
    COLOR_GRAY, COLOR_GRAY_DARK, COLOR_WHITE, COLOR_BLACK
)
from scourge_egypt.ui.audio import SoundManager
from scourge_egypt.ui.icons import draw_tile_icon


class TileGridUI:
    def __init__(self, rect: pygame.Rect, on_tile_click: Callable[[int], None]):
        self.rect = rect
        self.on_tile_click = on_tile_click
        self.hovered_index: Optional[int] = None
        self.mouse_pos = (0, 0)
        self.tile_rects: List[pygame.Rect] = []

        # 8 losetas dispuestas en 2 filas x 4 columnas
        cols = 4
        rows = 2
        padding_x = 8
        padding_y = 8
        tile_w = (rect.width - (cols + 1) * padding_x) // cols
        tile_h = (rect.height - (rows + 1) * padding_y) // rows

        self.tile_rects = []
        for r in range(rows):
            for c in range(cols):
                tx = rect.x + padding_x + c * (tile_w + padding_x)
                ty = rect.y + padding_y + r * (tile_h + padding_y)
                self.tile_rects.append(pygame.Rect(tx, ty, tile_w, tile_h))

    def handle_event(self, event: pygame.event.Event, player: Player) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self.hovered_index = None
            for idx, r in enumerate(self.tile_rects):
                if r.collidepoint(event.pos):
                    self.hovered_index = idx
                    break
            return False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, r in enumerate(self.tile_rects):
                if r.collidepoint(event.pos):
                    if idx < len(player.losetas_accion):
                        tile = player.losetas_accion[idx]
                        if tile.state == "activa":
                            SoundManager.get_instance().play("click")
                            self.on_tile_click(idx)
                            return True
            return False
        return False

    def draw(self, surface: pygame.Surface, player: Player):
        # Panel contenedor
        pygame.draw.rect(surface, COLOR_BG_PANEL, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, self.rect, width=2, border_radius=8)

        font_name = FontManager.get_font(13, bold=True)
        font_sub = FontManager.get_font(11)

        for idx, rect in enumerate(self.tile_rects):
            if idx >= len(player.losetas_accion):
                continue

            tile = player.losetas_accion[idx]
            is_hovered = (self.hovered_index == idx and tile.state == "activa")

            if tile.state == "activa":
                bg_col = (55, 45, 65) if is_hovered else COLOR_BG_CARD
                border_col = COLOR_GOLD_LIGHT if is_hovered else COLOR_GOLD
                text_col = COLOR_GOLD_LIGHT
                status_txt = tile.symbol_type
                status_col = (240, 200, 100)
            elif tile.state == "usada_boca_abajo":
                bg_col = (25, 23, 28)
                border_col = COLOR_GRAY_DARK
                text_col = COLOR_GRAY
                status_txt = "USADA"
                status_col = COLOR_GRAY
            else:  # destruida
                bg_col = (35, 20, 25)
                border_col = COLOR_CRIMSON
                text_col = (180, 100, 100)
                status_txt = "DESTRUIDA"
                status_col = COLOR_CRIMSON

            pygame.draw.rect(surface, bg_col, rect, border_radius=6)
            pygame.draw.rect(surface, border_col, rect, width=2 if is_hovered else 1, border_radius=6)

            # Icono central de la loseta
            icon_size = max(8, min(rect.height // 4, 14))
            icon_center = (rect.centerx, rect.top + rect.height // 2 - 4)
            icon_col = text_col if tile.state == "activa" else status_col
            draw_tile_icon(surface, tile.name, icon_center, icon_size, icon_col)

            # Nombre de la loseta (encima del icono)
            name_surf = font_name.render(tile.name, True, text_col)
            name_rect = name_surf.get_rect(centerx=rect.centerx, top=rect.top + 5)
            surface.blit(name_surf, name_rect)

            # Símbolo / Estado (debajo del icono)
            sym_surf = font_sub.render(status_txt, True, status_col)
            sym_rect = sym_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 4)
            surface.blit(sym_surf, sym_rect)

        # Si hay loseta en hover, dibujar tooltip flotante con descripción
        if self.hovered_index is not None and self.hovered_index < len(player.losetas_accion):
            tile = player.losetas_accion[self.hovered_index]
            self._draw_tooltip(surface, tile)

    def _draw_tooltip(self, surface: pygame.Surface, tile: ActionTile):
        font = FontManager.get_font(12)
        max_w = min(360, surface.get_width() - 32)
        words = f"{tile.name} ({tile.symbol_type}): {tile.description}".split()
        lines, line = [], ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] <= max_w - 20:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        t_w = max((font.size(item)[0] for item in lines), default=0)
        t_h = len(lines) * 17
        mx, my = self.mouse_pos
        tip_x = min(surface.get_width() - t_w - 20, max(10, mx - t_w // 2))
        tip_y = my - t_h - 18
        if tip_y < 5:
            tip_y = min(surface.get_height() - t_h - 16, my + 25)

        tip_rect = pygame.Rect(tip_x, tip_y, t_w + 20, t_h + 12)
        pygame.draw.rect(surface, (15, 12, 18), tip_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD, tip_rect, width=1, border_radius=4)
        for index, item in enumerate(lines):
            surface.blit(font.render(item, True, COLOR_PAPYRUS), (tip_x + 10, tip_y + 6 + index * 17))
