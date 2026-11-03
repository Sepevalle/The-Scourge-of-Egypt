"""
Vista interactiva y renderizado de la Fase Éxodo B (La Persecución en el Mar Rojo).
Representa el circuito lineal de 30 casillas, carros de combate, olas del mar y dados.
"""
from __future__ import annotations
import math
import pygame
from typing import Optional, List, Tuple
from scourge_egypt.exodus_b_engine import ExodusBEngine
from scourge_egypt.models import Player, Carro
from scourge_egypt.ui.theme import (
    FontManager, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_LAPIS, COLOR_LAPIS_LIGHT, COLOR_BG_PANEL, COLOR_BG_CARD,
    COLOR_BG_DARK, COLOR_PAPYRUS, COLOR_CRIMSON, COLOR_CRIMSON_DARK,
    COLOR_BLUE_SEA, COLOR_BLUE_DEEP, COLOR_WHITE, COLOR_BLACK, COLOR_GRAY
)
from scourge_egypt.ui.components import Button


class ExodusBView:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.font_title = FontManager.get_font(20, bold=True)
        self.font_sub = FontManager.get_font(14, bold=True)
        self.font_body = FontManager.get_font(12)
        self.font_small = FontManager.get_font(10)

        # Botones de acción
        btn_y = rect.bottom - 60
        self.btn_roll = Button(
            rect=pygame.Rect(rect.x + 30, btn_y, 220, 42),
            text="LANZAR DADOS (D6 + D12)",
            font_size=13
        )
        self.btn_risk = Button(
            rect=pygame.Rect(rect.x + 270, btn_y, 180, 42),
            text="ARRIESGAR (1 CUBO)",
            color_bg=COLOR_CRIMSON_DARK,
            color_hover=COLOR_CRIMSON,
            font_size=13
        )
        self.btn_pass = Button(
            rect=pygame.Rect(rect.x + 470, btn_y, 140, 42),
            text="NO ARRIESGAR",
            color_bg=COLOR_BG_CARD,
            color_hover=(60, 50, 70),
            font_size=13
        )

        # Opciones Mar Rojo (Avanzar vs Destruir casilla)
        self.btn_sea_adv = Button(
            rect=pygame.Rect(rect.x + 630, btn_y, 170, 42),
            text="AVANZAR +1 MAR",
            color_bg=COLOR_LAPIS,
            color_hover=COLOR_LAPIS_LIGHT,
            font_size=13
        )
        self.btn_sea_dest = Button(
            rect=pygame.Rect(rect.x + 820, btn_y, 200, 42),
            text="COLAPSAR ÚLTIMA CASILLA",
            color_bg=(140, 40, 40),
            color_hover=COLOR_CRIMSON,
            font_size=13
        )

    def handle_event(self, event: pygame.event.Event, engine: ExodusBEngine):
        if engine.is_game_over:
            return

        if engine.pending_risk:
            if self.btn_risk.handle_event(event):
                active_c = engine.get_active_carro(engine.current_player)
                if active_c:
                    engine.resolve_risk(active_c)
            elif self.btn_pass.handle_event(event):
                engine.pass_risk()
            return

        if engine.pending_sea_choice:
            active_c = engine.get_active_carro(engine.current_player)
            if active_c:
                if self.btn_sea_adv.handle_event(event):
                    engine.resolve_sea_choice(active_c, "advance")
                elif self.btn_sea_dest.handle_event(event):
                    engine.resolve_sea_choice(active_c, "destroy_space")
            return

        if self.btn_roll.handle_event(event):
            engine.execute_turn_phase_1_or_2()

    def draw(self, surface: pygame.Surface, engine: ExodusBEngine):
        # Panel de fondo
        pygame.draw.rect(surface, (16, 14, 20), self.rect)
        pygame.draw.rect(surface, COLOR_GOLD, self.rect, width=2)

        # Título y Estado
        t_surf = self.font_title.render("ÉXODO B: LA PERSECUCIÓN EN EL MAR ROJO", True, COLOR_GOLD_LIGHT)
        surface.blit(t_surf, (self.rect.x + 25, self.rect.y + 15))

        cur_p = engine.current_player
        p_txt = f"Turno activo: {cur_p.nombre_faccion} (Acólitos disponibles: {cur_p.reserva_acolitos})"
        p_surf = self.font_sub.render(p_txt, True, cur_p.color)
        surface.blit(p_surf, (self.rect.x + 25, self.rect.y + 45))

        # -------------------------------------------------------------
        # CIRCUITO DE 30 CASILLAS (Representado en 2 tramos de 15)
        # -------------------------------------------------------------
        self._draw_track(surface, engine)

        # -------------------------------------------------------------
        # PANEL CENTRAL DE DADOS Y CARTA ROBADA
        # -------------------------------------------------------------
        self._draw_dice_panel(surface, engine)

        # -------------------------------------------------------------
        # BOTONES DE ACCIÓN SEGÚN ESTADO
        # -------------------------------------------------------------
        if engine.pending_risk:
            self.btn_risk.draw(surface)
            self.btn_pass.draw(surface)
        elif engine.pending_sea_choice:
            self.btn_sea_adv.draw(surface)
            self.btn_sea_dest.draw(surface)
        else:
            self.btn_roll.draw(surface)

    def _draw_track(self, surface: pygame.Surface, engine: ExodusBEngine):
        """Dibuja las 30 casillas del circuito con los carros encima."""
        # Tramo 1: Casillas 1 a 15 (Torbellino de Fuego)
        # Tramo 2: Casillas 16 a 30 (16-19 Torbellino, 20-30 Mar Rojo)
        start_x = self.rect.x + 30
        track_w = self.rect.width - 60
        box_w = track_w // 15
        box_h = 44

        # Fila 1: 1 a 15
        y1 = self.rect.y + 80
        for i in range(1, 16):
            bx = start_x + (i - 1) * box_w
            b_rect = pygame.Rect(bx, y1, box_w - 4, box_h)
            # 1 a 15: Torbellino de fuego (naranja/arena oscura)
            pygame.draw.rect(surface, (45, 30, 20), b_rect, border_radius=4)
            pygame.draw.rect(surface, (180, 100, 30), b_rect, width=1, border_radius=4)

            num_surf = self.font_small.render(str(i), True, COLOR_PAPYRUS)
            surface.blit(num_surf, (bx + 4, y1 + 3))

            self._draw_chariots_at_position(surface, engine, i, b_rect)

        # Fila 2: 16 a 30
        y2 = self.rect.y + 140
        for i in range(16, 31):
            col_idx = i - 16
            bx = start_x + col_idx * box_w
            b_rect = pygame.Rect(bx, y2, box_w - 4, box_h)

            is_sea = (i >= 20)
            is_destroyed = (i > engine.board_state.casillas_activas_mar_rojo)
            is_threshold = (i == 20)

            if is_destroyed:
                bg_col = (10, 20, 35)
                border_col = (20, 50, 90)
                txt_col = (50, 80, 120)
            elif is_threshold:
                bg_col = (60, 50, 20)
                border_col = COLOR_GOLD_LIGHT
                txt_col = COLOR_GOLD_LIGHT
            elif is_sea:
                bg_col = (15, 45, 80)
                border_col = COLOR_LAPIS_LIGHT
                txt_col = (180, 220, 255)
            else:
                bg_col = (45, 30, 20)
                border_col = (180, 100, 30)
                txt_col = COLOR_PAPYRUS

            pygame.draw.rect(surface, bg_col, b_rect, border_radius=4)
            pygame.draw.rect(surface, border_col, b_rect, width=2 if is_threshold else 1, border_radius=4)

            # Etiqueta número o 'AGUA'
            label = "AGUA" if is_destroyed else (f"{i}★" if is_threshold else str(i))
            num_surf = self.font_small.render(label, True, txt_col)
            surface.blit(num_surf, (bx + 4, y2 + 3))

            if not is_destroyed:
                self._draw_chariots_at_position(surface, engine, i, b_rect)

    def _draw_chariots_at_position(self, surface: pygame.Surface, engine: ExodusBEngine, pos: int, cell_rect: pygame.Rect):
        """Dibuja los carros de cada facción que ocupen una casilla."""
        matching_chariots: List[Tuple[Player, Carro]] = []
        for p in engine.players:
            for c in p.carros_exodo_b:
                if c.position == pos and c.status in ("en_carrera", "escapado"):
                    matching_chariots.append((p, c))

        for idx, (p, c) in enumerate(matching_chariots[:3]):
            cx = cell_rect.x + 8 + idx * 16
            cy = cell_rect.y + 24
            # Círculo del carro con el color de su facción
            pygame.draw.circle(surface, p.color, (cx, cy), 6)
            pygame.draw.circle(surface, COLOR_WHITE if not c.reverse_to_20 else (255, 230, 0), (cx, cy), 6, width=1)
            # ID de carro
            id_surf = self.font_small.render(str(c.carro_id), True, COLOR_BLACK)
            surface.blit(id_surf, (cx - 3, cy - 5))

    def _draw_dice_panel(self, surface: pygame.Surface, engine: ExodusBEngine):
        """Dibuja resultados de tiradas de dados, divinidad y Moisés."""
        p_rect = pygame.Rect(self.rect.x + 30, self.rect.y + 205, self.rect.width - 60, 140)
        pygame.draw.rect(surface, COLOR_BG_PANEL, p_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, p_rect, width=1, border_radius=8)

        # Columna 1: Dados
        d_x = p_rect.x + 20
        d_y = p_rect.y + 15
        h_surf = self.font_sub.render("ÚLTIMA TIRADA DE COMBATE:", True, COLOR_GOLD_LIGHT)
        surface.blit(h_surf, (d_x, d_y))

        d6 = engine.last_roll_d6
        d12 = engine.last_roll_d12
        adv = engine.last_advance
        god = engine.last_god_card

        god_str = f"{god.god_name} (+{god.ra_symbols + god.seth_symbols} símb.)" if god else "Ninguna"
        d_txt = f"Dado Facción D6: {d6} | Divinidad: {god_str} | Dado Moisés D12: {d12}"
        d_surf = self.font_body.render(d_txt, True, COLOR_PAPYRUS)
        surface.blit(d_surf, (d_x, d_y + 26))

        adv_col = COLOR_EMERALD if adv > 0 else COLOR_CRIMSON
        adv_txt = f"Cálculo de Avance: ({d6} + Divinidad) - {d12} = {adv} casillas"
        adv_surf = self.font_sub.render(adv_txt, True, adv_col)
        surface.blit(adv_surf, (d_x, d_y + 48))

        # Columna 2: Estado del Mar y Peligros
        sea_x = p_rect.x + 480
        sea_txt = f"Límite Casillas Activas: {engine.board_state.casillas_activas_mar_rojo}/30"
        sea_surf = self.font_body.render(sea_txt, True, COLOR_BLUE_SEA if not engine.board_state.segundo_carro_en_20 else COLOR_CRIMSON)
        surface.blit(sea_surf, (sea_x, d_y + 15))

        status_txt = "¡AGUAS CERRÁNDOSE! Carros < 21 destruidos." if engine.board_state.segundo_carro_en_20 else "Aguas en calma (Esperando a un segundo carro en casilla 20)."
        stat_surf = self.font_small.render(status_txt, True, COLOR_PAPYRUS)
        surface.blit(stat_surf, (sea_x, d_y + 38))

        # Resumen de carros escapados
        escaped_summary = []
        for p in engine.players:
            esc = sum(1 for c in p.carros_exodo_b if c.status == "escapado")
            dest = sum(1 for c in p.carros_exodo_b if c.status == "destruido")
            escaped_summary.append(f"{p.nombre_faccion}: {esc} a salvo, {dest} caídos")
        sum_surf = self.font_small.render(" | ".join(escaped_summary), True, COLOR_GOLD)
        surface.blit(sum_surf, (d_x, d_y + 80))
