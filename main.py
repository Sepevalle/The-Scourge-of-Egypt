# /// script
# dependencies = ["pygame-ce", "numpy"]
# ///
"""
Punto de entrada principal para The Scourge of Egypt en Pygame.
Ejecuta el bucle de juego, gestiona eventos y renderiza la interfaz gráfica.
"""
from __future__ import annotations
import asyncio
import sys
import os
import numpy
import pygame

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scourge_egypt.ui.theme import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from scourge_egypt.ui.game_screen import ScreenManager
from scourge_egypt.ui.audio import SoundManager


def run_smoke_test():
    """Ejecuta una simulación completa sin ventana gráfica para pruebas automatizadas."""
    print("=== INICIANDO SMOKE TEST DE THE SCOURGE OF EGYPT ===")
    from scourge_egypt.game_engine import GameEngine
    engine = GameEngine(num_players=2)
    engine.start_turn()

    # 1. Robar carta de Moisés
    card = engine.draw_moses_card()
    print(f"Carta de Moisés robada con éxito: {card.name}")

    if engine.pending_choice:
        engine.resolve_choice(0)
        print("Decisión de plaga resuelta correctamente.")

    # 2. Usar loseta
    idx = next(i for i, t in enumerate(engine.current_player.losetas_accion) if t.id_name == "REZAR")
    engine.use_action_tile(idx)
    print(f"Loseta REZAR ejecutada. Ira actual: {engine.board_state.ira_de_dios}")

    # 3. Rueda solar
    res = engine.roll_solar_wheel()
    print(f"Rueda solar ejecutada: {res['inner_symbol']} con {res['outer_god']}")

    # 4. Finalizar turno
    engine.end_turn()
    print(f"Turno finalizado. Nuevo jugador activo: {engine.current_player.nombre_faccion}")
    print("=== SMOKE TEST COMPLETADO CON ÉXITO ===")


async def main():
    if "--smoke-test" in sys.argv or "--test" in sys.argv:
        run_smoke_test()
        return

    pygame.init()
    pygame.font.init()

    # Configuración de ventana
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("The Scourge of Egypt - Plagas, Faraón y el Mar Rojo")

    # Icono de ventana (generar superficie dorada con jeroglífico estilizado)
    icon_surf = pygame.Surface((32, 32))
    icon_surf.fill((20, 18, 24))
    pygame.draw.circle(icon_surf, (225, 175, 55), (16, 16), 14, width=2)
    pygame.draw.circle(icon_surf, (245, 210, 115), (16, 16), 6)
    pygame.display.set_icon(icon_surf)

    clock = pygame.time.Clock()
    screen_manager = ScreenManager(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                screen_manager.handle_event(event)

        screen_manager.update()
        screen_manager.draw()
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv or "--test" in sys.argv:
        run_smoke_test()
    else:
        asyncio.run(main())
