"""
Pruebas de la capa gráfica e integración de pantallas en modo headless.
"""
import unittest
import os
import pygame

# Forzar driver dummy para tests headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scourge_egypt.ui.theme import SCREEN_WIDTH, SCREEN_HEIGHT
from scourge_egypt.ui.game_screen import ScreenManager


class TestUIHeadless(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        cls.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_screen_manager_render_menu(self):
        sm = ScreenManager(self.surface)
        sm.draw()
        self.assertEqual(sm.current_screen, "MENU")

    def test_screen_manager_render_game_and_b(self):
        sm = ScreenManager(self.surface)
        sm.start_new_game()
        self.assertEqual(sm.current_screen, "GAME")
        sm.update()
        sm.draw()

        # Probar robar carta
        sm._on_draw_moses()
        sm.draw()

        # Probar forzar transición a Éxodo B y renderizar vista
        sm.engine.board_state.viviendas = 10
        sm.engine.board_state.bolsa_almacenamiento_fe = [1] * 30
        sm.engine._evaluate_exodus_a_transition()
        self.assertTrue(sm.engine.is_in_exodus_b)
        sm.draw()

    def test_rules_screen_back_button(self):
        sm = ScreenManager(self.surface)
        sm.set_screen("RULES")
        self.assertEqual(sm.current_screen, "RULES")
        sm.draw()

        # Simular click en el botón Volver al Menú
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": sm.btn_rules_back.rect.center}
        )
        sm.handle_event(click_event)
        self.assertEqual(sm.current_screen, "MENU")

    def test_game_over_back_button(self):
        sm = ScreenManager(self.surface)
        sm.set_screen("GAME_OVER")
        self.assertEqual(sm.current_screen, "GAME_OVER")
        sm.draw()

        # Simular click en el botón Volver al Menú
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": sm.btn_game_over_back.rect.center}
        )
        sm.handle_event(click_event)
        self.assertEqual(sm.current_screen, "MENU")

    def test_tutorial_screen_navigation_and_demos(self):
        sm = ScreenManager(self.surface)

        # 1. Click en botón tutorial del menú
        click_tutorial = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": sm.btn_tutorial.rect.center}
        )
        sm.handle_event(click_tutorial)
        self.assertEqual(sm.current_screen, "TUTORIAL")

        tut = sm.tutorial_screen
        self.assertEqual(tut.current_lesson, 1)
        sm.draw()

        # 2. Navegar por todas las lecciones 1 a 6
        for lesson in range(2, 7):
            tut.set_lesson(lesson)
            self.assertEqual(tut.current_lesson, lesson)
            tut.update()
            sm.draw()

        # 3. Probar botones de navegación next / prev
        tut.set_lesson(3)
        tut.prev_lesson()
        self.assertEqual(tut.current_lesson, 2)
        tut.next_lesson()
        self.assertEqual(tut.current_lesson, 3)

        # 4. Probar demos interactivos
        # Demo Lección 2 (Cosechas)
        prev_crop = tut.demo_trigo
        tut._demo_inc_crop()
        self.assertEqual(tut.demo_trigo, prev_crop + 2)
        tut._demo_dec_crop()
        self.assertEqual(tut.demo_trigo, prev_crop)

        # Demo Lección 3 (Sangre)
        prev_ira = tut.demo_ira
        tut._demo_sangre_ira()
        self.assertEqual(tut.demo_ira, prev_ira + 2)

        # Demo Lección 4 (Loseta)
        tut._demo_use_rezar()
        self.assertTrue(tut.demo_tile_used)
        tut._demo_reset_tile()
        self.assertFalse(tut.demo_tile_used)

        # Demo Lección 5 (Rueda Solar)
        tut._demo_spin_solar_wheel()

        # Demo Lección 6 (Carro en el Mar Rojo)
        tut._demo_roll_race()

        # 5. Volver al menú desde el tutorial
        click_back = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": tut.btn_menu.rect.center}
        )
        tut.handle_event(click_back)
        self.assertEqual(sm.current_screen, "MENU")

    def test_procedural_icons(self):
        """Verifica que todos los iconos procedurales se rendericen correctamente."""
        import scourge_egypt.ui.icons as icons
        surface = pygame.Surface((200, 200))
        color = (255, 215, 0)
        center = (100, 100)
        size = 15

        # Probar cada funcion de icono
        icon_funcs = [
            icons.draw_icon_flame,
            icons.draw_icon_wheat,
            icons.draw_icon_cow,
            icons.draw_icon_house,
            icons.draw_icon_pray,
            icons.draw_icon_person,
            icons.draw_icon_dice,
            icons.draw_icon_water,
            icons.draw_icon_sun,
            icons.draw_icon_ankh,
            icons.draw_icon_scroll,
            icons.draw_icon_chariot,
            icons.draw_icon_star,
            icons.draw_icon_skull,
            icons.draw_icon_bag,
            icons.draw_icon_eye_of_horus,
        ]

        for func in icon_funcs:
            surface.fill((0, 0, 0))
            func(surface, center, size, color)

        # Probar dispatchers
        for name in icons.TILE_ICON_MAP.keys():
            icons.draw_tile_icon(surface, name, center, size, color)

        for ctype in icons.CARD_TYPE_ICON_MAP.keys():
            icons.draw_card_type_icon(surface, ctype, center, size, color)


if __name__ == "__main__":
    unittest.main()
