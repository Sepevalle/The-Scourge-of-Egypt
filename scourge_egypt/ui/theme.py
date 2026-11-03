"""
Definición de tema visual, colores y tipografías para The Scourge of Egypt.
Inspirado en la iconografía, oro, lapislázuli y papiro del Antiguo Egipto.
"""
from __future__ import annotations
import pygame
from typing import Tuple, Dict

# Dimensiones base recomendadas
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Paleta de Colores
COLOR_BG_DARK = (18, 16, 22)             # Obsidiana oscura
COLOR_BG_PANEL = (30, 26, 36)            # Fondo de paneles
COLOR_BG_CARD = (42, 36, 50)             # Fondo de cartas
COLOR_BG_INPUT = (22, 20, 28)

COLOR_GOLD = (225, 175, 55)              # Oro faraónico
COLOR_GOLD_LIGHT = (245, 210, 115)        # Oro brillante
COLOR_GOLD_DARK = (155, 110, 25)         # Bronce / Oro viejo

COLOR_LAPIS = (35, 85, 165)              # Lapislázuli
COLOR_LAPIS_LIGHT = (65, 130, 225)       # Lapislázuli claro
COLOR_LAPIS_DARK = (20, 50, 105)

COLOR_PAPYRUS = (235, 220, 185)          # Papiro
COLOR_PAPYRUS_DARK = (195, 175, 140)

COLOR_CRIMSON = (190, 45, 55)            # Carmesí / Sangre
COLOR_CRIMSON_DARK = (125, 25, 30)

COLOR_EMERALD = (35, 160, 95)            # Verde Nilo / Esmeralda
COLOR_SAND = (210, 180, 135)             # Arena del desierto
COLOR_BLUE_SEA = (25, 105, 180)          # Mar Rojo abierto
COLOR_BLUE_DEEP = (10, 50, 100)          # Aguas profundas

COLOR_WHITE = (250, 250, 252)
COLOR_GRAY_LIGHT = (180, 180, 190)
COLOR_GRAY = (120, 120, 130)
COLOR_GRAY_DARK = (60, 60, 70)
COLOR_BLACK = (0, 0, 0)

# Fuentes
class FontManager:
    _fonts: Dict[str, pygame.font.Font] = {}

    @classmethod
    def get_font(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = f"{size}_{bold}"
        if key not in cls._fonts:
            try:
                # Intentar cargar fuentes elegantes disponibles en Windows
                system_fonts = ["segoeui", "calibri", "arial", "georgia"]
                font_name = pygame.font.match_font(system_fonts[0], bold=bold)
                if font_name:
                    cls._fonts[key] = pygame.font.Font(font_name, size)
                else:
                    cls._fonts[key] = pygame.font.SysFont("Arial", size, bold=bold)
            except Exception:
                cls._fonts[key] = pygame.font.SysFont(None, size, bold=bold)
        return cls._fonts[key]
