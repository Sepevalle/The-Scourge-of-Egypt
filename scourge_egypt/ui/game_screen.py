"""
Gestor principal de pantallas e interfaces gráficas para The Scourge of Egypt.
Maneja Menú Principal, Tablero Éxodo A, Tablero Éxodo B, Pantalla de Reglas y Fin de Partida.
"""
from __future__ import annotations
import sys
import pygame
from typing import Optional, List, Dict, Any
from scourge_egypt.models import Player, FACTIONS_DEF
from scourge_egypt.game_engine import GameEngine
from scourge_egypt.save_load import save_game_to_file, load_game_from_file
from scourge_egypt.ui.theme import (
    FontManager, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG_DARK, COLOR_BG_PANEL, COLOR_BG_CARD,
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_LAPIS, COLOR_LAPIS_LIGHT, COLOR_PAPYRUS,
    COLOR_CRIMSON, COLOR_CRIMSON_DARK, COLOR_EMERALD,
    COLOR_WHITE, COLOR_GRAY, COLOR_GRAY_DARK, COLOR_BLACK
)
from scourge_egypt.ui.components import Button, ModalDialog, GameLoggerUI
from scourge_egypt.ui.board_renderer import BoardRenderer
from scourge_egypt.ui.solar_wheel_ui import SolarWheelUI
from scourge_egypt.ui.tile_grid_ui import TileGridUI
from scourge_egypt.ui.exodus_b_view import ExodusBView
from scourge_egypt.ui.audio import SoundManager
from scourge_egypt.ui.tutorial_screen import TutorialScreen
from scourge_egypt.ui.icons import draw_icon_ankh, draw_icon_eye_of_horus, draw_icon_star


class ScreenManager:
    def __init__(self, surface: pygame.Surface):
        self.display_surface = surface
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.current_screen: str = "MENU"   # 'MENU', 'GAME', 'RULES', 'GAME_OVER'

        self.engine: Optional[GameEngine] = None
        self.board_renderer = BoardRenderer()
        self.sound_manager = SoundManager.get_instance()

        # Configuración de partida nueva en el menú
        self.num_players: int = 2
        self.selected_factions: List[int] = [0, 1, 2, 3]

        # Componentes UI de juego
        self.solar_wheel = SolarWheelUI(center=(210, 480), radius=90)
        self.tile_grid = TileGridUI(
            rect=pygame.Rect(720, 275, 535, 175),
            on_tile_click=self._on_tile_clicked
        )
        self.logger_ui = GameLoggerUI(rect=pygame.Rect(20, 595, 1240, 115))
        self.exodus_b_view = ExodusBView(rect=pygame.Rect(20, 85, 1240, 495))

        self.active_modal: Optional[ModalDialog] = None
        self.rules_scroll: int = 0
        self.tutorial_screen = TutorialScreen(surface=self.surface, on_exit=lambda: self.set_screen("MENU"))

        self._init_menu_buttons()
        self._init_game_buttons()

        cx = SCREEN_WIDTH // 2
        self.btn_rules_back = Button(
            rect=pygame.Rect(cx - 100, SCREEN_HEIGHT - 65, 200, 42),
            text="VOLVER AL MENÚ",
            on_click=lambda: self.set_screen("MENU"),
            font_size=14
        )
        self.btn_game_over_back = Button(
            rect=pygame.Rect(cx - 110, SCREEN_HEIGHT // 2 + 70, 220, 42),
            text="VOLVER AL MENÚ",
            on_click=lambda: self.set_screen("MENU"),
            font_size=14
        )

    # -------------------------------------------------------------
    # BOTONES DE MENÚ
    # -------------------------------------------------------------
    def _init_menu_buttons(self):
        cx = SCREEN_WIDTH // 2
        self.btn_start = Button(
            rect=pygame.Rect(cx - 150, 410, 300, 42),
            text="INICIAR PARTIDA",
            on_click=self.start_new_game,
            font_size=15
        )
        self.btn_tutorial = Button(
            rect=pygame.Rect(cx - 150, 458, 300, 42),
            text="TUTORIAL (CÓMO JUGAR)",
            on_click=lambda: self.set_screen("TUTORIAL"),
            color_bg=COLOR_GOLD_DARK,
            color_hover=COLOR_GOLD,
            color_text=COLOR_WHITE,
            font_size=15
        )
        self.btn_load = Button(
            rect=pygame.Rect(cx - 150, 506, 300, 42),
            text="CARGAR PARTIDA",
            on_click=self.load_game,
            font_size=15
        )
        self.btn_rules = Button(
            rect=pygame.Rect(cx - 150, 554, 300, 42),
            text="REGLAS Y MANUAL",
            on_click=lambda: self.set_screen("RULES"),
            font_size=15
        )
        self.btn_quit = Button(
            rect=pygame.Rect(cx - 150, 602, 300, 42),
            text="VOLVER AL MENÚ" if sys.platform == "emscripten" else "SALIR",
            on_click=self._on_quit,
            color_bg=COLOR_CRIMSON_DARK,
            color_hover=COLOR_CRIMSON,
            font_size=15
        )

        # Botones de selección de jugadores
        self.btn_players_list = []
        for n in range(1, 5):
            bx = cx - 140 + (n - 1) * 75
            b = Button(
                rect=pygame.Rect(bx, 340, 60, 35),
                text=f"{n} JUG",
                on_click=lambda num=n: self._set_player_count(num),
                font_size=13
            )
            self.btn_players_list.append(b)

    def _set_player_count(self, count: int):
        self.num_players = count

    def _on_quit(self):
        if sys.platform == "emscripten":
            self.set_screen("MENU")
        else:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    # -------------------------------------------------------------
    # BOTONES DE JUEGO (ÉXODO A)
    # -------------------------------------------------------------
    def _init_game_buttons(self):
        # Botones de acción situados en el área derecha y central
        self.btn_draw_moses = Button(
            rect=pygame.Rect(720, 215, 250, 45),
            text="ROBAR CARTA DE MOISÉS",
            on_click=self._on_draw_moses,
            font_size=13
        )
        self.btn_roll_wheel = Button(
            rect=pygame.Rect(95, 330, 230, 36),
            text="GRACIA DEL FARAÓN (D6)",
            on_click=self._on_roll_solar_wheel,
            font_size=12
        )
        self.btn_donate_faith = Button(
            rect=pygame.Rect(990, 215, 125, 45),
            text="DONAR 1 FE",
            on_click=self._on_donate_faith,
            font_size=12
        )
        self.btn_buy_god = Button(
            rect=pygame.Rect(1125, 215, 130, 45),
            text="INVOCAR DIOS",
            on_click=self._on_buy_god,
            font_size=12
        )
        self.btn_end_turn = Button(
            rect=pygame.Rect(990, 465, 265, 42),
            text="FINALIZAR TURNO",
            on_click=self._on_end_turn,
            color_bg=(50, 40, 65),
            color_hover=COLOR_GOLD_DARK,
            font_size=13
        )
        self.btn_save_game = Button(
            rect=pygame.Rect(720, 465, 120, 42),
            text="GUARDAR",
            on_click=self._on_save_game,
            font_size=12
        )
        self.btn_menu_return = Button(
            rect=pygame.Rect(850, 465, 120, 42),
            text="MENÚ",
            on_click=lambda: self.set_screen("MENU"),
            color_bg=COLOR_CRIMSON_DARK,
            color_hover=COLOR_CRIMSON,
            font_size=12
        )

    def set_screen(self, screen_name: str):
        self.current_screen = screen_name
        self.sound_manager.play("click")

    def start_new_game(self):
        self.engine = GameEngine(
            num_players=self.num_players,
            faction_indices=self.selected_factions[:self.num_players]
        )
        self.engine.start_turn()
        self.current_screen = "GAME"
        self.sound_manager.play("fanfare")

    def load_game(self):
        loaded = load_game_from_file("partida_guardada.json")
        if loaded:
            self.engine = loaded
            self.current_screen = "GAME"
            self.sound_manager.play("fanfare")
        else:
            self.sound_manager.play("alert")

    # -------------------------------------------------------------
    # EVENTOS DE JUEGO (ÉXODO A)
    # -------------------------------------------------------------
    def _on_draw_moses(self):
        if not self.engine:
            return
        if self.engine.turn_subphase != "DRAW_MOSES":
            self.engine.log("Ya has robado la carta de Moisés para este turno.")
            return

        self.sound_manager.play("card")
        card = self.engine.draw_moses_card()

        # Si se activó una decisión pendiente (ej. Sangre)
        if self.engine.pending_choice:
            c = self.engine.pending_choice
            self.active_modal = ModalDialog(
                title="DECISIÓN SAGRADA: PLAGA DE SANGRE",
                message=c["message"],
                options=c["options"],
                on_select=self._on_resolve_modal_choice,
                screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT)
            )

    def _on_resolve_modal_choice(self, option_index: int):
        if self.engine and self.engine.pending_choice:
            self.engine.resolve_choice(option_index)
        self.active_modal = None

    def _on_tile_clicked(self, tile_index: int):
        if not self.engine:
            return
        player = self.engine.current_player
        tile = player.losetas_accion[tile_index]

        # Si es Cosechar, preguntar qué cereal aliviar
        if tile.id_name == "COSECHAR":
            self.active_modal = ModalDialog(
                title="LOSETA COSECHAR",
                message="Elige qué cultivo aliviar en 2 casillas:",
                options=["Aliviar Trigo", "Aliviar Avena", "Aliviar Cebada"],
                on_select=lambda idx: self._resolve_cosechar_tile(tile_index, idx),
                on_cancel=self._cancel_cosechar_tile,
                screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            return

        success = self.engine.use_action_tile(tile_index)
        if success:
            self.sound_manager.play("click")

    def _resolve_cosechar_tile(self, tile_index: int, crop_option_idx: int):
        crops = ["trigo", "avena", "cebada"]
        crop = crops[crop_option_idx]
        self.engine.use_action_tile(tile_index, extra_param=crop)
        self.active_modal = None

    def _cancel_cosechar_tile(self):
        if self.engine:
            self.engine.log("Selección de cosecha cancelada; no se gastó la acción.")
        self.active_modal = None

    def _on_roll_solar_wheel(self):
        if not self.engine:
            return
        res = self.engine.roll_solar_wheel()
        self.solar_wheel.update_indices(res["new_inner_idx"], res["new_outer_idx"])
        self.sound_manager.play("dice")
        if res["success"]:
            self.sound_manager.play("fanfare")

    def _on_donate_faith(self):
        if self.engine:
            if self.engine.donate_faith(1):
                self.sound_manager.play("click")
            else:
                self.sound_manager.play("alert")

    def _on_buy_god(self):
        if self.engine:
            god = self.engine.buy_god_card()
            if god:
                self.sound_manager.play("fanfare")
            else:
                self.sound_manager.play("alert")

    def _on_end_turn(self):
        if not self.engine:
            return
        self.engine.end_turn()
        self.sound_manager.play("click")

    def _on_save_game(self):
        if self.engine:
            save_game_to_file(self.engine, "partida_guardada.json")
            self.sound_manager.play("fanfare")

    # -------------------------------------------------------------
    # BUCLE DE EVENTOS Y ACTUALIZACIÓN
    # -------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        # Mantener coordenadas lógicas para que la interfaz responda también
        # cuando la ventana tenga un tamaño distinto al diseño de referencia.
        if hasattr(event, "pos") or event.type == pygame.MOUSEWHEEL:
            scale = min(self.display_surface.get_width() / SCREEN_WIDTH,
                        self.display_surface.get_height() / SCREEN_HEIGHT)
            ox = (self.display_surface.get_width() - SCREEN_WIDTH * scale) / 2
            oy = (self.display_surface.get_height() - SCREEN_HEIGHT * scale) / 2
            raw_pos = getattr(event, "pos", pygame.mouse.get_pos())
            pos = ((raw_pos[0] - ox) / scale, (raw_pos[1] - oy) / scale)
            event = pygame.event.Event(event.type, {**event.dict, "pos": pos})
        if self.current_screen == "MENU":
            self._handle_menu_events(event)
        elif self.current_screen == "GAME":
            self._handle_game_events(event)
        elif self.current_screen == "TUTORIAL":
            self.tutorial_screen.handle_event(event)
        elif self.current_screen == "RULES":
            self._handle_rules_events(event)
        elif self.current_screen == "GAME_OVER":
            if self.btn_game_over_back.handle_event(event):
                return
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.set_screen("MENU")

    def _handle_menu_events(self, event: pygame.event.Event):
        self.btn_start.handle_event(event)
        self.btn_tutorial.handle_event(event)
        self.btn_load.handle_event(event)
        self.btn_rules.handle_event(event)
        self.btn_quit.handle_event(event)
        for b in self.btn_players_list:
            b.handle_event(event)

    def _handle_game_events(self, event: pygame.event.Event):
        if not self.engine:
            return

        # Si hay modal activo, bloquea el resto
        if self.active_modal:
            self.active_modal.handle_event(event)
            return

        self.logger_ui.handle_event(event)

        # Si estamos en Éxodo B
        if self.engine.is_in_exodus_b:
            if self.engine.exodus_b_engine:
                self.exodus_b_view.handle_event(event, self.engine.exodus_b_engine)
                if self.engine.exodus_b_engine.is_game_over:
                    self.set_screen("GAME_OVER")
            return

        # En Éxodo A
        if self.engine.board_state.fase_actual in ("VICTORIA", "DERROTA"):
            self.set_screen("GAME_OVER")
            return

        self.btn_draw_moses.handle_event(event)
        self.btn_roll_wheel.handle_event(event)
        self.btn_donate_faith.handle_event(event)
        self.btn_buy_god.handle_event(event)
        self.btn_end_turn.handle_event(event)
        self.btn_save_game.handle_event(event)
        self.btn_menu_return.handle_event(event)

        self.tile_grid.handle_event(event, self.engine.current_player)

    def _handle_rules_events(self, event: pygame.event.Event):
        if self.btn_rules_back.handle_event(event):
            return
        if event.type == pygame.MOUSEWHEEL:
            self.rules_scroll = max(0, min(800, self.rules_scroll - event.y * 30))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.set_screen("MENU")

    def update(self):
        if self.current_screen == "GAME" and self.engine and not self.engine.is_in_exodus_b:
            self.solar_wheel.update()
        elif self.current_screen == "TUTORIAL":
            self.tutorial_screen.update()

    # -------------------------------------------------------------
    # RENDERIZADO POR PANTALLA
    # -------------------------------------------------------------
    def draw(self):
        self.surface.fill(COLOR_BG_DARK)

        if self.current_screen == "MENU":
            self._draw_menu()
        elif self.current_screen == "GAME":
            self._draw_game()
        elif self.current_screen == "TUTORIAL":
            self.tutorial_screen.draw()
        elif self.current_screen == "RULES":
            self._draw_rules()
        elif self.current_screen == "GAME_OVER":
            self._draw_game_over()

        scale = min(self.display_surface.get_width() / SCREEN_WIDTH,
                    self.display_surface.get_height() / SCREEN_HEIGHT)
        size = (max(1, int(SCREEN_WIDTH * scale)), max(1, int(SCREEN_HEIGHT * scale)))
        rendered = pygame.transform.smoothscale(self.surface, size)
        self.display_surface.fill(COLOR_BLACK)
        self.display_surface.blit(rendered, ((self.display_surface.get_width() - size[0]) // 2,
                                             (self.display_surface.get_height() - size[1]) // 2))

    def _draw_menu(self):
        cx = SCREEN_WIDTH // 2

        # Título principal con ornamentos
        font_title = FontManager.get_font(42, bold=True)
        t_surf = font_title.render("THE SCOURGE OF EGYPT", True, COLOR_GOLD_LIGHT)
        t_rect = t_surf.get_rect(center=(cx, 130))
        self.surface.blit(t_surf, t_rect)
        draw_icon_eye_of_horus(self.surface, (t_rect.left - 45, 130), 22, COLOR_GOLD)
        draw_icon_eye_of_horus(self.surface, (t_rect.right + 45, 130), 22, COLOR_GOLD)

        font_sub = FontManager.get_font(18)
        sub_surf = font_sub.render("Juego de Mesa Estratégico | Éxodo, Plagas y el Mar Rojo", True, COLOR_PAPYRUS)
        sub_rect = sub_surf.get_rect(center=(cx, 185))
        self.surface.blit(sub_surf, sub_rect)

        # Marco decorativo central
        panel_rect = pygame.Rect(cx - 240, 240, 480, 440)
        pygame.draw.rect(self.surface, COLOR_BG_PANEL, panel_rect, border_radius=12)
        pygame.draw.rect(self.surface, COLOR_GOLD, panel_rect, width=2, border_radius=12)

        # Selector de Jugadores
        font_lbl = FontManager.get_font(14, bold=True)
        lbl_surf = font_lbl.render(f"NÚMERO DE JUGADORES: {self.num_players}", True, COLOR_GOLD_LIGHT)
        self.surface.blit(lbl_surf, (cx - 140, 280))

        for idx, btn in enumerate(self.btn_players_list, start=1):
            btn.color_bg = COLOR_GOLD_DARK if idx == self.num_players else COLOR_BG_CARD
            btn.draw(self.surface)

        # Facciones asignadas
        f_y = 390
        fac_names = [FACTIONS_DEF[i]["name"] for i in range(self.num_players)]
        f_surf = font_sub.render("Facciones: " + ", ".join(fac_names), True, COLOR_PAPYRUS)
        self.surface.blit(f_surf, f_surf.get_rect(center=(cx, f_y)))

        # Botones del menú
        self.btn_start.draw(self.surface)
        self.btn_tutorial.draw(self.surface)
        self.btn_load.draw(self.surface)
        self.btn_rules.draw(self.surface)
        self.btn_quit.draw(self.surface)

    def _draw_game(self):
        if not self.engine:
            return

        # Si estamos en Éxodo B, mostrar la vista del Mar Rojo
        if self.engine.is_in_exodus_b:
            if self.engine.exodus_b_engine:
                self.exodus_b_view.draw(self.surface, self.engine.exodus_b_engine)
            self.logger_ui.draw(self.surface, self.engine.log_messages)
            return

        # 1. Barra superior HUD
        self.board_renderer.draw_hud(
            self.surface,
            self.engine.board_state,
            self.engine.current_player,
            self.engine.turn_number,
            self.engine.round_number,
            self.engine.turn_subphase,
            self.engine.actions_remaining_this_turn
        )

        # 2. Tracks de Cosechas
        cosecha_rect = pygame.Rect(20, 85, 390, 150)
        self.board_renderer.draw_harvest_tracks(self.surface, self.engine.board_state, cosecha_rect)

        # 3. Reservas y Bolsas Sagradas
        reserva_rect = pygame.Rect(425, 85, 275, 150)
        self.board_renderer.draw_reserves_and_bags(self.surface, self.engine.board_state, self.engine.num_players, reserva_rect)

        # 4. Carta de Moisés Activa
        card_rect = pygame.Rect(720, 85, 535, 120)
        self.board_renderer.draw_active_card_area(
            self.surface,
            self.engine.current_moses_card,
            self.engine.active_commandment,
            card_rect
        )

        # 5. Rueda Solar Interactiva
        active_god_names = [g.god_name for g in self.engine.current_player.dioses_activos]
        self.solar_wheel.draw(self.surface, active_god_names)
        self.btn_roll_wheel.draw(self.surface)

        # 6. Botones de acción del turno
        self.btn_draw_moses.draw(self.surface)
        self.btn_donate_faith.draw(self.surface)
        self.btn_buy_god.draw(self.surface)
        self.btn_end_turn.draw(self.surface)
        self.btn_save_game.draw(self.surface)
        self.btn_menu_return.draw(self.surface)

        # Contador de acciones restantes este turno
        font_act = FontManager.get_font(13, bold=True)
        act_txt = f"ACCIONES RESTANTES: {self.engine.actions_remaining_this_turn}"
        act_surf = font_act.render(act_txt, True, COLOR_GOLD_LIGHT)
        act_badge = pygame.Rect(720, 249, 535, 22)
        pygame.draw.rect(self.surface, COLOR_BG_PANEL, act_badge, border_radius=5)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, act_badge, width=1, border_radius=5)
        self.surface.blit(act_surf, (act_badge.x + 9, act_badge.y + 3))
        for action_idx in range(4):
            dot_color = COLOR_GOLD if action_idx < self.engine.actions_remaining_this_turn else COLOR_GRAY_DARK
            pygame.draw.circle(self.surface, dot_color, (act_badge.right - 72 + action_idx * 15, act_badge.centery), 4)

        # 7. Grid de Losetas del Jugador
        self.tile_grid.draw(self.surface, self.engine.current_player)

        # 8. Logger de Eventos
        self.logger_ui.draw(self.surface, self.engine.log_messages)

        # 9. Modal de decisión si está activo
        if self.active_modal:
            self.active_modal.draw(self.surface)

    def _draw_rules(self):
        cx = SCREEN_WIDTH // 2
        font_title = FontManager.get_font(24, bold=True)
        t_surf = font_title.render("MANUAL DE REGLAS - THE SCOURGE OF EGYPT", True, COLOR_GOLD_LIGHT)
        self.surface.blit(t_surf, t_surf.get_rect(center=(cx, 40)))

        # Contenedor de reglas con scroll
        p_rect = pygame.Rect(60, 80, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 160)
        pygame.draw.rect(self.surface, COLOR_BG_PANEL, p_rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, p_rect, width=2, border_radius=10)

        # Clip del texto scrolleable
        font_rule_h = FontManager.get_font(14, bold=True)
        font_rule_p = FontManager.get_font(12)

        rules_content = [
            ("1. OBJETIVO DEL JUEGO", [
                "Los jugadores lideran facciones del Antiguo Egipto que deben resistir las plagas bíblicas de Moisés (Éxodo A)",
                "para luego competir con sus carros en la persecución y escape a través del Mar Rojo (Éxodo B)."
            ]),
            ("2. RECURSOS Y MARCADORES (ÉXODO A)", [
                "- Ira de Dios [0..50]: Aumenta con las plagas. En 20 puntos suma +1 de potencia; en 40 puntos suma +2.",
                "- Cosechas (Trigo, Avena, Cebada) [0..10]: En posición >=5 hay Hambruna; en 10 hay Agotamiento (-1 Ganado).",
                "- Reservas Globales: Ganado (cubos blancos) y Viviendas (cubos grises). Si viviendas llegan a 0, ¡DERROTA!",
                "- Bolsa Negra (Tumbas): Acumula sacrificios de acólitos y ganado.",
                "- Bolsa Azul (Almacenamiento de Fe): Requisito indispensable para sobrevivir al fin del Éxodo A."
            ]),
            ("3. LAS 8 LOSETAS DE ACCIÓN", [
                "1. Cosechar (+2 cereal) | 2. Rezar (-2 Ira de Dios) | 3. Ganadería (+2 ganado) | 4. Regadíos (+1 acción por 1 Fe)",
                "5. Renacimiento (+2 acólitos) | 6. Reconstrucción (+2 viviendas) | 7. Dioses Favorables (+1 relanzamiento) | 8. Rendir Pleitesía (+2 Fe)"
            ]),
            ("4. MOISÉS Y MANDAMIENTOS", [
                "Al robar cartas con el símbolo de tablas de la ley, se añade 1 cubo al altar. Con 5 cubos se desbloquea un Mandamiento",
                "y el meeple de Moisés avanza. Al llegar al Mandamiento X (casilla 10), finaliza el Éxodo A y se evalúa la victoria."
            ]),
            ("5. GRACIA DEL FARAÓN (RUEDA SOLAR)", [
                "El jugador activo tira su dado de facción (D6) y reparte los puntos girando la rueda interna (Sol) y externa (Dioses).",
                "Si el SOL RADIANTE coincide con un Dios activo de tu facción: ¡Poder gratis sin coste y +3 tokens de Fe!"
            ]),
            ("6. ÉXODO B: EL MAR ROJO", [
                "- Casillas 1 a 19 (Torbellino): Avance = (D6 + Símbolos Divinos) - D12. Si es <= 0, puedes arriesgar con 1 cubo.",
                "- Casillas 20 a 30 (Mar Rojo): Se avanza de 1 en 1. Al llegar un 2º carro a la 20, ¡las aguas empiezan a cerrarse!",
                "- Cierre de Aguas: Carros < 21 son destruidos. Los sobrevivientes deben regresar a la casilla 20 para escapar.",
                "- Gana la facción con más carros salvados."
            ])
        ]

        y_offset = p_rect.y + 20 - self.rules_scroll
        for header, paras in rules_content:
            if p_rect.y - 30 <= y_offset <= p_rect.bottom + 20:
                h_s = font_rule_h.render(header, True, COLOR_GOLD)
                self.surface.blit(h_s, (p_rect.x + 25, y_offset))
            y_offset += 24

            for p in paras:
                if p_rect.y - 30 <= y_offset <= p_rect.bottom + 20:
                    p_s = font_rule_p.render(p, True, COLOR_PAPYRUS)
                    self.surface.blit(p_s, (p_rect.x + 35, y_offset))
                y_offset += 20
            y_offset += 12

        # Botón volver
        self.btn_rules_back.draw(self.surface)

    def _draw_game_over(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        fase = self.engine.board_state.fase_actual if self.engine else "FIN"
        is_victory = (fase == "VICTORIA")

        # Título
        font_big = FontManager.get_font(40, bold=True)
        title_txt = "¡¡VICTORIA EN EL ÉXODO!!" if is_victory else "DERROTA TOTAL"
        title_col = COLOR_GOLD_LIGHT if is_victory else COLOR_CRIMSON
        t_surf = font_big.render(title_txt, True, title_col)
        self.surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 80)))

        # Razón
        font_desc = FontManager.get_font(18)
        if is_victory and self.engine and self.engine.exodus_b_engine and self.engine.exodus_b_engine.winner_player:
            desc_txt = f"¡La facción victoriosa es: {self.engine.exodus_b_engine.winner_player.nombre_faccion}!"
        else:
            desc_txt = self.engine.game_over_reason if (self.engine and self.engine.game_over_reason) else "Egipto ha sucumbido ante el poder de las plagas y las aguas."

        d_surf = font_desc.render(desc_txt, True, COLOR_PAPYRUS)
        self.surface.blit(d_surf, d_surf.get_rect(center=(cx, cy - 20)))

        self.btn_game_over_back.draw(self.surface)
