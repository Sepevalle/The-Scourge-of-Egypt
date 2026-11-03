"""
Pruebas del motor central de juego (GameEngine).
"""
import unittest
import os
from scourge_egypt.game_engine import GameEngine
from scourge_egypt.models import PlagueCard
from scourge_egypt.save_load import save_game_to_file, load_game_from_file


class TestGameEngine(unittest.TestCase):
    def test_engine_init(self):
        engine = GameEngine(num_players=2)
        self.assertEqual(len(engine.players), 2)
        self.assertEqual(engine.board_state.ganado, 20)
        self.assertEqual(engine.board_state.viviendas, 25)
        self.assertEqual(engine.turn_number, 1)

    def test_action_tiles(self):
        engine = GameEngine(num_players=2)
        p = engine.current_player

        # Probar COSECHAR
        engine.board_state.cosechas["trigo"] = 4
        # Buscar tile COSECHAR
        idx = next(i for i, t in enumerate(p.losetas_accion) if t.id_name == "COSECHAR")
        res = engine.use_action_tile(idx, "trigo")
        self.assertTrue(res)
        self.assertEqual(engine.board_state.cosechas["trigo"], 2)
        self.assertEqual(p.losetas_accion[idx].state, "usada_boca_abajo")

        # Probar REZAR
        engine.board_state.ira_de_dios = 6
        idx_rezar = next(i for i, t in enumerate(p.losetas_accion) if t.id_name == "REZAR")
        res = engine.use_action_tile(idx_rezar)
        self.assertTrue(res)
        self.assertEqual(engine.board_state.ira_de_dios, 4)

    def test_sangre_plague_choice(self):
        engine = GameEngine(num_players=2)
        # Inyectar carta de plaga de sangre
        card = PlagueCard(
            id="test_sangre", name="Plaga de Sangre", card_type="plaga",
            description="", plague_type="sangre", potency_base=2
        )
        engine._resolve_plague(card)
        self.assertIsNotNone(engine.pending_choice)
        self.assertEqual(engine.pending_choice["type"], "sangre_choice")

        # Elegir opción 0: Aumentar Ira
        prev_ira = engine.board_state.ira_de_dios
        engine.resolve_choice(0)
        self.assertEqual(engine.board_state.ira_de_dios, prev_ira + 2)
        self.assertIsNone(engine.pending_choice)

    def test_save_and_load(self):
        engine = GameEngine(num_players=3)
        engine.board_state.ira_de_dios = 15
        engine.current_player.tokens_fe = 7
        save_file = "test_partida.json"

        saved = save_game_to_file(engine, save_file)
        self.assertTrue(saved)
        self.assertTrue(os.path.exists(save_file))

        loaded = load_game_from_file(save_file)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.num_players, 3)
        self.assertEqual(loaded.board_state.ira_de_dios, 15)
        self.assertEqual(loaded.players[0].tokens_fe, 7)

        if os.path.exists(save_file):
            os.remove(save_file)


if __name__ == "__main__":
    unittest.main()
