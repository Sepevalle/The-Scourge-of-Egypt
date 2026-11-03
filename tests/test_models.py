"""
Pruebas unitarias de modelos de datos y serialización.
"""
import unittest
from scourge_egypt.models import (
    Player, BoardState, ActionTile, Acolito, Carro, PlagueCard, GodCard, CommandmentCard, ItemCard, create_default_action_tiles
)


class TestModels(unittest.TestCase):
    def test_action_tiles_default(self):
        tiles = create_default_action_tiles()
        self.assertEqual(len(tiles), 8)
        names = [t.id_name for t in tiles]
        self.assertIn("COSECHAR", names)
        self.assertIn("REZAR", names)
        self.assertIn("GANADERIA", names)
        self.assertIn("REGADIOS", names)
        self.assertIn("RENACIMIENTO", names)
        self.assertIn("RECONSTRUCCION", names)
        self.assertIn("DIOSES_FAVORABLES", names)
        self.assertIn("RENDIR_PLEITESIA", names)

    def test_player_serialization(self):
        p = Player(
            id=1,
            nombre_faccion="Sacerdotes de Ra",
            color=(230, 160, 40),
            reserva_acolitos=6,
            tokens_fe=4
        )
        d = p.to_dict()
        p2 = Player.from_dict(d)
        self.assertEqual(p2.id, 1)
        self.assertEqual(p2.nombre_faccion, "Sacerdotes de Ra")
        self.assertEqual(p2.reserva_acolitos, 6)
        self.assertEqual(p2.tokens_fe, 4)
        self.assertEqual(len(p2.losetas_accion), 8)

    def test_board_state_serialization(self):
        bs = BoardState(
            ira_de_dios=25,
            cosechas={"trigo": 3, "avena": 5, "cebada": 1},
            ganado=18,
            viviendas=22
        )
        bs.bolsa_tumbas_egipcias.append(Acolito(player_id=1, faction_name="Ra"))
        bs.bolsa_almacenamiento_fe.append(1)

        d = bs.to_dict()
        bs2 = BoardState.from_dict(d)
        self.assertEqual(bs2.ira_de_dios, 25)
        self.assertEqual(bs2.cosechas["avena"], 5)
        self.assertEqual(len(bs2.bolsa_tumbas_egipcias), 1)
        self.assertEqual(bs2.bolsa_tumbas_egipcias[0].player_id, 1)
        self.assertEqual(len(bs2.bolsa_almacenamiento_fe), 1)

    def test_carro_model(self):
        c = Carro(player_id=2, carro_id=1, position=12, status="en_carrera")
        d = c.to_dict()
        c2 = Carro.from_dict(d)
        self.assertEqual(c2.position, 12)
        self.assertEqual(c2.status, "en_carrera")


if __name__ == "__main__":
    unittest.main()
