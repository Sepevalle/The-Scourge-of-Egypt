"""
Pantalla interactiva de Tutoriales para The Scourge of Egypt.
Guía paso a paso al jugador desde 0, dividida en 6 lecciones temáticas
con explicaciones claras, diagramas visuales y demostraciones prácticas interactivas.
"""
from __future__ import annotations
import math
import random
import pygame
from typing import Callable, List, Dict, Any, Optional
from scourge_egypt.ui.theme import (
    FontManager, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG_DARK, COLOR_BG_PANEL, COLOR_BG_CARD,
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_LAPIS, COLOR_LAPIS_LIGHT, COLOR_PAPYRUS,
    COLOR_CRIMSON, COLOR_CRIMSON_DARK, COLOR_EMERALD,
    COLOR_WHITE, COLOR_GRAY, COLOR_GRAY_DARK, COLOR_BLACK, COLOR_GRAY_LIGHT,
    COLOR_BLUE_SEA, COLOR_BLUE_DEEP
)
from scourge_egypt.ui.components import Button
from scourge_egypt.ui.solar_wheel_ui import SolarWheelUI
from scourge_egypt.ui.audio import SoundManager


class TutorialScreen:
    def __init__(self, surface: pygame.Surface, on_exit: Callable[[], None]):
        self.surface = surface
        self.on_exit = on_exit
        self.current_lesson: int = 1
        self.total_lessons: int = 6

        # Fuentes
        self.font_title = FontManager.get_font(22, bold=True)
        self.font_h2 = FontManager.get_font(16, bold=True)
        self.font_body = FontManager.get_font(13)
        self.font_small = FontManager.get_font(11)
        self.font_tip = FontManager.get_font(12, bold=True)

        # Botones de navegación inferior
        cx = SCREEN_WIDTH // 2
        self.btn_prev = Button(
            rect=pygame.Rect(60, SCREEN_HEIGHT - 65, 170, 42),
            text="← ANTERIOR",
            on_click=self.prev_lesson,
            font_size=13
        )
        self.btn_next = Button(
            rect=pygame.Rect(SCREEN_WIDTH - 230, SCREEN_HEIGHT - 65, 170, 42),
            text="SIGUIENTE →",
            on_click=self.next_lesson,
            font_size=13,
            color_bg=COLOR_GOLD_DARK,
            color_hover=COLOR_GOLD
        )
        self.btn_menu = Button(
            rect=pygame.Rect(cx - 90, SCREEN_HEIGHT - 65, 180, 42),
            text="VOLVER AL MENÚ",
            on_click=self.on_exit,
            font_size=13
        )

        # Botones de salto rápido de lección (pestañas superiores)
        self.lesson_tabs: List[Button] = []
        tab_w = 170
        for i in range(1, 7):
            bx = 60 + (i - 1) * (tab_w + 10)
            btn = Button(
                rect=pygame.Rect(bx, 68, tab_w, 32),
                text=f"Lección {i}",
                on_click=lambda num=i: self.set_lesson(num),
                font_size=12
            )
            self.lesson_tabs.append(btn)

        # -------------------------------------------------------------
        # VARIABLES PARA DEMOSTRACIONES PRÁCTICAS INTERACTIVAS
        # -------------------------------------------------------------
        # Demo Lección 2: Simulador de Cosechas
        self.demo_trigo: int = 4
        self.btn_demo_add_crop = Button(
            rect=pygame.Rect(785, 300, 198, 38),
            text="+2 Hambruna",
            on_click=self._demo_inc_crop,
            font_size=12,
            color_bg=COLOR_CRIMSON_DARK,
            color_hover=COLOR_CRIMSON
        )
        self.btn_demo_sub_crop = Button(
            rect=pygame.Rect(997, 300, 198, 38),
            text="Usar 'Cosechar' (-2)",
            on_click=self._demo_dec_crop,
            font_size=12,
            color_bg=COLOR_EMERALD,
            color_hover=(50, 190, 120)
        )

        # Demo Lección 3: Simulador de Plaga de Sangre
        self.demo_ira: int = 18
        self.demo_acolitos: int = 5
        self.btn_demo_sangre_ira = Button(
            rect=pygame.Rect(785, 335, 198, 40),
            text="Aumentar Ira (+2)",
            on_click=self._demo_sangre_ira,
            font_size=12
        )
        self.btn_demo_sangre_sac = Button(
            rect=pygame.Rect(997, 335, 198, 40),
            text="Sacrificar 2 Acólitos",
            on_click=self._demo_sangre_sac,
            font_size=12,
            color_bg=COLOR_CRIMSON_DARK,
            color_hover=COLOR_CRIMSON
        )

        # Demo Lección 4: Loseta activa interactiva
        self.demo_tile_used: bool = False
        self.demo_fe: int = 3
        self.btn_demo_use_tile = Button(
            rect=pygame.Rect(785, 335, 198, 40),
            text="Pulsar 'Rezar' (-2 Ira)",
            on_click=self._demo_use_rezar,
            font_size=12
        )
        self.btn_demo_reset_round = Button(
            rect=pygame.Rect(997, 335, 198, 40),
            text="Terminar Ronda (Reactivar)",
            on_click=self._demo_reset_tile,
            font_size=12,
            color_bg=COLOR_BG_CARD,
            color_hover=COLOR_LAPIS
        )

        # Demo Lección 5: Rueda Solar interactiva
        self.demo_wheel = SolarWheelUI(center=(990, 255), radius=68)
        self.demo_wheel.inner_radius = 40
        self.btn_demo_spin_wheel = Button(
            rect=pygame.Rect(830, 365, 320, 40),
            text="Lanzar Dado D6 (Girar Rueda)",
            on_click=self._demo_spin_solar_wheel,
            font_size=12
        )
        self.demo_wheel_msg: str = "Tira el dado para buscar alineación sagrada."

        # Demo Lección 6: Simulador de Carro en el Mar Rojo
        self.demo_carro_pos: int = 15
        self.demo_last_roll: str = "Sin tirada"
        self.btn_demo_roll_race = Button(
            rect=pygame.Rect(830, 280, 320, 40),
            text="Lanzar D6 + D12 Moisés",
            on_click=self._demo_roll_race,
            font_size=12
        )

    # -------------------------------------------------------------
    # MÉTODOS DE NAVEGACIÓN
    # -------------------------------------------------------------
    def set_lesson(self, num: int):
        self.current_lesson = max(1, min(self.total_lessons, num))
        SoundManager.get_instance().play("click")

    def prev_lesson(self):
        if self.current_lesson > 1:
            self.set_lesson(self.current_lesson - 1)

    def next_lesson(self):
        if self.current_lesson < self.total_lessons:
            self.set_lesson(self.current_lesson + 1)
        else:
            self.on_exit()

    # -------------------------------------------------------------
    # EVENTOS DE INTERACCIÓN DE DEMOS
    # -------------------------------------------------------------
    def _demo_inc_crop(self):
        self.demo_trigo = min(10, self.demo_trigo + 2)
        SoundManager.get_instance().play("alert" if self.demo_trigo >= 5 else "click")

    def _demo_dec_crop(self):
        self.demo_trigo = max(0, self.demo_trigo - 2)
        SoundManager.get_instance().play("click")

    def _demo_sangre_ira(self):
        self.demo_ira = min(50, self.demo_ira + 2)
        SoundManager.get_instance().play("click")

    def _demo_sangre_sac(self):
        if self.demo_acolitos >= 2:
            self.demo_acolitos -= 2
            SoundManager.get_instance().play("gong")

    def _demo_use_rezar(self):
        if not self.demo_tile_used:
            self.demo_tile_used = True
            self.demo_ira = max(0, self.demo_ira - 2)
            SoundManager.get_instance().play("click")

    def _demo_reset_tile(self):
        self.demo_tile_used = False
        SoundManager.get_instance().play("card")

    def _demo_spin_solar_wheel(self):
        d6 = random.randint(1, 6)
        in_steps = d6 // 2
        out_steps = d6 - in_steps
        new_in = (self.demo_wheel.current_inner_idx + in_steps) % 4
        new_out = (self.demo_wheel.current_outer_idx + out_steps) % 8
        self.demo_wheel.update_indices(new_in, new_out)
        SoundManager.get_instance().play("dice")

        god_names = ["Ra", "Seth", "Osiris", "Horus", "Isis", "Anubis", "Thoth", "Hathor"]
        in_names = ["SOL RADIANTE", "ECLIPSE", "SOL NACIENTE", "SOL PONIENTE"]
        in_sym = in_names[new_in]
        out_god = god_names[new_out]

        if in_sym == "SOL RADIANTE" and out_god in ("Ra", "Osiris"):
            self.demo_wheel_msg = f"¡¡ALINEACIÓN CON {out_god}!! Poder gratis + 3 Fe."
            SoundManager.get_instance().play("fanfare")
        else:
            self.demo_wheel_msg = f"D6={d6}: {in_sym} con {out_god}. Sin alineación."

    def _demo_roll_race(self):
        d6 = random.randint(1, 6)
        d12 = random.randint(1, 12)
        god_symb = 2  # Simulado
        total = d6 + god_symb
        advance = total - d12
        SoundManager.get_instance().play("dice")

        if advance > 0:
            self.demo_carro_pos = min(30, self.demo_carro_pos + (1 if self.demo_carro_pos >= 20 else advance))
            self.demo_last_roll = f"D6={d6} + Divinidad(2) vs D12={d12} => +{advance} casillas."
        else:
            self.demo_last_roll = f"D6={d6} + Divinidad(2) vs D12={d12} => {advance} (Detenido / Arriesgar)."

    # -------------------------------------------------------------
    # EVENTOS Y DIBUJADO
    # -------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        # Botones de navegación
        self.btn_prev.handle_event(event)
        self.btn_next.handle_event(event)
        self.btn_menu.handle_event(event)

        for tab in self.lesson_tabs:
            tab.handle_event(event)

        # Botones de interacción según lección activa
        if self.current_lesson == 2:
            self.btn_demo_add_crop.handle_event(event)
            self.btn_demo_sub_crop.handle_event(event)
        elif self.current_lesson == 3:
            self.btn_demo_sangre_ira.handle_event(event)
            self.btn_demo_sangre_sac.handle_event(event)
        elif self.current_lesson == 4:
            self.btn_demo_use_tile.handle_event(event)
            self.btn_demo_reset_round.handle_event(event)
        elif self.current_lesson == 5:
            self.btn_demo_spin_wheel.handle_event(event)
        elif self.current_lesson == 6:
            self.btn_demo_roll_race.handle_event(event)

    def update(self):
        if self.current_lesson == 5:
            self.demo_wheel.update()

    def draw(self):
        self.surface.fill(COLOR_BG_DARK)

        # 1. Cabecera del tutorial
        self._draw_header()

        # 2. Pestañas de lecciones
        for idx, tab in enumerate(self.lesson_tabs, start=1):
            tab.color_bg = COLOR_GOLD_DARK if idx == self.current_lesson else COLOR_BG_CARD
            tab.color_text = COLOR_GOLD_LIGHT if idx == self.current_lesson else COLOR_PAPYRUS
            tab.draw(self.surface)

        # 3. Panel de contenido dividido (Izquierda: Explicación, Derecha: Sandbox interactivo)
        panel_left = pygame.Rect(60, 115, 680, 480)
        panel_right = pygame.Rect(760, 115, 460, 480)

        pygame.draw.rect(self.surface, COLOR_BG_PANEL, panel_left, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, panel_left, width=2, border_radius=8)

        pygame.draw.rect(self.surface, (24, 20, 30), panel_right, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_GOLD, panel_right, width=2, border_radius=8)

        # 4. Renderizar contenido específico de la lección
        if self.current_lesson == 1:
            self._draw_lesson_1(panel_left, panel_right)
        elif self.current_lesson == 2:
            self._draw_lesson_2(panel_left, panel_right)
        elif self.current_lesson == 3:
            self._draw_lesson_3(panel_left, panel_right)
        elif self.current_lesson == 4:
            self._draw_lesson_4(panel_left, panel_right)
        elif self.current_lesson == 5:
            self._draw_lesson_5(panel_left, panel_right)
        elif self.current_lesson == 6:
            self._draw_lesson_6(panel_left, panel_right)

        # 5. Botones inferiores
        self.btn_prev.enabled = (self.current_lesson > 1)
        self.btn_prev.draw(self.surface)
        self.btn_menu.draw(self.surface)
        self.btn_next.text = "FINALIZAR TUTORIAL" if self.current_lesson == self.total_lessons else "SIGUIENTE →"
        self.btn_next.draw(self.surface)

    def _draw_header(self):
        cx = SCREEN_WIDTH // 2
        t_surf = self.font_title.render("ACADEMIA DEL FARAÓN: TUTORIAL PASO A PASO", True, COLOR_GOLD_LIGHT)
        self.surface.blit(t_surf, t_surf.get_rect(center=(cx, 32)))

    # -------------------------------------------------------------
    # CONTENIDOS DE CADA LECCIÓN
    # -------------------------------------------------------------
    def _draw_lesson_1(self, left: pygame.Rect, right: pygame.Rect):
        # Texto izquierda
        t = self.font_h2.render("LECCIÓN 1: ¿DE QUÉ TRATA EL JUEGO?", True, COLOR_GOLD_LIGHT)
        left_x = left.x + 25
        left_y = left.y + 20
        self.surface.blit(t, (left_x, left_y))

        paragraphs = [
            "¡Bienvenido, líder sacerdotal del Antiguo Egipto! En este juego te pones al mando",
            "de una de las cinco grandes facciones que rinden culto a los dioses:",
            "  • Sacerdotes de Ra | Servidores de Seth | Discípulos de Osiris",
            "  • Seguidores de Horus | Novicios de Isis",
            "",
            "El juego se divide en DOS GRANDES ACTOS:",
            "1. ÉXODO A (Las Plagas Bíblicas):",
            "   Moisés y la cólera divina azotan Egipto. Tu objetivo cooperativo es evitar que",
            "   Egipto colapse (si se destruyen todas las viviendas o la Fe comunitaria es",
            "   insuficiente, ¡todos los jugadores pierden!). Pero a la vez debes proteger a tus",
            "   propios acólitos: el jugador que más acólitos sacrifique será eliminado.",
            "",
            "2. ÉXODO B (La Persecución en el Mar Rojo):",
            "   Las facciones supervivientes se convierten en carros de combate y compiten",
            "   a toda velocidad en un circuito de 30 casillas antes de que las aguas colapsen.",
            "",
            "¿Cómo se gana la partida?",
            "Sobreviviendo al Éxodo A y logrando rescatar el mayor número de carros con vida",
            "de vuelta a la casilla 20 en el Éxodo B."
        ]

        cur_y = left_y + 35
        for line in paragraphs:
            col = COLOR_GOLD if line.startswith("1.") or line.startswith("2.") or line.startswith("¿Cómo") else COLOR_PAPYRUS
            surf = self.font_body.render(line, True, col)
            self.surface.blit(surf, (left_x, cur_y))
            cur_y += 20

        # Panel derecha (Diagrama visual)
        self._draw_box_header(right, "ESTRUCTURA DE LA PARTIDA")
        # Visual de los 2 actos
        b1 = pygame.Rect(right.x + 30, right.y + 70, right.width - 60, 150)
        pygame.draw.rect(self.surface, (35, 25, 45), b1, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_CRIMSON, b1, width=2, border_radius=6)
        self.surface.blit(self.font_h2.render("ACTO 1: ÉXODO A", True, COLOR_GOLD_LIGHT), (b1.x + 15, b1.y + 12))
        self.surface.blit(self.font_small.render("- Tablero global con 10 plagas", True, COLOR_PAPYRUS), (b1.x + 15, b1.y + 40))
        self.surface.blit(self.font_small.render("- Gestión de Cosechas, Ganado y Viviendas", True, COLOR_PAPYRUS), (b1.x + 15, b1.y + 60))
        self.surface.blit(self.font_small.render("- Donar Fe a la Bolsa Azul comunitaria", True, COLOR_PAPYRUS), (b1.x + 15, b1.y + 80))
        self.surface.blit(self.font_small.render("- Acumular los 10 Mandamientos de Moisés", True, COLOR_PAPYRUS), (b1.x + 15, b1.y + 100))
        self.surface.blit(self.font_small.render("- Sobrevivir al recuento de la Bolsa Negra", True, (240, 120, 120)), (b1.x + 15, b1.y + 120))

        b2 = pygame.Rect(right.x + 30, right.y + 250, right.width - 60, 150)
        pygame.draw.rect(self.surface, (15, 35, 60), b2, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_BLUE_SEA, b2, width=2, border_radius=6)
        self.surface.blit(self.font_h2.render("ACTO 2: ÉXODO B", True, (160, 210, 255)), (b2.x + 15, b2.y + 12))
        self.surface.blit(self.font_small.render("- Circuito de 30 casillas (Mar Rojo)", True, COLOR_PAPYRUS), (b2.x + 15, b2.y + 40))
        self.surface.blit(self.font_small.render("- Tus acólitos se convierten en Carros", True, COLOR_PAPYRUS), (b2.x + 15, b2.y + 60))
        self.surface.blit(self.font_small.render("- Tiradas de combate: D6 + Dioses vs D12", True, COLOR_PAPYRUS), (b2.x + 15, b2.y + 80))
        self.surface.blit(self.font_small.render("- ¡Cierre de aguas engulle a los rezagados!", True, (240, 120, 120)), (b2.x + 15, b2.y + 100))
        self.surface.blit(self.font_small.render("- Huida a la casilla 20 para la victoria", True, COLOR_GOLD_LIGHT), (b2.x + 15, b2.y + 120))

    def _draw_lesson_2(self, left: pygame.Rect, right: pygame.Rect):
        t = self.font_h2.render("LECCIÓN 2: RECURSOS CRÍTICOS Y BOLSAS SAGRADAS", True, COLOR_GOLD_LIGHT)
        left_x = left.x + 25
        left_y = left.y + 20
        self.surface.blit(t, (left_x, left_y))

        lines = [
            "En el Éxodo A debes vigilar 5 elementos clave del tablero:",
            "",
            "1. IRA DE DIOS [0..50]:",
            "   Aumenta cuando las plagas golpean. En 20 puntos se activa el 1º Rayo (+1 de potencia)",
            "   y en 40 puntos el 2º Rayo (+2 de potencia a todas las plagas). ¡Reza para bajarla!",
            "",
            "2. COSECHAS (Trigo, Avena, Cebada) [0..10]:",
            "   Avanzan hacia la derecha. Si superan la posición 5, entran en ALERTA DE HAMBRUNA.",
            "   Si alcanzan 10, hay AGOTAMIENTO TOTAL y se destruye 1 ganado automáticamente.",
            "",
            "3. GANADO Y VIVIENDAS:",
            "   El ganado alimenta a tus gentes. Las viviendas protegen a la población.",
            "   ¡PELIGRO!: Si las viviendas llegan a 0, la partida termina en DERROTA inmediata.",
            "",
            "4. BOLSA NEGRA (Tumbas Egipcias):",
            "   Aquí van a parar los acólitos y ganado sacrificados. Al final del Éxodo A, ¡el",
            "   jugador que tenga más acólitos en la bolsa es ELIMINADO de la partida!",
            "",
            "5. BOLSA AZUL (Almacenamiento de Fe):",
            "   Los jugadores deben donar fichas de Fe aquí. Se exige un mínimo conjunto",
            "   (15, 25, 35 o 45 según el nº de jugadores). Si no se alcanza, ¡todos pierden!"
        ]

        cur_y = left_y + 35
        for line in lines:
            col = COLOR_GOLD_LIGHT if any(line.startswith(p) for p in ["1.", "2.", "3.", "4.", "5."]) else COLOR_PAPYRUS
            surf = self.font_body.render(line, True, col)
            self.surface.blit(surf, (left_x, cur_y))
            cur_y += 20

        # Panel derecha (Simulador de Cosechas)
        self._draw_box_header(right, "SIMULADOR PRÁCTICO: COSECHAS")
        c_x = right.x + 25
        c_y = right.y + 60
        self.surface.blit(self.font_h2.render(f"Track de Trigo: {self.demo_trigo}/10", True, COLOR_GOLD_LIGHT), (c_x, c_y))

        # Barra visual
        bar_w = right.width - 50
        bar_rect = pygame.Rect(c_x, c_y + 30, bar_w, 24)
        pygame.draw.rect(self.surface, (20, 18, 24), bar_rect, border_radius=4)

        # Relleno
        fill_w = int(bar_w * (self.demo_trigo / 10.0))
        if fill_w > 0:
            fill_rect = pygame.Rect(c_x, c_y + 30, fill_w, 24)
            col = COLOR_CRIMSON if self.demo_trigo >= 10 else ((230, 140, 40) if self.demo_trigo >= 5 else COLOR_EMERALD)
            pygame.draw.rect(self.surface, col, fill_rect, border_radius=4)
        pygame.draw.rect(self.surface, COLOR_GOLD, bar_rect, width=2, border_radius=4)

        # Marcador línea 5 y 10
        x5 = c_x + int(bar_w * 0.5)
        pygame.draw.line(self.surface, COLOR_WHITE, (x5, c_y + 25), (x5, c_y + 58), 2)
        self.surface.blit(self.font_small.render("Alerta (5)", True, (240, 180, 80)), (x5 - 20, c_y + 60))

        # Estado del trigo
        st_txt = "¡AGOTAMIENTO! Se destruye 1 ganado." if self.demo_trigo >= 10 else ("¡Alerta de Hambruna!" if self.demo_trigo >= 5 else "Cosecha segura y próspera.")
        st_col = COLOR_CRIMSON if self.demo_trigo >= 10 else ((230, 140, 40) if self.demo_trigo >= 5 else COLOR_EMERALD)
        self.surface.blit(self.font_h2.render(st_txt, True, st_col), (c_x, c_y + 90))

        # Botones interactivos (situados en y = 300)
        self.btn_demo_add_crop.draw(self.surface)
        self.btn_demo_sub_crop.draw(self.surface)

        # Consejo
        tip_rect = pygame.Rect(c_x, c_y + 195, bar_w, 140)
        pygame.draw.rect(self.surface, (30, 25, 40), tip_rect, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, tip_rect, width=1, border_radius=6)
        self.surface.blit(self.font_tip.render("CONSEJO DEL FARAÓN:", True, COLOR_GOLD), (tip_rect.x + 15, tip_rect.y + 12))
        self.surface.blit(self.font_small.render("• El trigo, avena y cebada avanzan con las plagas hacia 10.", True, COLOR_PAPYRUS), (tip_rect.x + 15, tip_rect.y + 38))
        self.surface.blit(self.font_small.render("• Si superan 5, entran en ALERTA DE HAMBRUNA.", True, (240, 180, 80)), (tip_rect.x + 15, tip_rect.y + 60))
        self.surface.blit(self.font_small.render("• En 10 (AGOTAMIENTO), se destruye 1 cubo de ganado.", True, (240, 120, 120)), (tip_rect.x + 15, tip_rect.y + 82))
        self.surface.blit(self.font_small.render("• Usa la loseta COSECHAR para aliviar la hambruna a tiempo.", True, COLOR_GOLD_LIGHT), (tip_rect.x + 15, tip_rect.y + 106))

    def _draw_lesson_3(self, left: pygame.Rect, right: pygame.Rect):
        t = self.font_h2.render("LECCIÓN 3: EL FLUJO DE TURNO Y LAS PLAGAS", True, COLOR_GOLD_LIGHT)
        left_x = left.x + 25
        left_y = left.y + 20
        self.surface.blit(t, (left_x, left_y))

        lines = [
            "Cada turno de un jugador se estructura en fases muy claras:",
            "",
            "1. ROBAR CARTA DE MOISÉS:",
            "   Al inicio de tu turno, pulsas el botón dorado 'Robar Carta de Moisés'.",
            "   Puede ser una Plaga, un Personaje Bíblico, un Evento o un Edificio Mítico.",
            "",
            "2. RESOLVER EL EFECTO / DECISIÓN:",
            "   • Plaga de Sangre: Debes decidir entre aumentar la Ira de Dios (+2)",
            "     o sacrificar acólitos de tu facción.",
            "   • Ranas / Langostas: Voltean 3 losetas de acción e incrementan cosechas.",
            "   • Úlceras: Compara el poder de Ra y Seth; si gana Seth, todos sacrifican.",
            "   • Granizo: Una tirada destruye viviendas. ¡Cuidado de no quedarte sin casas!",
            "   • Tinieblas: Bloquea el uso de dioses durante 3 turnos.",
            "",
            "3. EL ALTAR DE LOS MANDAMIENTOS:",
            "   Las cartas con símbolo de las tablas sagradas colocan un cubo blanco en el altar.",
            "   Al reunir 5 CUBOS BLANCOS:",
            "   - Se desbloquea un Mandamiento Sagrado (I al X) con una regla global.",
            "   - El meeple de Moisés avanza 1 casilla en el track de números romanos.",
            "   - ¡Cuando Moisés llega a la casilla X, el Éxodo A TERMINA!"
        ]

        cur_y = left_y + 35
        for line in lines:
            col = COLOR_GOLD_LIGHT if any(line.startswith(p) for p in ["1.", "2.", "3."]) else COLOR_PAPYRUS
            surf = self.font_body.render(line, True, col)
            self.surface.blit(surf, (left_x, cur_y))
            cur_y += 20

        # Panel derecha (Simulador de Decisión de Sangre)
        self._draw_box_header(right, "SIMULADOR: DECISIÓN DE SANGRE")
        c_x = right.x + 25
        c_y = right.y + 55

        card_box = pygame.Rect(c_x, c_y, right.width - 50, 155)
        pygame.draw.rect(self.surface, COLOR_BG_CARD, card_box, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_CRIMSON, card_box, width=2, border_radius=6)

        self.surface.blit(self.font_h2.render("PLAGA DE SANGRE", True, COLOR_CRIMSON), (card_box.x + 15, card_box.y + 12))
        self.surface.blit(self.font_body.render("El Nilo se tiñe de rojo. Elige una opción:", True, COLOR_PAPYRUS), (card_box.x + 15, card_box.y + 38))
        self.surface.blit(self.font_small.render("Opción A: Aumentar la Ira de Dios (+2).", True, (240, 160, 80)), (card_box.x + 15, card_box.y + 64))
        self.surface.blit(self.font_small.render("Opción B: Sacrificar 2 acólitos a la Bolsa Negra.", True, (240, 120, 120)), (card_box.x + 15, card_box.y + 84))

        stats_txt = f"Ira actual: {self.demo_ira}/50  |  Tus Acólitos: {self.demo_acolitos}"
        self.surface.blit(self.font_h2.render(stats_txt, True, COLOR_GOLD_LIGHT), (card_box.x + 15, card_box.y + 118))

        # Botones de decisión interactivos (a y = 335)
        self.btn_demo_sangre_ira.draw(self.surface)
        self.btn_demo_sangre_sac.draw(self.surface)

        # Explicación / Consejo (a y = 390)
        exp_rect = pygame.Rect(c_x, c_y + 200, right.width - 50, 150)
        pygame.draw.rect(self.surface, (30, 25, 40), exp_rect, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, exp_rect, width=1, border_radius=6)
        self.surface.blit(self.font_tip.render("CONSEJO ANTE LAS PLAGAS:", True, COLOR_GOLD), (exp_rect.x + 15, exp_rect.y + 12))
        self.surface.blit(self.font_small.render("• Si aumentas la Ira, aceleras la potencia de futuras plagas", True, COLOR_PAPYRUS), (exp_rect.x + 15, exp_rect.y + 38))
        self.surface.blit(self.font_small.render("  (alcanzando los 20 y 40 puntos para los Rayos Divinos).", True, (240, 180, 80)), (exp_rect.x + 15, exp_rect.y + 58))
        self.surface.blit(self.font_small.render("• Si sacrificas acólitos, te arriesgas a ser ELIMINADO en el", True, COLOR_PAPYRUS), (exp_rect.x + 15, exp_rect.y + 82))
        self.surface.blit(self.font_small.render("  recuento final de la Bolsa Negra al culminar el Éxodo A.", True, (240, 120, 120)), (exp_rect.x + 15, exp_rect.y + 102))

    def _draw_lesson_4(self, left: pygame.Rect, right: pygame.Rect):
        t = self.font_h2.render("LECCIÓN 4: LAS 8 LOSETAS DE ACCIÓN Y LOS DIOSES", True, COLOR_GOLD_LIGHT)
        left_x = left.x + 25
        left_y = left.y + 20
        self.surface.blit(t, (left_x, left_y))

        lines = [
            "Tras robar la carta de Moisés, tienes hasta 4 ACCIONES DE LOSETA por turno.",
            "Cada jugador cuenta con 8 losetas básicas:",
            "  1. COSECHAR: -2 a un track de cereal para frenar la hambruna.",
            "  2. REZAR: -2 a la Ira de Dios para aplacar la cólera.",
            "  3. GANADERÍA: +2 cubos a la reserva de ganado.",
            "  4. REGADÍOS: Paga 1 Fe para obtener +1 acción de loseta extra este turno.",
            "  5. RENACIMIENTO: +2 acólitos a tu reserva personal.",
            "  6. RECONSTRUCCIÓN: +2 viviendas a la reserva global comunitaria.",
            "  7. DIOSES FAVORABLES: +1 relanzamiento de dados para cualquier tirada.",
            "  8. RENDIR PLEITESÍA: +2 fichas de Fe personales.",
            "",
            "Estados de las Losetas:",
            "• ACTIVA (Dorado): Puedes usarla haciendo clic sobre ella.",
            "• USADA (Oscura): Se voltea boca abajo. ¡Se reactiva al terminar la ronda!",
            "• DESTRUIDA (Roja): Inutilizable salvo milagro de Josué.",
            "",
            "Además puedes:",
            "• DONAR 1 FE: Aporta fichas a la Bolsa Azul para cumplir el objetivo colectivo.",
            "• INVOCAR DIOS (2 Fe): Obtén cartas de Ra, Seth, Osiris, etc., con grandes poderes."
        ]

        cur_y = left_y + 35
        for line in lines:
            col = COLOR_GOLD_LIGHT if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "• ACTIVA", "• DONAR", "• INVOCAR")) else COLOR_PAPYRUS
            surf = self.font_body.render(line, True, col)
            self.surface.blit(surf, (left_x, cur_y))
            cur_y += 18

        # Panel derecha (Simulador de Loseta)
        self._draw_box_header(right, "SIMULADOR: USO DE LOSETA")
        c_x = right.x + 25
        c_y = right.y + 55

        # Tarjeta visual de la loseta REZAR
        t_box = pygame.Rect(c_x, c_y, right.width - 50, 150)
        bg_col = (25, 23, 28) if self.demo_tile_used else COLOR_BG_CARD
        border_col = COLOR_GRAY_DARK if self.demo_tile_used else COLOR_GOLD
        pygame.draw.rect(self.surface, bg_col, t_box, border_radius=6)
        pygame.draw.rect(self.surface, border_col, t_box, width=2, border_radius=6)

        st_title = "ESTADO: USADA (BOCA ABAJO)" if self.demo_tile_used else "ESTADO: ACTIVA (DISPONIBLE)"
        st_tcol = COLOR_GRAY if self.demo_tile_used else COLOR_GOLD_LIGHT
        self.surface.blit(self.font_h2.render("LOSETA: REZAR (1 Ra / 1 Seth)", True, st_tcol), (t_box.x + 15, t_box.y + 14))
        self.surface.blit(self.font_body.render(st_title, True, (240, 180, 80)), (t_box.x + 15, t_box.y + 42))
        self.surface.blit(self.font_small.render("Efecto: Reduce la Ira de Dios en 2 puntos.", True, COLOR_PAPYRUS), (t_box.x + 15, t_box.y + 70))

        ira_info = f"Ira de Dios simulada: {self.demo_ira}/50"
        self.surface.blit(self.font_h2.render(ira_info, True, COLOR_CRIMSON if self.demo_ira >= 20 else COLOR_EMERALD), (t_box.x + 15, t_box.y + 110))

        # Botones interactivos (situados DEBAJO de t_box, en y = 335)
        self.btn_demo_use_tile.draw(self.surface)
        self.btn_demo_reset_round.draw(self.surface)

        # Nota / Consejo
        note_rect = pygame.Rect(c_x, c_y + 195, right.width - 50, 150)
        pygame.draw.rect(self.surface, (30, 25, 40), note_rect, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, note_rect, width=1, border_radius=6)
        self.surface.blit(self.font_tip.render("CONSEJO DE ACCIONES:", True, COLOR_GOLD), (note_rect.x + 15, note_rect.y + 12))
        self.surface.blit(self.font_small.render("• Cada turno dispones de hasta 4 acciones de loseta.", True, COLOR_PAPYRUS), (note_rect.x + 15, note_rect.y + 38))
        self.surface.blit(self.font_small.render("• Al usar una loseta se voltea a 'USADA' (boca abajo).", True, (240, 180, 80)), (note_rect.x + 15, note_rect.y + 60))
        self.surface.blit(self.font_small.render("• Permanece inactiva hasta que todos finalizan su turno.", True, COLOR_PAPYRUS), (note_rect.x + 15, note_rect.y + 82))
        self.surface.blit(self.font_small.render("• Pulsa 'Terminar Ronda' para reactivarla de nuevo.", True, COLOR_GOLD_LIGHT), (note_rect.x + 15, note_rect.y + 106))

    def _draw_lesson_5(self, left: pygame.Rect, right: pygame.Rect):
        t = self.font_h2.render("LECCIÓN 5: LA GRACIA DEL FARAÓN (RUEDA SOLAR)", True, COLOR_GOLD_LIGHT)
        left_x = left.x + 25
        left_y = left.y + 20
        self.surface.blit(t, (left_x, left_y))

        lines = [
            "Al final de tu turno puedes acceder al ritual sagrado de la Rueda Solar.",
            "",
            "¿Cómo funciona la Rueda Solar?",
            "Consta de DOS CÍRCULOS CONCÉNTRICOS:",
            "  • Anillo Interior (4 estados del Sol): SOL RADIANTE, Eclipse, Sol Naciente, Sol Poniente.",
            "  • Anillo Exterior (8 Dioses Egipcios): Ra, Seth, Osiris, Horus, Isis, Anubis, Thoth, Hathor.",
            "",
            "El Lanzamiento de la Gracia del Faraón:",
            "1. Tiras tu dado de facción (D6).",
            "2. El número obtenido hace girar ambos anillos en sentido horario.",
            "3. En la parte superior (marcador sagrado a las 12 horas) se comprueba qué símbolo",
            "   del Sol queda alineado con qué Dios.",
            "",
            "¡EL GRAN PREMIO DE ALINEACIÓN SAGRADA!",
            "Si el marcador superior marca SOL RADIANTE y el Dios alineado está ACTIVO en tu facción:",
            "  ★ ¡Activas el poder especial de ese Dios COMPLETAMENTE GRATIS (sin pagar Fe)!",
            "  ★ ¡Recibes además una recompensa de +3 FICHAS DE FE personales!",
            "",
            "¡Es una de las mejores formas de recuperar acólitos, sanar cosechas y ganar Fe!"
        ]

        cur_y = left_y + 35
        for line in lines:
            col = COLOR_GOLD_LIGHT if "¡EL GRAN PREMIO" in line or line.startswith("  ★") else COLOR_PAPYRUS
            surf = self.font_body.render(line, True, col)
            self.surface.blit(surf, (left_x, cur_y))
            cur_y += 19

        # Panel derecha (Rueda Solar Interactiva)
        self._draw_box_header(right, "SIMULADOR: RUEDA SOLAR")
        # Dibuja rueda simulada centrada
        self.demo_wheel.center = (right.centerx, right.y + 140)
        self.demo_wheel.radius = 68
        self.demo_wheel.inner_radius = 40
        self.demo_wheel.draw(self.surface, ["Ra", "Osiris"])
        self.btn_demo_spin_wheel.draw(self.surface)

        # Cuadro de resultado y consejo
        res_rect = pygame.Rect(right.x + 25, right.y + 300, right.width - 50, 165)
        pygame.draw.rect(self.surface, (30, 25, 40), res_rect, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, res_rect, width=1, border_radius=6)
        self.surface.blit(self.font_h2.render(self.demo_wheel_msg, True, COLOR_GOLD_LIGHT), (res_rect.x + 15, res_rect.y + 12))
        self.surface.blit(self.font_tip.render("CONSEJO DEL RITUAL SOLAR:", True, COLOR_GOLD), (res_rect.x + 15, res_rect.y + 45))
        self.surface.blit(self.font_small.render("• El dado D6 hace girar el Sol (interior) y Dioses (exterior).", True, COLOR_PAPYRUS), (res_rect.x + 15, res_rect.y + 72))
        self.surface.blit(self.font_small.render("• Si el Sol Radiante coincide con un Dios activo de tu facción:", True, COLOR_PAPYRUS), (res_rect.x + 15, res_rect.y + 94))
        self.surface.blit(self.font_small.render("  ¡Activas su poder especial GRATIS y ganas +3 Fe!", True, (140, 230, 160)), (res_rect.x + 15, res_rect.y + 118))

    def _draw_lesson_6(self, left: pygame.Rect, right: pygame.Rect):
        t = self.font_h2.render("LECCIÓN 6: EL FIN DE ÉXODO A Y LA CARRERA EN EL MAR ROJO", True, COLOR_GOLD_LIGHT)
        left_x = left.x + 25
        left_y = left.y + 20
        self.surface.blit(t, (left_x, left_y))

        lines = [
            "Cuando Moisés alcanza el Mandamiento X, finaliza el Éxodo A.",
            "El motor evalúa de inmediato:",
            "  1. ¿Quedan viviendas? Si viviendas <= 0: DERROTA inmediata.",
            "  2. ¿Hay suficiente Fe en la Bolsa Azul? Si falta Fe: DERROTA colectiva.",
            "  3. Recuento de la Bolsa Negra: ¡Quien tenga más acólitos sacrificados es",
            "     ELIMINADO de la partida (salvo quien posea el edificio Portal Seguro)!",
            "",
            "LOS SUPERVIVIENTES PASAN A ÉXODO B (El Mar Rojo):",
            "Tus acólitos se transforman en Carros de Guerra sobre un circuito de 30 casillas:",
            "• Fase 1: Torbellino de Fuego (Casillas 1 a 19):",
            "  Tiras Dado D6 + Símbolos Divinos vs Dado D12 Moisés.",
            "  Si el resultado es positivo, avanzas. Si es negativo o 0, te detienes o puedes",
            "  arriesgar gastando 1 cubo (si la carta robada no tiene Ira, ¡el carro se destruye!).",
            "",
            "• Fase 2: El Mar Rojo (Casillas 20 a 30):",
            "  Al pisar la casilla 20 puedes meter un 2º carro en juego.",
            "  ¡CIERRE DE AGUAS!: Cuando un 2º carro pisa la casilla 20, las aguas colapsan y",
            "  todos los carros rezagados (que no hayan llegado a la 21) se ahogan.",
            "",
            "• Huida: Los carros deben dar la vuelta y escapar de vuelta a la casilla 20.",
            "  ¡Gana la facción con más carros salvados!"
        ]

        cur_y = left_y + 35
        for line in lines:
            col = COLOR_GOLD_LIGHT if "LOS SUPERVIVIENTES" in line or line.startswith(("• Fase", "• Huida")) else COLOR_PAPYRUS
            surf = self.font_body.render(line, True, col)
            self.surface.blit(surf, (left_x, cur_y))
            cur_y += 18

        # Panel derecha (Simulador del Mar Rojo)
        self._draw_box_header(right, "SIMULADOR: PERSECUCIÓN")
        c_x = right.x + 25
        c_y = right.y + 55

        # Mini circuito visual
        self.surface.blit(self.font_h2.render(f"Posición de tu Carro: Casilla {self.demo_carro_pos}/30", True, COLOR_GOLD_LIGHT), (c_x, c_y))

        # Dibujar casillas
        box_w = (right.width - 50) // 10
        by = c_y + 32
        for i in range(1, 11):
            cell_idx = (self.demo_carro_pos - 5 + i)
            cell_idx = max(1, min(30, cell_idx))
            bx = c_x + (i - 1) * box_w
            b_r = pygame.Rect(bx, by, box_w - 4, 32)

            is_sea = (cell_idx >= 20)
            is_carro = (cell_idx == self.demo_carro_pos)

            b_col = COLOR_LAPIS if is_sea else (45, 30, 20)
            pygame.draw.rect(self.surface, b_col, b_r, border_radius=4)
            pygame.draw.rect(self.surface, COLOR_GOLD if is_carro else COLOR_GRAY, b_r, width=2 if is_carro else 1, border_radius=4)

            num_s = self.font_small.render(str(cell_idx), True, COLOR_WHITE)
            self.surface.blit(num_s, (bx + 3, by + 2))

            if is_carro:
                pygame.draw.circle(self.surface, COLOR_GOLD_LIGHT, (bx + box_w // 2 - 2, by + 18), 5)

        # Último tiro
        self.surface.blit(self.font_small.render(self.demo_last_roll, True, (240, 200, 100)), (c_x, by + 40))

        # Botón tirar
        self.btn_demo_roll_race.draw(self.surface)

        # Resumen final
        res_rect = pygame.Rect(c_x, c_y + 170, right.width - 50, 175)
        pygame.draw.rect(self.surface, (25, 20, 35), res_rect, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_GOLD_DARK, res_rect, width=1, border_radius=6)
        self.surface.blit(self.font_tip.render("¡LISTO PARA LA PERSECUCIÓN EN EL MAR ROJO!", True, COLOR_GOLD_LIGHT), (res_rect.x + 15, res_rect.y + 12))
        self.surface.blit(self.font_small.render("• Casillas 1-19 (Torbellino): D6 + Divinidad - D12.", True, COLOR_PAPYRUS), (res_rect.x + 15, res_rect.y + 38))
        self.surface.blit(self.font_small.render("• Si el avance es <= 0, puedes arriesgar gastando 1 cubo.", True, (240, 180, 80)), (res_rect.x + 15, res_rect.y + 58))
        self.surface.blit(self.font_small.render("• Casilla 20: Entrada al Mar Rojo (avance de 1 en 1).", True, COLOR_PAPYRUS), (res_rect.x + 15, res_rect.y + 78))
        self.surface.blit(self.font_small.render("• ¡Cierre de Aguas!: Al llegar un 2º carro a la 20, todos los", True, (240, 120, 120)), (res_rect.x + 15, res_rect.y + 98))
        self.surface.blit(self.font_small.render("  carros rezagados (< 21) son destruidos de inmediato.", True, (240, 120, 120)), (res_rect.x + 15, res_rect.y + 118))
        self.surface.blit(self.font_small.render("• Huida: Regresar con vida a la casilla 20 para ganar.", True, (140, 230, 160)), (res_rect.x + 15, res_rect.y + 142))

    def _draw_box_header(self, rect: pygame.Rect, title: str):
        h_surf = self.font_h2.render(title, True, COLOR_GOLD_LIGHT)
        self.surface.blit(h_surf, (rect.x + 20, rect.y + 18))
        pygame.draw.line(self.surface, COLOR_GOLD_DARK, (rect.x + 20, rect.y + 42), (rect.right - 20, rect.y + 42), 1)
