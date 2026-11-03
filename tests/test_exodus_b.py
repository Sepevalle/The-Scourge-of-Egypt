"""
Pruebas del motor de la Fase Éxodo B (La Persecución en el Mar Rojo).
"""
import unittest
from scourge_egypt.models import BoardState, Player, Carro
from scourge_egypt.exodus_b_engine import ExodusBEngine


class TestExodusB(unittest.TestCase):
    def test_exodus_b_initialization(self):
        p1 = Player(id=1, nombre_faccion="Ra", color=(255, 0, 0), reserva_acolitos=3)
        p2 = Player(id=2, nombre_faccion="Seth", color=(0, 255, 0), reserva_acolitos=2)
        bs = BoardState()

        engine = ExodusBEngine(bs, [p1, p2])
        self.assertEqual(len(engine.players), 2)
        self.assertEqual(len(p1.carros_exodo_b), 3)
        self.assertEqual(len(p2.carros_exodo_b), 2)
        self.assertEqual(p1.carros_exodo_b[0].status, "en_carrera")
        self.assertEqual(p1.carros_exodo_b[0].position, 1)

    def test_water_closing_trigger(self):
        p1 = Player(id=1, nombre_faccion="Ra", color=(255, 0, 0), reserva_acolitos=2)
        p2 = Player(id=2, nombre_faccion="Seth", color=(0, 255, 0), reserva_acolitos=2)
        bs = BoardState()
        engine = ExodusBEngine(bs, [p1, p2])

        # Colocar un carro en 20 y otro en 20
        c1 = p1.carros_exodo_b[0]
        c1.position = 20
        c2 = p2.carros_exodo_b[0]
        c2.position = 20

        # Un tercer carro retrasado en casilla 15
        c3 = p1.carros_exodo_b[1]
        c3.status = "en_carrera"
        c3.position = 15

        engine._check_second_carro_reached_20(c2)
        self.assertTrue(bs.segundo_carro_en_20)
        # El carro retrasado en 15 (<21) debe ser destruido
        self.assertEqual(c3.status, "destruido")

    def test_sea_space_destruction(self):
        p1 = Player(id=1, nombre_faccion="Ra", color=(255, 0, 0), reserva_acolitos=1)
        bs = BoardState()
        engine = ExodusBEngine(bs, [p1])

        c1 = p1.carros_exodo_b[0]
        c1.position = 28
        engine.resolve_sea_choice(c1, "destroy_space")
        self.assertEqual(bs.casillas_activas_mar_rojo, 29)


if __name__ == "__main__":
    unittest.main()
