"""
Renderizador del tablero de juego principal para la Fase Éxodo A.
Dibuja tracks de Ira de Dios, Mandamientos de Moisés, Cosechas, Reservas y Cartas Activas.
"""
from __future__ import annotations
import pygame
from typing import Optional, Dict, Any, List
from scourge_egypt.models import BoardState, Player, Card, PlagueCard, GodCard, CommandmentCard
from scourge_egypt.ui.theme import (
    FontManager, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_LAPIS, COLOR_LAPIS_LIGHT, COLOR_BG_PANEL, COLOR_BG_CARD,
    COLOR_BG_DARK, COLOR_PAPYRUS, COLOR_CRIMSON, COLOR_CRIMSON_DARK,
    COLOR_EMERALD, COLOR_WHITE, COLOR_GRAY, COLOR_GRAY_DARK, COLOR_BLACK
)
from scourge_egypt.rules import REQUISITO_FE_EXODO_A, get_potenciacion
from scourge_egypt.ui.icons import (
    draw_icon_flame, draw_icon_wheat, draw_icon_cow,
    draw_icon_house, draw_icon_skull, draw_icon_star,
    draw_icon_scroll, draw_icon_sun, draw_icon_ankh,
    draw_card_type_icon,
)


class BoardRenderer:
    def __init__(self):
        self.font_header = FontManager.get_font(18, bold=True)
        self.font_sub = FontManager.get_font(13, bold=True)
        self.font_small = FontManager.get_font(11)
        self.font_body = FontManager.get_font(12)

    def draw_hud(self, surface: pygame.Surface, board_state: BoardState, player: Player, turn_num: int, round_num: int, subphase: str = "", actions_remaining: int = 0, trends: Optional[Dict[str, int]] = None):
        """Dibuja la barra superior del HUD (Ira de Dios, Mandamientos y Datos de Turno)."""
        sw = surface.get_width()
        hud_h = 70
        hud_rect = pygame.Rect(0, 0, sw, hud_h)

        pygame.draw.rect(surface, (14, 12, 18), hud_rect)
        pygame.draw.line(surface, COLOR_GOLD, (0, hud_h), (sw, hud_h), 2)

        # 1. Título y Turno
        title_surf = self.font_header.render("THE SCOURGE OF EGYPT", True, COLOR_GOLD_LIGHT)
        surface.blit(title_surf, (15, 12))

        phase_names = {"DRAW_MOSES": "ROBA CARTA", "ACTIONS": "ELIGE ACCIONES", "END_TURN": "CIERRA TURNO"}
        phase = phase_names.get(subphase, subphase.replace("_", " ") if subphase else board_state.fase_actual)
        sub_txt = f"RONDA {round_num}  |  TURNO {turn_num}  |  {phase}"
        sub_surf = self.font_small.render(sub_txt, True, COLOR_PAPYRUS)
        surface.blit(sub_surf, (15, 42))

        # 2. Barra de Ira de Dios (0..50)
        ira_x = 280
        ira_y = 14
        ira_w = 260
        ira_h = 20
        ira_val = min(50, max(0, board_state.ira_de_dios))
        pot = get_potenciacion(ira_val)

        # Icono de llama
        draw_icon_flame(surface, (ira_x + 8, ira_y + 8), 7, COLOR_CRIMSON)

        ira_delta = (trends or {}).get("ira", 0)
        ira_lbl = self.font_sub.render(
            f"Ira de Dios: {ira_val}/50 (+{pot} Potencia) {self._trend_mark(ira_delta)}",
            True, COLOR_GOLD_LIGHT
        )
        surface.blit(ira_lbl, (ira_x + 20, ira_y))

        # Barra
        bar_rect = pygame.Rect(ira_x, ira_y + 24, ira_w, 16)
        pygame.draw.rect(surface, (40, 20, 20), bar_rect, border_radius=4)
        fill_w = int(ira_w * (ira_val / 50.0))
        if fill_w > 0:
            fill_rect = pygame.Rect(ira_x, ira_y + 24, fill_w, 16)
            col_bar = COLOR_CRIMSON if ira_val >= 40 else ((220, 120, 30) if ira_val >= 20 else (200, 170, 40))
            pygame.draw.rect(surface, col_bar, fill_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, bar_rect, width=1, border_radius=4)

        # Marcadores de umbral en 20 (Rayo 1) y 40 (Rayo 2)
        mark_20_x = ira_x + int(ira_w * (20 / 50.0))
        mark_40_x = ira_x + int(ira_w * (40 / 50.0))
        pygame.draw.line(surface, COLOR_WHITE, (mark_20_x, ira_y + 20), (mark_20_x, ira_y + 42), 2)
        pygame.draw.line(surface, COLOR_WHITE, (mark_40_x, ira_y + 20), (mark_40_x, ira_y + 42), 2)

        # 3. Track de Mandamientos de Moisés (I al X)
        mand_x = 570
        mand_y = 14
        mand_lbl = self.font_sub.render(f"Moisés: Mandamiento {board_state.mandamiento_actual}/10", True, COLOR_GOLD_LIGHT)
        surface.blit(mand_lbl, (mand_x, mand_y))

        romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        step_box_w = 23
        for idx, r_num in enumerate(romans, start=1):
            bx = mand_x + (idx - 1) * (step_box_w + 3)
            by = mand_y + 24
            b_rect = pygame.Rect(bx, by, step_box_w, 18)
            is_active = (idx == board_state.mandamiento_actual)
            is_past = (idx < board_state.mandamiento_actual)

            bg_col = COLOR_GOLD if is_active else (COLOR_LAPIS if is_past else COLOR_BG_CARD)
            pygame.draw.rect(surface, bg_col, b_rect, border_radius=3)
            pygame.draw.rect(surface, COLOR_GOLD_DARK, b_rect, width=1, border_radius=3)

            t_col = COLOR_BLACK if is_active else COLOR_PAPYRUS
            r_surf = self.font_small.render(r_num, True, t_col)
            surface.blit(r_surf, r_surf.get_rect(center=b_rect.center))

        # Altar de cubos blancos en mandamiento actual (0..5)
        cubes_txt = f"Cubos altar: [{board_state.cubos_mandamiento}/5]"
        c_surf = self.font_small.render(cubes_txt, True, (240, 240, 240))
        surface.blit(c_surf, (mand_x + 10 * (step_box_w + 3) + 10, mand_y + 27))

        # 4. Banner del Jugador Activo (Extremo Derecho)
        p_x = sw - 280
        p_y = 8
        pygame.draw.rect(surface, COLOR_BG_CARD, (p_x, p_y, 265, 54), border_radius=6)
        pygame.draw.rect(surface, player.color, (p_x, p_y, 265, 54), width=2, border_radius=6)

        p_name_surf = self.font_sub.render(f"JUEGA AHORA: {player.nombre_faccion}", True, player.color)
        surface.blit(p_name_surf, (p_x + 8, p_y + 6))

        stats_txt = f"Acólitos: {player.reserva_acolitos} | Fe: {player.tokens_fe} | Rerolls: {player.rerolls_disponibles}"
        stats_surf = self.font_small.render(stats_txt, True, COLOR_PAPYRUS)
        surface.blit(stats_surf, (p_x + 8, p_y + 30))

    def draw_harvest_tracks(self, surface: pygame.Surface, board_state: BoardState, rect: pygame.Rect, trends: Optional[Dict[str, int]] = None):
        """Dibuja los tracks de Cosechas (Trigo, Avena, Cebada)."""
        pygame.draw.rect(surface, COLOR_BG_PANEL, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, rect, width=2, border_radius=8)

        title = self.font_sub.render("TRACKS DE COSECHAS Y HAMBRUNA", True, COLOR_GOLD_LIGHT)
        surface.blit(title, (rect.x + 15, rect.y + 12))

        crops = [
            ("trigo", "Trigo", (220, 190, 80)),
            ("avena", "Avena", (200, 170, 120)),
            ("cebada", "Cebada", (180, 200, 100))
        ]

        start_y = rect.y + 40
        track_w = rect.width - 155
        num_steps = 11  # 0..10

        for i, (key, name, color) in enumerate(crops):
            val = board_state.cosechas.get(key, 0)
            ty = start_y + i * 36

            # Icono de espiga
            draw_icon_wheat(surface, (rect.x + 22, ty + 9), 7, color)

            # Nombre
            n_surf = self.font_body.render(name, True, color)
            surface.blit(n_surf, (rect.x + 35, ty))

            # Barra del track
            tx = rect.x + 95
            th = 18
            bg_bar = pygame.Rect(tx, ty, track_w, th)
            pygame.draw.rect(surface, (20, 18, 24), bg_bar, border_radius=3)

            # Umbral de Alerta Hambruna en posición 5
            x_alert = tx + int(track_w * (5 / 10.0))
            pygame.draw.line(surface, (220, 140, 40), (x_alert, ty - 2), (x_alert, ty + th + 2), 2)

            # Umbral de Agotamiento en posición 10
            x_agot = tx + track_w
            pygame.draw.line(surface, COLOR_CRIMSON, (x_agot, ty - 2), (x_agot, ty + th + 2), 2)

            # Posición actual
            cur_x = tx + int(track_w * (val / 10.0))
            marker_rect = pygame.Rect(cur_x - 6, ty - 1, 12, th + 2)
            pygame.draw.rect(surface, color, marker_rect, border_radius=2)
            pygame.draw.rect(surface, COLOR_WHITE, marker_rect, width=1, border_radius=2)

            # Valor numérico
            val_txt = f"{val}/10{self._trend_mark((trends or {}).get(key, 0))}"
            v_col = COLOR_CRIMSON if val >= 10 else ((240, 160, 50) if val >= 5 else COLOR_PAPYRUS)
            v_surf = self.font_small.render(val_txt, True, v_col)
            surface.blit(v_surf, (tx + track_w + 10, ty + 2))

        # Leyenda pequeña
        ley_txt = "5: HAMBRUNA | 10: AGOTAMIENTO | ↑↓ cambio/turno"
        ley_surf = FontManager.get_font(10).render(ley_txt, True, COLOR_PAPYRUS)
        surface.blit(ley_surf, (rect.x + 15, rect.bottom - 22))

    def draw_reserves_and_bags(self, surface: pygame.Surface, board_state: BoardState, num_players: int, rect: pygame.Rect, trends: Optional[Dict[str, int]] = None):
        """Dibuja contadores de Ganado, Viviendas, Bolsa Negra y Bolsa Azul."""
        pygame.draw.rect(surface, COLOR_BG_PANEL, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, rect, width=2, border_radius=8)

        title = self.font_sub.render("RESERVAS Y BOLSAS SAGRADAS", True, COLOR_GOLD_LIGHT)
        surface.blit(title, (rect.x + 15, rect.y + 10))

        # 1. Ganado (Icono Vaca)
        g_txt = f"Ganado Global: {board_state.ganado} cubos"
        g_surf = self.font_body.render(g_txt, True, (245, 245, 245))
        draw_icon_cow(surface, (rect.x + 22, rect.y + 41), 9, (230, 230, 230))
        surface.blit(g_surf, (rect.x + 38, rect.y + 33))
        self._draw_trend(surface, rect, rect.y + 35, (trends or {}).get("ganado", 0))

        # 2. Viviendas (Icono Casa/Pirámide)
        v_col = COLOR_CRIMSON if board_state.viviendas <= 5 else (180, 180, 190)
        v_txt = f"Viviendas: {board_state.viviendas} cubos" + ("  |  NIVEL CRÍTICO" if board_state.viviendas <= 5 else "")
        v_surf = self.font_body.render(v_txt, True, v_col)
        draw_icon_house(surface, (rect.x + 22, rect.y + 61), 8, v_col)
        surface.blit(v_surf, (rect.x + 38, rect.y + 53))
        self._draw_trend(surface, rect, rect.y + 55, (trends or {}).get("viviendas", 0))

        # 3. Bolsa Negra (Icono Calavera)
        num_sac = len(board_state.bolsa_tumbas_egipcias)
        b_negra_txt = f"Bolsa Negra (Tumbas): {num_sac} sacrificios"
        bn_surf = self.font_body.render(b_negra_txt, True, (210, 110, 120))
        draw_icon_skull(surface, (rect.x + 22, rect.y + 81), 8, COLOR_CRIMSON)
        surface.blit(bn_surf, (rect.x + 38, rect.y + 73))
        self._draw_trend(surface, rect, rect.y + 75, (trends or {}).get("tumbas", 0))

        # 4. Bolsa Azul (Icono Estrella / Fe)
        req_fe = REQUISITO_FE_EXODO_A.get(num_players, 45)
        cur_fe = len(board_state.bolsa_almacenamiento_fe)
        fe_col = COLOR_GOLD_LIGHT if cur_fe >= req_fe else (120, 180, 240)
        b_azul_txt = f"Bolsa Azul (Fe): {cur_fe}/{req_fe} requerida"
        ba_surf = self.font_body.render(b_azul_txt, True, fe_col)
        draw_icon_star(surface, (rect.x + 22, rect.y + 101), 8, COLOR_LAPIS_LIGHT)
        surface.blit(ba_surf, (rect.x + 38, rect.y + 93))
        self._draw_trend(surface, rect, rect.y + 95, (trends or {}).get("fe_bolsa", 0))
        faith_bar = pygame.Rect(rect.x + 38, rect.y + 116, rect.width - 55, 9)
        pygame.draw.rect(surface, COLOR_BG_CARD, faith_bar, border_radius=4)
        ratio = min(1.0, cur_fe / max(1, req_fe))
        if ratio:
            fill = pygame.Rect(faith_bar.x, faith_bar.y, max(4, int(faith_bar.width * ratio)), faith_bar.height)
            pygame.draw.rect(surface, COLOR_LAPIS_LIGHT if cur_fe < req_fe else COLOR_GOLD, fill, border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, faith_bar, width=1, border_radius=4)

    @staticmethod
    def _trend_mark(delta: int) -> str:
        if delta > 0:
            return f"↑{delta}"
        if delta < 0:
            return f"↓{abs(delta)}"
        return "→"

    def _draw_trend(self, surface: pygame.Surface, rect: pygame.Rect, y: int, delta: int):
        color = COLOR_GOLD_LIGHT if delta else COLOR_GRAY
        text = FontManager.get_font(10, bold=True).render(self._trend_mark(delta), True, color)
        surface.blit(text, text.get_rect(right=rect.right - 10, centery=y))

    def draw_active_card_area(self, surface: pygame.Surface, card: Optional[Card], commandment: Optional[CommandmentCard], rect: pygame.Rect):
        """Dibuja la carta actual de Moisés revelada y el mandamiento activo."""
        pygame.draw.rect(surface, COLOR_BG_PANEL, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, rect, width=2, border_radius=8)

        title = self.font_sub.render("CARTA DE MOISÉS ACTIVA", True, COLOR_GOLD_LIGHT)
        surface.blit(title, (rect.x + 15, rect.y + 10))

        if card:
            hint_font = FontManager.get_font(10, bold=True)
            hint = hint_font.render("CLIC PARA LEER COMPLETA", True, COLOR_LAPIS_LIGHT)
            surface.blit(hint, (rect.right - hint.get_width() - 15, rect.y + 12))
            # Marco de la carta
            c_rect = pygame.Rect(rect.x + 15, rect.y + 32, rect.width - 30, rect.height - 42)
            c_type = getattr(card, "card_type", "").lower()

            if c_type == "plaga":
                border_c = COLOR_CRIMSON
                badge_bg = COLOR_CRIMSON_DARK
                badge_txt = "PLAGA"
            elif c_type == "personaje":
                border_c = COLOR_LAPIS_LIGHT
                badge_bg = COLOR_LAPIS
                badge_txt = "PERSONAJE BÍBLICO"
            elif c_type == "evento":
                border_c = COLOR_GOLD
                badge_bg = COLOR_GOLD_DARK
                badge_txt = "EVENTO SAGRADO"
            else:
                border_c = COLOR_EMERALD
                badge_bg = (20, 80, 50)
                badge_txt = "EDIFICIO MÍTICO"

            pygame.draw.rect(surface, COLOR_BG_CARD, c_rect, border_radius=6)
            pygame.draw.rect(surface, border_c, c_rect, width=2, border_radius=6)

            # Badge tipo con icono
            font_badge = FontManager.get_font(10, bold=True)
            b_surf = font_badge.render(badge_txt, True, COLOR_WHITE)
            badge_w = b_surf.get_width() + 28
            pygame.draw.rect(surface, badge_bg, (c_rect.x + 10, c_rect.y + 8, badge_w, 18), border_radius=3)
            draw_card_type_icon(surface, c_type, (c_rect.x + 20, c_rect.y + 17), 6, COLOR_WHITE)
            surface.blit(b_surf, (c_rect.x + 30, c_rect.y + 10))

            # Nombre
            n_surf = self.font_sub.render(card.name, True, COLOR_GOLD_LIGHT)
            surface.blit(n_surf, (c_rect.x + 10, c_rect.y + 30))

            # Descripción con salto de línea
            self._render_multiline_text(surface, card.description, c_rect.x + 10, c_rect.y + 55, c_rect.width - 20, c_rect.bottom - 5)
        else:
            no_card = self.font_body.render("Pulsa 'Robar Carta de Moisés' para iniciar el turno.", True, COLOR_GRAY)
            surface.blit(no_card, (rect.x + 20, rect.y + 40))

    def _render_multiline_text(self, surface: pygame.Surface, text: str, x: int, y: int, max_w: int, bottom: int):
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = f"{cur} {w}".strip()
            if self.font_small.size(test)[0] < max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        cur_y = y
        max_lines = max(1, (bottom - y) // 16)
        visible_lines = lines[:max_lines]
        if len(lines) > max_lines and visible_lines:
            visible_lines[-1] = visible_lines[-1].rstrip(" .") + "..."
        for l in visible_lines:
            surf = self.font_small.render(l, True, COLOR_PAPYRUS)
            surface.blit(surf, (x, cur_y))
            cur_y += 16
