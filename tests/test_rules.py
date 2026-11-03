"""
Pruebas unitarias de algoritmos de reglas y validaciones.
"""
import unittest
from scourge_egypt.models import BoardState, Player, Acolito, GodCard
from scourge_egypt.rules import (
    get_potenciacion, check_famine_and_exhaustion, sacrifice_acolytes,
    sacrifice_cattle, destroy_houses, add_faith_to_blue_bag,
    check_commandments_progress, resolve_solar_wheel, verificar_condiciones_exodo_a
)


class TestRules(unittest.TestCase):
    def test_potenciacion_thresholds(self):
        self.assertEqual(get_potenciacion(0), 0)
        self.assertEqual(get_potenciacion(19), 0)
        self.assertEqual(get_potenciacion(20), 1)
        self.assertEqual(get_potenciacion(39), 1)
        self.assertEqual(get_potenciacion(40), 2)
        self.assertEqual(get_potenciacion(50), 2)

    def test_sacrifices_and_bags(self):
        bs = BoardState(ganado=10, viviendas=15)
        p = Player(id=1, nombre_faccion="Ra", color=(255, 200, 0), reserva_acolitos=5, tokens_fe=4)

        # Sacrificar acólitos
        sac = sacrifice_acolytes(p, bs, 2)
        self.assertEqual(sac, 2)
        self.assertEqual(p.reserva_acolitos, 3)
        self.assertEqual(len(bs.bolsa_tumbas_egipcias), 2)

        # Donar fe a bolsa azul
        donated = add_faith_to_blue_bag(p, bs, 3)
        self.assertEqual(donated, 3)
        self.assertEqual(p.tokens_fe, 1)
        self.assertEqual(len(bs.bolsa_almacenamiento_fe), 3)

        # Destruir casas y ganado
        destroy_houses(bs, 4)
        self.assertEqual(bs.viviendas, 11)
        sacrifice_cattle(bs, 2)
        self.assertEqual(bs.ganado, 8)
        self.assertEqual(len(bs.bolsa_tumbas_egipcias), 4)

    def test_famine_checks(self):
        bs = BoardState(ganado=5, cosechas={"trigo": 5, "avena": 10, "cebada": 2})
        logs = check_famine_and_exhaustion(bs)
        self.assertTrue(any("Aviso de hambruna en TRIGO" in m for m in logs))
        self.assertTrue(any("AGOTAMIENTO TOTAL" in m for m in logs))
        self.assertEqual(bs.ganado, 4)  # Perdió 1 ganado por agotamiento

    def test_commandment_accumulation(self):
        bs = BoardState(cubos_mandamiento=4, mandamiento_actual=1)
        triggered, num = check_commandments_progress(bs)
        self.assertFalse(triggered)

        bs.cubos_mandamiento = 5
        triggered, num = check_commandments_progress(bs)
        self.assertTrue(triggered)
        self.assertEqual(num, 1)
        self.assertEqual(bs.cubos_mandamiento, 0)
        self.assertEqual(bs.mandamiento_actual, 2)

    def test_solar_wheel_alignment(self):
        p = Player(id=1, nombre_faccion="Ra", color=(255, 200, 0))
        god_ra = GodCard(id="g_ra", name="Ra", card_type="divinidad", description="", god_name="Ra")
        p.dioses_activos.append(god_ra)

        # inner: 0 ("SOL RADIANTE"), outer: 0 ("Ra")
        # Si parte de inner 0 y outer 0, con tirada 0 (o roll_total = 4, 0 inner, 0 outer con mod)
        res = resolve_solar_wheel(
            roll_total=4,
            inner_steps=0,
            outer_steps=4,
            current_inner=0,
            current_outer=4,
            player=p
        )
        # inner remains 0 (SOL RADIANTE), outer = (4 + 4) % 8 = 0 (Ra)
        self.assertTrue(res["success"])
        self.assertEqual(res["inner_symbol"], "SOL RADIANTE")
        self.assertEqual(res["outer_god"], "Ra")

    def test_verificar_condiciones_exodo_a(self):
        p1 = Player(id=1, nombre_faccion="Ra", color=(255, 0, 0))
        p2 = Player(id=2, nombre_faccion="Seth", color=(0, 255, 0))
        bs = BoardState(viviendas=10)

        # Falla por fe insuficiente en bolsa azul (2 jugadores requieren 25)
        bs.bolsa_almacenamiento_fe = [1] * 10
        success, msg, surv = verificar_condiciones_exodo_a(bs, [p1, p2])
        self.assertFalse(success)
        self.assertIn("Fe insuficiente", msg)

        # Con suficiente fe:
        bs.bolsa_almacenamiento_fe = [1] * 25
        # Añadir sacrificios: p1 tiene 3 sacrificios, p2 tiene 1 sacrificio
        bs.bolsa_tumbas_egipcias = [
            Acolito(1, "Ra"), Acolito(1, "Ra"), Acolito(1, "Ra"),
            Acolito(2, "Seth")
        ]
        success, msg, surv = verificar_condiciones_exodo_a(bs, [p1, p2])
        self.assertTrue(success)
        self.assertTrue(p1.eliminado)
        self.assertFalse(p2.eliminado)
        self.assertEqual(len(surv), 1)
        self.assertEqual(surv[0].id, 2)


if __name__ == "__main__":
    unittest.main()
