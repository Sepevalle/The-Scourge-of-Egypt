"""
Componentes interactivos de UI para Pygame:
Botones con hover, modales flotantes de decisión y panel de log con scroll.
"""
from __future__ import annotations
import pygame
from typing import Callable, Optional, List, Tuple
from scourge_egypt.ui.theme import (
    FontManager, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK,
    COLOR_BG_PANEL, COLOR_BG_CARD, COLOR_BG_DARK, COLOR_PAPYRUS,
    COLOR_CRIMSON, COLOR_WHITE, COLOR_GRAY, COLOR_GRAY_DARK, COLOR_BLACK
)
from scourge_egypt.ui.audio import SoundManager


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        on_click: Optional[Callable[[], None]] = None,
        font_size: int = 16,
        color_bg: Tuple[int, int, int] = COLOR_BG_CARD,
        color_hover: Tuple[int, int, int] = COLOR_GOLD_DARK,
        color_text: Tuple[int, int, int] = COLOR_GOLD_LIGHT,
        color_border: Tuple[int, int, int] = COLOR_GOLD,
        tooltip: str = ""
    ):
        self.rect = rect
        self.text = text
        self.on_click = on_click
        self.font_size = font_size
        self.color_bg = color_bg
        self.color_hover = color_hover
        self.color_text = color_text
        self.color_border = color_border
        self.tooltip = tooltip
        self.is_hovered: bool = False
        self.enabled: bool = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            self.is_hovered = False
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                SoundManager.get_instance().play("click")
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        if not self.enabled:
            bg_col = COLOR_GRAY_DARK
            border_col = COLOR_GRAY
            text_col = COLOR_GRAY
        elif self.is_hovered:
            bg_col = self.color_hover
            border_col = COLOR_GOLD_LIGHT
            text_col = COLOR_WHITE
        else:
            bg_col = self.color_bg
            border_col = self.color_border
            text_col = self.color_text

        # Fondo con bordes redondeados
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=6)

        # Texto centrado
        font = FontManager.get_font(self.font_size, bold=True)
        text_surf = font.render(self.text, True, text_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class ModalDialog:
    def __init__(
        self,
        title: str,
        message: str,
        options: List[str],
        on_select: Callable[[int], None],
        screen_size: Tuple[int, int] = (1280, 720),
        on_cancel: Optional[Callable[[], None]] = None
    ):
        self.title = title
        self.message = message
        self.options = options
        self.on_select = on_select
        self.on_cancel = on_cancel

        sw, sh = screen_size
        self.width = min(600, sw - 80)
        self.height = 240 + len(options) * 45
        self.rect = pygame.Rect((sw - self.width) // 2, (sh - self.height) // 2, self.width, self.height)

        self.buttons: List[Button] = []
        btn_w = self.width - 60
        btn_h = 36
        start_y = self.rect.y + 160

        for idx, opt in enumerate(options):
            b_rect = pygame.Rect(self.rect.x + 30, start_y + idx * 46, btn_w, btn_h)
            btn = Button(
                rect=b_rect,
                text=opt,
                on_click=lambda i=idx: self._handle_click(i),
                font_size=15,
                color_bg=COLOR_BG_CARD,
                color_hover=COLOR_GOLD_DARK,
                color_text=COLOR_GOLD_LIGHT
            )
            self.buttons.append(btn)

        self.cancel_button: Optional[Button] = None
        if on_cancel:
            cancel_rect = pygame.Rect(
                self.rect.centerx - 90,
                self.rect.bottom - 52,
                180,
                btn_h
            )
            self.cancel_button = Button(
                rect=cancel_rect,
                text="CANCELAR",
                on_click=self._handle_cancel,
                font_size=14,
                color_bg=COLOR_BG_CARD,
                color_hover=COLOR_CRIMSON,
                color_text=COLOR_PAPYRUS
            )

    def _handle_click(self, index: int):
        self.on_select(index)

    def _handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if (
            self.on_cancel
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            self._handle_cancel()
            return True

        # Bloquea clicks al fondo
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        if self.cancel_button and self.cancel_button.handle_event(event):
            return True
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return True  # Consume el evento
        return False

    def draw(self, surface: pygame.Surface):
        # Capa translúcida oscura de fondo
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Panel del modal
        pygame.draw.rect(surface, COLOR_BG_PANEL, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_GOLD, self.rect, width=3, border_radius=10)

        # Título
        font_title = FontManager.get_font(20, bold=True)
        t_surf = font_title.render(self.title, True, COLOR_GOLD_LIGHT)
        t_rect = t_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top + 20)
        surface.blit(t_surf, t_rect)

        # Mensaje (wrap de texto simple)
        font_msg = FontManager.get_font(15)
        words = self.message.split(" ")
        lines = []
        cur_line = ""
        for word in words:
            test_line = f"{cur_line} {word}".strip()
            if font_msg.size(test_line)[0] < self.width - 60:
                cur_line = test_line
            else:
                lines.append(cur_line)
                cur_line = word
        if cur_line:
            lines.append(cur_line)

        y_offset = self.rect.top + 60
        for line in lines:
            m_surf = font_msg.render(line, True, COLOR_PAPYRUS)
            m_rect = m_surf.get_rect(centerx=self.rect.centerx, top=y_offset)
            surface.blit(m_surf, m_rect)
            y_offset += 22

        # Botones de opciones
        for btn in self.buttons:
            btn.draw(surface)
        if self.cancel_button:
            self.cancel_button.draw(surface)


class GameLoggerUI:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.scroll_offset: int = 0
        self.line_height: int = 18
        self.font = FontManager.get_font(13)
        self.filters = ("TODO", "TURNOS", "ALERTAS", "CARTAS", "OTROS")
        self.active_filter = "TODO"
        self.filter_rects = {}
        x = rect.right - 390
        for label, width in zip(self.filters, (58, 68, 72, 66, 58)):
            self.filter_rects[label] = pygame.Rect(x, rect.y + 4, width, 18)
            x += width + 7

    @staticmethod
    def _category(message: str) -> str:
        lower = message.lower()
        if message.startswith("--- Turno") or "comienza la ronda" in lower or "fin de ronda" in lower:
            return "TURNOS"
        if "moisés revela:" in lower or lower.startswith("efecto:") or "mandamiento" in lower:
            return "CARTAS"
        alerts = ("derrota", "alerta", "aguas cerrándose", "destruida", "sacrifica", "sacrificio", "¡¡")
        if any(term in lower for term in alerts):
            return "ALERTAS"
        return "OTROS"

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(getattr(event, "pos", pygame.mouse.get_pos())):
                self.scroll_offset = max(0, self.scroll_offset - event.y * 2)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, filter_rect in self.filter_rects.items():
                if filter_rect.collidepoint(event.pos):
                    self.active_filter = label
                    self.scroll_offset = 0
                    break

    def draw(self, surface: pygame.Surface, messages: List[str]):
        # Fondo del logger
        pygame.draw.rect(surface, (15, 13, 18), self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, self.rect, width=1, border_radius=6)
        title = FontManager.get_font(11, bold=True).render("REGISTRO", True, COLOR_GOLD_LIGHT)
        surface.blit(title, (self.rect.x + 10, self.rect.y + 6))
        for label, filter_rect in self.filter_rects.items():
            selected = label == self.active_filter
            pygame.draw.rect(surface, COLOR_GOLD_DARK if selected else COLOR_BG_CARD, filter_rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_GOLD if selected else COLOR_GRAY_DARK, filter_rect, width=1, border_radius=5)
            label_surf = FontManager.get_font(9, bold=True).render(label, True, COLOR_WHITE if selected else COLOR_GRAY)
            surface.blit(label_surf, label_surf.get_rect(center=filter_rect.center))
        pygame.draw.line(surface, COLOR_GOLD_DARK, (self.rect.x + 8, self.rect.y + 25),
                         (self.rect.right - 8, self.rect.y + 25), 1)

        # Ajustar cada evento al ancho para conservar el mensaje completo.
        wrapped_messages = []
        max_width = self.rect.width - 36
        for message in messages:
            category = self._category(message)
            if self.active_filter != "TODO" and category != self.active_filter:
                continue
            current = ""
            for word in message.split():
                candidate = f"{current} {word}".strip()
                if self.font.size(candidate)[0] <= max_width:
                    current = candidate
                else:
                    if current:
                        wrapped_messages.append((current, category))
                    current = word
            if current:
                wrapped_messages.append((current, category))

        visible_lines = max(1, (self.rect.height - 34) // self.line_height)
        total_lines = len(wrapped_messages)

        # Ajuste de scroll: mantener abajo por defecto si el usuario no ha scrolleado arriba
        max_scroll = max(0, total_lines - visible_lines)
        offset = min(self.scroll_offset, max_scroll)

        start_idx = max(0, total_lines - visible_lines - offset)
        end_idx = min(total_lines, start_idx + visible_lines)

        y = self.rect.y + 29
        for msg, category in wrapped_messages[start_idx:end_idx]:
            # Color según contenido del mensaje
            col = COLOR_PAPYRUS
            if category == "ALERTAS":
                col = COLOR_CRIMSON
            elif category == "CARTAS" or "ÉXITO" in msg or "VICTORIA" in msg:
                col = COLOR_GOLD_LIGHT
            elif "Plaga" in msg or "Ira" in msg:
                col = (230, 140, 70)
            elif category == "TURNOS":
                col = (140, 190, 240)

            # Truncar texto si excede el ancho
            rendered_text = msg
            while self.font.size(rendered_text)[0] > self.rect.width - 24 and len(rendered_text) > 5:
                rendered_text = rendered_text[:-5] + "..."

            if category == "TURNOS":
                pygame.draw.rect(surface, (28, 31, 42),
                                 pygame.Rect(self.rect.x + 5, y - 1, self.rect.width - 15, self.line_height),
                                 border_radius=3)
            surf = self.font.render(rendered_text, True, col)
            surface.blit(surf, (self.rect.x + 10, y))
            y += self.line_height

        # Indicador de scroll si hay muchas líneas
        if max_scroll > 0:
            thumb_h = max(12, int((self.rect.height - 27) * (visible_lines / total_lines)))
            thumb_y = self.rect.y + 27 + int((self.rect.height - 27 - thumb_h) * (1.0 - (offset / max_scroll)))
            pygame.draw.rect(surface, COLOR_GOLD_DARK, (self.rect.right - 8, thumb_y, 5, thumb_h), border_radius=2)


class CardDetailDialog:
    """Vista ampliada y desplazable para consultar la descripción completa de una carta."""

    def __init__(self, card, screen_size=(1280, 720), history=None):
        self.history = history or [{"card": card, "turn": 0, "round": 0, "faction": ""}]
        self.history_index = max(
            0,
            next((i for i, entry in enumerate(self.history) if entry.get("card") is card), len(self.history) - 1),
        )
        self.card = self.history[self.history_index].get("card", card)
        sw, sh = screen_size
        self.rect = pygame.Rect(0, 0, min(860, sw - 80), min(610, sh - 60))
        self.rect.center = (sw // 2, sh // 2)
        self.scroll_offset = 0
        self.font_title = FontManager.get_font(23, bold=True)
        self.font_body = FontManager.get_font(17)
        self.font_hint = FontManager.get_font(12)
        self.btn_close = Button(
            pygame.Rect(self.rect.right - 154, self.rect.bottom - 54, 130, 36),
            "CERRAR",
            on_click=self.close,
            font_size=13,
        )
        self.btn_previous = Button(
            pygame.Rect(self.rect.x + 28, self.rect.bottom - 54, 142, 36),
            "← ANTERIOR",
            on_click=lambda: self._move_history(-1),
            font_size=12,
        )
        self.btn_next = Button(
            pygame.Rect(self.rect.x + 182, self.rect.bottom - 54, 142, 36),
            "SIGUIENTE →",
            on_click=lambda: self._move_history(1),
            font_size=12,
        )
        self.closed = False

    def _move_history(self, offset):
        self.history_index = max(0, min(len(self.history) - 1, self.history_index + offset))
        self.card = self.history[self.history_index].get("card", self.card)
        self.scroll_offset = 0

    def close(self):
        self.closed = True

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.close()
            return True
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, self.scroll_offset - event.y * 3)
            return True
        self.btn_previous.enabled = self.history_index > 0
        self.btn_next.enabled = self.history_index < len(self.history) - 1
        if self.btn_previous.handle_event(event) or self.btn_next.handle_event(event):
            return True
        if self.btn_close.handle_event(event):
            return True
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return True
        return False

    def _wrap_description(self, max_width):
        lines = []
        for paragraph in str(getattr(self.card, "description", "")).splitlines() or [""]:
            if not paragraph.strip():
                lines.append("")
                continue
            current = ""
            for word in paragraph.split():
                candidate = f"{current} {word}".strip()
                if self.font_body.size(candidate)[0] <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def _affected_resources(self):
        text = str(getattr(self.card, "description", "")).lower()
        groups = [
            (("ira", "plaga", "tinieblas", "fuego"), "IRA / PLAGAS"),
            (("trigo", "avena", "cebada", "cosecha", "cultivo", "hambruna"), "COSECHAS"),
            (("ganado", "vaca", "oveja", "animal"), "GANADO"),
            (("vivienda", "casa", "poblacion", "población"), "VIVIENDAS"),
            (("acolito", "acólito", "sacrificio", "tumba"), "ACÓLITOS"),
            (("fe", "bolsa azul"), "FE"),
            (("carro", "mar rojo", "agua"), "ÉXODO B"),
            (("mandamiento", "ley", "moises", "moisés"), "MANDAMIENTOS"),
        ]
        labels = [label for terms, label in groups if any(term in text for term in terms)]
        return labels or ["EFECTO DESCRITO EN LA CARTA"]

    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        surface.blit(overlay, (0, 0))
        pygame.draw.rect(surface, COLOR_BG_PANEL, self.rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_GOLD, self.rect, width=3, border_radius=12)

        card_type_raw = str(getattr(self.card, "card_type", "carta")).lower()
        card_type = card_type_raw.upper()
        type_colors = {
            "plaga": COLOR_CRIMSON,
            "personaje": COLOR_LAPIS_LIGHT,
            "evento": COLOR_GOLD,
            "edificio": COLOR_EMERALD,
        }
        name = str(getattr(self.card, "name", "Carta de Moisés"))
        badge = self.font_hint.render(card_type, True, type_colors.get(card_type_raw, COLOR_GOLD_LIGHT))
        surface.blit(badge, (self.rect.x + 28, self.rect.y + 22))
        title = self.font_title.render(name, True, COLOR_WHITE)
        surface.blit(title, (self.rect.x + 28, self.rect.y + 46))
        record = self.history[self.history_index]
        context = (
            f"CARTA {self.history_index + 1}/{len(self.history)} · "
            f"Ronda {record.get('round', '?')} · Turno {record.get('turn', '?')} · {record.get('faction', '')}"
        )
        context_surf = self.font_hint.render(context, True, COLOR_GRAY_LIGHT)
        context_surf_rect = context_surf.get_rect(right=self.rect.right - 28, centery=self.rect.y + 32)
        surface.blit(context_surf, context_surf_rect)

        resource_labels = self._affected_resources()
        resource_caption = self.font_hint.render("RECURSOS:", True, COLOR_GOLD_LIGHT)
        surface.blit(resource_caption, (self.rect.x + 28, self.rect.y + 88))
        chip_x = self.rect.x + 104
        chip_y = self.rect.y + 85
        for label in resource_labels:
            chip_font = FontManager.get_font(10, bold=True)
            chip_text = chip_font.render(label, True, COLOR_PAPYRUS)
            chip = pygame.Rect(chip_x, chip_y, chip_text.get_width() + 18, 19)
            pygame.draw.rect(surface, COLOR_BG_CARD, chip, border_radius=5)
            pygame.draw.rect(surface, COLOR_GOLD_DARK, chip, width=1, border_radius=5)
            surface.blit(chip_text, (chip.x + 9, chip.y + 3))
            chip_x = chip.right + 7

        divider_y = self.rect.y + 112
        pygame.draw.line(surface, COLOR_GOLD_DARK,
                         (self.rect.x + 26, divider_y),
                         (self.rect.right - 26, divider_y), 1)

        consequence_label = self.font_hint.render("CONSECUENCIA", True, COLOR_GOLD_LIGHT)
        surface.blit(consequence_label, (self.rect.x + 28, self.rect.y + 118))
        content = pygame.Rect(self.rect.x + 28, self.rect.y + 140,
                              self.rect.width - 56, self.rect.height - 214)
        lines = self._wrap_description(content.width)
        line_height = 25
        visible_count = max(1, content.height // line_height)
        max_scroll = max(0, len(lines) - visible_count)
        self.scroll_offset = min(self.scroll_offset, max_scroll)
        old_clip = surface.get_clip()
        surface.set_clip(content)
        y = content.y
        for line in lines[self.scroll_offset:self.scroll_offset + visible_count]:
            if line:
                surface.blit(self.font_body.render(line, True, COLOR_PAPYRUS), (content.x, y))
            y += line_height
        surface.set_clip(old_clip)

        if max_scroll:
            track = pygame.Rect(content.right - 5, content.y, 4, content.height)
            pygame.draw.rect(surface, COLOR_BG_CARD, track, border_radius=2)
            thumb_h = max(24, int(content.height * visible_count / len(lines)))
            thumb_y = track.y + int((track.height - thumb_h) * self.scroll_offset / max_scroll)
            pygame.draw.rect(surface, COLOR_GOLD, (track.x, thumb_y, track.width, thumb_h), border_radius=2)

        hint = self.font_hint.render("Rueda del ratón para desplazarte · Esc para cerrar", True, COLOR_GRAY)
        surface.blit(hint, (self.rect.x + 28, self.rect.bottom - 74))
        self.btn_previous.enabled = self.history_index > 0
        self.btn_next.enabled = self.history_index < len(self.history) - 1
        self.btn_previous.draw(surface)
        self.btn_next.draw(surface)
        self.btn_close.draw(surface)
