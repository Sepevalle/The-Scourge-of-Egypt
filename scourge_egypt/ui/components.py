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
        self.line_height: int = 20
        self.font = FontManager.get_font(13)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, self.scroll_offset - event.y * 2)

    def draw(self, surface: pygame.Surface, messages: List[str]):
        # Fondo del logger
        pygame.draw.rect(surface, (15, 13, 18), self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD_DARK, self.rect, width=1, border_radius=6)

        visible_lines = (self.rect.height - 12) // self.line_height
        total_lines = len(messages)

        # Ajuste de scroll: mantener abajo por defecto si el usuario no ha scrolleado arriba
        max_scroll = max(0, total_lines - visible_lines)
        offset = min(self.scroll_offset, max_scroll)

        start_idx = max(0, total_lines - visible_lines - offset)
        end_idx = min(total_lines, start_idx + visible_lines)

        y = self.rect.y + 6
        for msg in messages[start_idx:end_idx]:
            # Color según contenido del mensaje
            col = COLOR_PAPYRUS
            if "¡¡" in msg or "DERROTA" in msg or "ALERTA" in msg:
                col = COLOR_CRIMSON
            elif "ÉXITO" in msg or "VICTORIA" in msg or "MANDAMIENTO" in msg:
                col = COLOR_GOLD_LIGHT
            elif "Plaga" in msg or "Ira" in msg:
                col = (230, 140, 70)
            elif "Turno" in msg or "Ronda" in msg:
                col = (140, 190, 240)

            # Truncar texto si excede el ancho
            rendered_text = msg
            while self.font.size(rendered_text)[0] > self.rect.width - 24 and len(rendered_text) > 5:
                rendered_text = rendered_text[:-5] + "..."

            surf = self.font.render(rendered_text, True, col)
            surface.blit(surf, (self.rect.x + 10, y))
            y += self.line_height

        # Indicador de scroll si hay muchas líneas
        if max_scroll > 0:
            thumb_h = max(15, int(self.rect.height * (visible_lines / total_lines)))
            thumb_y = self.rect.y + int((self.rect.height - thumb_h) * (1.0 - (offset / max_scroll)))
            pygame.draw.rect(surface, COLOR_GOLD_DARK, (self.rect.right - 8, thumb_y, 5, thumb_h), border_radius=2)
