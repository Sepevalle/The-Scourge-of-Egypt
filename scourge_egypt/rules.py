"""
Módulo de reglas, algoritmos de resolución y validaciones para The Scourge of Egypt.
"""
from __future__ import annotations
import random
from typing import List, Tuple, Dict, Optional, Any
from scourge_egypt.models import BoardState, Player, Acolito, PlagueCard, GodCard, Carro


SOLAR_WHEEL_INNER = [
    "SOL RADIANTE",
    "ECLIPSE",
    "SOL NACIENTE",
    "SOL PONIENTE"
]

SOLAR_WHEEL_OUTER = [
    "Ra",
    "Seth",
    "Osiris",
    "Horus",
    "Isis",
    "Anubis",
    "Thoth",
    "Hathor"
]

REQUISITO_FE_EXODO_A = {
    1: 15,
    2: 25,
    3: 35,
    4: 45
}

INITIAL_GANADO = {
    1: 15,
    2: 20,
    3: 30,
    4: 40
}

INITIAL_VIVIENDAS = {
    1: 20,
    2: 25,
    3: 35,
    4: 40
}


def get_potenciacion(ira_de_dios: int) -> int:
    """Calcula el factor de potenciación de plagas según la Ira de Dios."""
    if ira_de_dios >= 40:
        return 2
    elif ira_de_dios >= 20:
        return 1
    return 0


def check_famine_and_exhaustion(board_state: BoardState) -> List[str]:
    """Comprueba las líneas de hambruna (>=5) y agotamiento (10) en las cosechas."""
    logs = []
    for crop, value in board_state.cosechas.items():
        if value >= 10:
            logs.append(f"¡ALERTA MÁXIMA! El track de {crop.upper()} ha alcanzado AGOTAMIENTO TOTAL (10).")
            # Penalización por agotamiento: se pierde 1 ganado si hay disponible
            if board_state.ganado > 0:
                board_state.ganado -= 1
                board_state.bolsa_tumbas_egipcias.append("ganado")
                logs.append(f"La hambruna extrema de {crop} causa la pérdida de 1 ganado.")
        elif value >= 5:
            logs.append(f"Aviso de hambruna en {crop.upper()} (Posición {value}/10).")
    return logs


def sacrifice_acolytes(player: Player, board_state: BoardState, amount: int) -> int:
    """Sacrifica acólitos de un jugador enviándolos a la Bolsa Negra."""
    actual_sacrificed = min(player.reserva_acolitos, amount)
    player.reserva_acolitos -= actual_sacrificed
    for _ in range(actual_sacrificed):
        board_state.bolsa_tumbas_egipcias.append(Acolito(player_id=player.id, faction_name=player.nombre_faccion))
    return actual_sacrificed


def sacrifice_cattle(board_state: BoardState, amount: int) -> int:
    """Sacrifica ganado global enviándolo a la Bolsa Negra."""
    actual = min(board_state.ganado, amount)
    board_state.ganado -= actual
    for _ in range(actual):
        board_state.bolsa_tumbas_egipcias.append("ganado")
    return actual


def destroy_houses(board_state: BoardState, amount: int) -> int:
    """Destruye viviendas de la reserva global."""
    actual = min(board_state.viviendas, amount)
    board_state.viviendas -= actual
    return actual


def add_faith_to_blue_bag(player: Player, board_state: BoardState, amount: int) -> int:
    """Transfiere fichas de Fe de un jugador a la Bolsa Azul comunitaria."""
    actual = min(player.tokens_fe, amount)
    player.tokens_fe -= actual
    for _ in range(actual):
        board_state.bolsa_almacenamiento_fe.append(player.id)
    return actual


def check_commandments_progress(board_state: BoardState) -> Tuple[bool, Optional[int]]:
    """Comprueba si se han acumulado 5 cubos blancos en mandamientos."""
    if board_state.cubos_mandamiento >= 5:
        mandamiento_desvelado = board_state.mandamiento_actual
        board_state.cubos_mandamiento = 0
        board_state.mandamiento_actual += 1
        return True, mandamiento_desvelado
    return False, None


def resolve_solar_wheel(
    roll_total: int,
    inner_steps: int,
    outer_steps: int,
    current_inner: int,
    current_outer: int,
    player: Player
) -> Dict[str, Any]:
    """
    Resuelve la fase de la Gracia del Faraón (Rueda Solar).
    Reparte roll_total entre inner_steps y outer_steps.
    """
    if inner_steps + outer_steps != roll_total:
        raise ValueError(f"Los pasos asignados ({inner_steps} + {outer_steps}) deben sumar {roll_total}.")

    new_inner = (current_inner + inner_steps) % len(SOLAR_WHEEL_INNER)
    new_outer = (current_outer + outer_steps) % len(SOLAR_WHEEL_OUTER)

    inner_name = SOLAR_WHEEL_INNER[new_inner]
    outer_god = SOLAR_WHEEL_OUTER[new_outer]

    is_radiant = (inner_name == "SOL RADIANTE")
    matching_god: Optional[GodCard] = None

    for god in player.dioses_activos:
        if god.god_name.lower() == outer_god.lower():
            matching_god = god
            break

    success = is_radiant and (matching_god is not None)

    return {
        "new_inner_idx": new_inner,
        "new_outer_idx": new_outer,
        "inner_symbol": inner_name,
        "outer_god": outer_god,
        "success": success,
        "matched_god": matching_god
    }


def verificar_condiciones_exodo_a(board_state: BoardState, players: List[Player]) -> Tuple[bool, str, List[Player]]:
    """
    Verifica las condiciones de victoria de Éxodo A y descarte de jugadores antes de Éxodo B.
    Condición 1: Viviendas > 0
    Condición 2: Fe en Bolsa Azul >= requisito
    Condición 3: Recuento de sacrificios (se elimina quien tenga mayor número de sacrificios)
    """
    # Condición 1: Viviendas
    if board_state.viviendas <= 0:
        return False, "DERROTA: Todas las viviendas fueron destruidas por las plagas.", []

    # Condición 2: Almacenamiento de Fe (Bolsa Azul)
    num_players = len(players)
    req = REQUISITO_FE_EXODO_A.get(num_players, 45)
    total_fe = len(board_state.bolsa_almacenamiento_fe)
    if total_fe < req:
        return False, f"DERROTA: Fe insuficiente en la Bolsa Azul ({total_fe}/{req} requerida).", []

    # Condición 3: Recuento de Sacrificios (Bolsa Negra)
    conteo_sacrificios: Dict[int, int] = {p.id: 0 for p in players}
    for item in board_state.bolsa_tumbas_egipcias:
        if isinstance(item, Acolito):
            if item.player_id in conteo_sacrificios:
                conteo_sacrificios[item.player_id] += 1

    max_sacrificios = max(conteo_sacrificios.values()) if conteo_sacrificios else 0

    supervivientes: List[Player] = []
    for p in players:
        # Se elimina el jugador con max_sacrificios si no tiene Portal Seguro (y si al menos sacrificó > 0 si hay otros)
        if conteo_sacrificios[p.id] == max_sacrificios and max_sacrificios > 0 and not p.tiene_portal_seguro:
            p.eliminado = True
        else:
            p.eliminado = False
            supervivientes.append(p)

    # Si todos empatan con el máximo y ninguno tiene portal seguro, todos sobreviven si no hay distinción
    if len(supervivientes) == 0 and not any(p.tiene_portal_seguro for p in players):
        for p in players:
            p.eliminado = False
            supervivientes.append(p)

    if len(supervivientes) == 0:
        return False, "DERROTA: Todos los jugadores fueron consumidos por los sacrificios.", []

    return True, f"ÉXITO: ¡Transición a Éxodo B con {len(supervivientes)} jugadores supervivientes!", supervivientes
