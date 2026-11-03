"""
Motor de juego para la Fase Éxodo B (La Persecución en el Mar Rojo).
Gestiona el circuito de 30 casillas, carros, torbellino de fuego, cierre de aguas y escape.
"""
from __future__ import annotations
import random
from typing import List, Dict, Tuple, Optional, Any
from scourge_egypt.models import Player, Carro, BoardState, Card, GodCard, PlagueCard
from scourge_egypt.decks import build_moses_deck, build_gods_deck


class ExodusBEngine:
    def __init__(self, board_state: BoardState, players: List[Player]):
        self.board_state = board_state
        self.players = [p for p in players if not p.eliminado]
        self.current_player_idx = 0
        self.moses_deck = build_moses_deck()
        self.gods_deck = build_gods_deck()

        self.last_roll_d6: int = 0
        self.last_roll_d12: int = 0
        self.last_god_card: Optional[GodCard] = None
        self.last_moses_card: Optional[Card] = None
        self.last_advance: int = 0

        self.pending_risk: bool = False
        self.pending_sea_choice: bool = False   # Choice: Advance or Destroy last space

        self.log_messages: List[str] = []
        self.is_game_over: bool = False
        self.winner_player: Optional[Player] = None

        # Setup initial chariots: max 3 chariots based on remaining acolytes
        for p in self.players:
            p.carros_exodo_b = []
            num_carros = max(1, min(3, p.reserva_acolitos))
            for cid in range(1, num_carros + 1):
                # First chariot starts at position 1 (or 0), others in 'espera'
                c = Carro(
                    player_id=p.id,
                    carro_id=cid,
                    position=1 if cid == 1 else 0,
                    status="en_carrera" if cid == 1 else "espera"
                )
                p.carros_exodo_b.append(c)

        self.log("=== INICIO DE ÉXODO B: LA PERSECUCIÓN EN EL MAR ROJO ===")
        self.log(f"{len(self.players)} facciones compiten con sus carros por la supervivencia.")

    def log(self, message: str):
        self.log_messages.append(message)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def get_active_carro(self, player: Player) -> Optional[Carro]:
        # Return first chariot currently in race that has not escaped or been destroyed
        for c in player.carros_exodo_b:
            if c.status == "en_carrera":
                return c
        # If none in race, activate one in waiting
        for c in player.carros_exodo_b:
            if c.status == "espera":
                c.status = "en_carrera"
                c.position = 1
                return c
        return None

    def draw_god_card(self) -> GodCard:
        if not self.gods_deck:
            self.gods_deck = build_gods_deck()
        return self.gods_deck.pop()

    def draw_moses_card(self) -> Card:
        if not self.moses_deck:
            self.moses_deck = build_moses_deck()
        return self.moses_deck.pop()

    def execute_turn_phase_1_or_2(self, chosen_carro: Optional[Carro] = None) -> Dict[str, Any]:
        """
        Ejecuta la tirada y avance de un carro del jugador activo.
        """
        player = self.current_player
        carro = chosen_carro or self.get_active_carro(player)

        if not carro or carro.status != "en_carrera":
            self.log(f"{player.nombre_faccion} no tiene carros activos para mover.")
            self.next_turn()
            return {"status": "no_carro"}

        # Tiradas
        d6 = random.randint(1, 6)
        d12 = random.randint(1, 12)
        god_card = self.draw_god_card()

        self.last_roll_d6 = d6
        self.last_roll_d12 = d12
        self.last_god_card = god_card

        god_symbols = god_card.ra_symbols + god_card.seth_symbols
        total_puntos = d6 + god_symbols
        avance = total_puntos - d12
        self.last_advance = avance

        self.log(f"{player.nombre_faccion} tira: D6={d6} + Divinidad ({god_card.god_name}, {god_symbols} símb.) = {total_puntos} vs Moisés D12={d12}. Avance = {avance}.")

        # Caso Mar Rojo (casillas 20 a 30)
        if carro.position >= 20:
            return self._handle_sea_movement(carro, avance, god_symbols)
        else:
            return self._handle_whirlwind_movement(carro, avance)

    def _handle_whirlwind_movement(self, carro: Carro, avance: int) -> Dict[str, Any]:
        player = self.current_player
        if avance > 0:
            nueva_pos = min(20, carro.position + avance)
            carro.position = nueva_pos
            self.log(f"¡Carro #{carro.carro_id} de {player.nombre_faccion} avanza a la casilla {carro.position}!")

            if carro.position == 20:
                self.log(f"¡El Carro #{carro.carro_id} de {player.nombre_faccion} ha llegado a la casilla 20 (Mar Rojo)!")
                self._check_second_carro_reached_20(carro)
                # Permitir meter 2º carro si existe en espera
                for c2 in player.carros_exodo_b:
                    if c2.status == "espera":
                        c2.status = "en_carrera"
                        c2.position = 1
                        self.log(f"{player.nombre_faccion} introduce su 2º carro en la casilla de salida.")
                        break
            self.next_turn()
            return {"status": "advanced", "position": carro.position}
        else:
            self.log(f"Avance <= 0 ({avance}). El Carro #{carro.carro_id} se detiene. Opción de arriesgar gastando 1 cubo.")
            self.pending_risk = True
            return {"status": "pending_risk", "carro": carro}

    def _handle_sea_movement(self, carro: Carro, avance: int, god_symbols: int) -> Dict[str, Any]:
        player = self.current_player
        # Si ya está en modo reversa (regreso a la casilla 20 para escapar)
        if carro.reverse_to_20:
            if avance > 0:
                carro.position = max(20, carro.position - 1)
                self.log(f"El Carro #{carro.carro_id} retrocede hacia la salvación: Casilla {carro.position}.")
                if carro.position == 20:
                    carro.status = "escapado"
                    self.log(f"¡¡VICTORIA PARCIAL!! El Carro #{carro.carro_id} de {player.nombre_faccion} ha ESCAPADO en la casilla 20.")
                    self._check_game_over()
            else:
                self.log(f"El carro no logra retroceder este turno.")
            self.next_turn()
            return {"status": "reverse_advanced", "position": carro.position}

        # Avanzando en el Mar Rojo hacia la 30
        if avance > 0:
            # En el Mar Rojo solo se avanza 1 casilla por éxito
            carro.position = min(self.board_state.casillas_activas_mar_rojo, carro.position + 1)
            self.log(f"Internándose en el mar: Carro #{carro.carro_id} avanza a la casilla {carro.position}.")

            if carro.position >= self.board_state.casillas_activas_mar_rojo:
                carro.reverse_to_20 = True
                self.log(f"¡Carro #{carro.carro_id} alcanza el confín del mar! Da la vuelta y ahora debe escapar de vuelta a la 20.")

            # Si las aguas ya están cerrándose, resolver evento de avance
            if self.board_state.segundo_carro_en_20:
                return self._resolve_closing_waters_card_draw(carro, god_symbols)

            self.next_turn()
            return {"status": "sea_advanced", "position": carro.position}
        else:
            # En el Mar Rojo, resultados negativos fuerzan arriesgar automáticamente sin gastar cubos
            self.log("Resultado negativo en el Mar Rojo: Se fuerza arriesgar automáticamente.")
            return self.resolve_risk(carro, force_free=True)

    def _check_second_carro_reached_20(self, current_carro: Carro):
        """Comprueba si un segundo carro (de cualquier jugador) ha llegado a la casilla 20."""
        if self.board_state.segundo_carro_en_20:
            return

        carros_en_20_o_mas = 0
        for p in self.players:
            for c in p.carros_exodo_b:
                if c.position >= 20 and c.status in ("en_carrera", "escapado"):
                    carros_en_20_o_mas += 1

        if carros_en_20_o_mas >= 2:
            self.board_state.segundo_carro_en_20 = True
            self.log("==================================================")
            self.log("¡¡ALERTA MÁXIMA: LAS AGUAS EMPIEZAN A CERRARSE!!")
            self.log("Todos los carros que no alcanzaron la casilla 21 son engullidos.")
            self.log("==================================================")
            # Eliminar carros que no alcanzaron la casilla 21
            for p in self.players:
                for c in p.carros_exodo_b:
                    if c.status == "en_carrera" and c.position < 21:
                        c.status = "destruido"
                        self.log(f"El Carro #{c.carro_id} de {p.nombre_faccion} (en casilla {c.position}) ha sido destruido por el mar.")
            self._check_game_over()

    def _resolve_closing_waters_card_draw(self, carro: Carro, god_symbols: int) -> Dict[str, Any]:
        """Al avanzar con aguas cerrándose, robar carta de Moisés y comparar con Divinidad."""
        moses_card = self.draw_moses_card()
        self.last_moses_card = moses_card
        wrath_val = getattr(moses_card, "wrath_increment", 1)

        self.log(f"Moisés alza su vara: Carta '{moses_card.name}' (Ira={wrath_val}) vs Símbolos Divinos ({god_symbols}).")

        if god_symbols > wrath_val:
            self.log("Símbolos Divinos superan la Ira: El jugador puede elegir entre avanzar +1 o destruir la última casilla del mar.")
            self.pending_sea_choice = True
            return {"status": "pending_sea_choice", "carro": carro}
        else:
            self.log("La Ira de Dios domina: El carro se ve forzado a avanzar hacia adelante.")
            carro.position = min(self.board_state.casillas_activas_mar_rojo, carro.position + 1)
            self.next_turn()
            return {"status": "sea_forced_advance", "position": carro.position}

    def resolve_sea_choice(self, carro: Carro, choice: str):
        """choice: 'advance' or 'destroy_space'"""
        self.pending_sea_choice = False
        if choice == "destroy_space":
            self.board_state.casillas_activas_mar_rojo -= 1
            destroyed_pos = self.board_state.casillas_activas_mar_rojo + 1
            self.log(f"¡El mar colapsa! La casilla {destroyed_pos} ha sido destruida (límite ahora: {self.board_state.casillas_activas_mar_rojo}).")
            # Si algún carro estaba en esa casilla o más adelante, debe retroceder o muere
            for p in self.players:
                for c in p.carros_exodo_b:
                    if c.status == "en_carrera" and c.position >= destroyed_pos:
                        c.position = self.board_state.casillas_activas_mar_rojo
                        self.log(f"Carro #{c.carro_id} de {p.nombre_faccion} retrocede forzosamente a la casilla {c.position}.")
        else:
            carro.position = min(self.board_state.casillas_activas_mar_rojo, carro.position + 1)
            self.log(f"El jugador decide avanzar con su Carro #{carro.carro_id} a la casilla {carro.position}.")

        self.next_turn()

    def resolve_risk(self, carro: Carro, force_free: bool = False) -> Dict[str, Any]:
        """Ejecuta la opción de arriesgar tras tirada negativa."""
        player = self.current_player
        self.pending_risk = False

        if not force_free:
            if player.reserva_acolitos <= 0:
                self.log(f"{player.nombre_faccion} no tiene acólitos para gastar en arriesgar.")
                self.next_turn()
                return {"status": "no_acolytes"}
            player.reserva_acolitos -= 1
            self.board_state.bolsa_tumbas_egipcias.append("arriesgar")
            self.log(f"{player.nombre_faccion} sacrifica 1 cubo para arriesgar.")

        moses_card = self.draw_moses_card()
        self.last_moses_card = moses_card
        wrath_val = getattr(moses_card, "wrath_increment", 0)

        if wrath_val > 0:
            carro.position = min(20, carro.position + wrath_val)
            self.log(f"¡Éxito en el riesgo! Carta '{moses_card.name}' tiene avance de Ira (+{wrath_val}). Carro avanza a {carro.position}.")
            if carro.position == 20:
                self._check_second_carro_reached_20(carro)
            res = {"status": "risk_success", "advance": wrath_val, "position": carro.position}
        else:
            carro.status = "destruido"
            self.log(f"¡Catástrofe! Carta '{moses_card.name}' no tiene avance de Ira. ¡El Carro #{carro.carro_id} QUEDA DESTRUIDO!")
            self._check_game_over()
            res = {"status": "risk_failed", "destroyed": True}

        self.next_turn()
        return res

    def pass_risk(self):
        """El jugador decide no arriesgar."""
        self.pending_risk = False
        self.log(f"{self.current_player.nombre_faccion} decide no arriesgar y permanece en su posición.")
        self.next_turn()

    def next_turn(self):
        self._check_game_over()
        if not self.is_game_over:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def _check_game_over(self):
        # Todos los carros de todos los jugadores han escapado o están destruidos
        total_carros = sum(len(p.carros_exodo_b) for p in self.players)
        finalizados = sum(
            1 for p in self.players for c in p.carros_exodo_b
            if c.status in ("escapado", "destruido")
        )

        if finalizados == total_carros and total_carros > 0:
            self.is_game_over = True
            self.board_state.fase_actual = "VICTORIA"

            # Contar carros escapados por jugador
            escapados = {
                p.id: sum(1 for c in p.carros_exodo_b if c.status == "escapado")
                for p in self.players
            }
            max_esc = max(escapados.values()) if escapados else 0
            if max_esc > 0:
                ganadores = [p for p in self.players if escapados[p.id] == max_esc]
                self.winner_player = ganadores[0]
                self.log(f"¡¡FIN DEL JUEGO!! Ganador: {self.winner_player.nombre_faccion} con {max_esc} carros a salvo.")
            else:
                self.board_state.fase_actual = "DERROTA"
                self.log("FIN DEL JUEGO: Ningún carro logró regresar con vida a la casilla 20. Derrota total.")
