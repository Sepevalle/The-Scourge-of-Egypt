"""
Motor central de juego para The Scourge of Egypt.
Controla el flujo de turnos, fases de Éxodo A, eventos de plagas, ruedas solares y transición a Éxodo B.
"""
from __future__ import annotations
import random
from typing import List, Dict, Optional, Tuple, Any, Callable
from scourge_egypt.models import (
    BoardState, Player, ActionTile, Card, PlagueCard, GodCard, CommandmentCard,
    ItemCard, Acolito, FACTIONS_DEF, create_default_action_tiles
)
from scourge_egypt.decks import (
    build_moses_deck, build_gods_deck, build_commandments_deck
)
from scourge_egypt.rules import (
    get_potenciacion, check_famine_and_exhaustion, sacrifice_acolytes,
    sacrifice_cattle, destroy_houses, add_faith_to_blue_bag,
    check_commandments_progress, resolve_solar_wheel, verificar_condiciones_exodo_a,
    INITIAL_GANADO, INITIAL_VIVIENDAS, REQUISITO_FE_EXODO_A
)
from scourge_egypt.exodus_b_engine import ExodusBEngine


class GameEngine:
    def __init__(self, num_players: int = 2, faction_indices: Optional[List[int]] = None):
        self.num_players = max(1, min(4, num_players))
        self.players: List[Player] = []
        self._init_players(faction_indices)

        self.board_state = BoardState(
            ganado=INITIAL_GANADO.get(self.num_players, 20),
            viviendas=INITIAL_VIVIENDAS.get(self.num_players, 25)
        )

        self.moses_deck: List[Card] = build_moses_deck()
        self.gods_deck: List[GodCard] = build_gods_deck()
        self.commandments_deck: List[CommandmentCard] = build_commandments_deck()

        self.current_player_idx: int = 0
        self.turn_number: int = 1
        self.round_number: int = 1

        self.current_moses_card: Optional[Card] = None
        self.moses_card_history: List[Dict[str, Any]] = []
        self.active_commandment: Optional[CommandmentCard] = None
        self.last_drawn_god_card: Optional[GodCard] = None

        # Turn phase state in Exodus A:
        # 'DRAW_MOSES', 'RESOLVE_PLAGUE', 'ACTION_TILES', 'SOLAR_WHEEL', 'TURN_END'
        self.turn_subphase: str = "DRAW_MOSES"
        self.actions_remaining_this_turn: int = 4
        self.regadios_used_this_turn: bool = False

        self.pending_choice: Optional[Dict[str, Any]] = None
        self.log_messages: List[str] = []

        self.exodus_b_engine: Optional[ExodusBEngine] = None
        self.game_over_reason: str = ""

        self.log(f"=== PARTIDA INICIADA: THE SCOURGE OF EGYPT ({self.num_players} Jugadores) ===")
        for p in self.players:
            self.log(f"Facción {p.id}: {p.nombre_faccion} (Acólitos: {p.reserva_acolitos}, Fe: {p.tokens_fe})")

    def _init_players(self, faction_indices: Optional[List[int]] = None):
        indices = faction_indices if faction_indices and len(faction_indices) == self.num_players else list(range(self.num_players))
        for i, f_idx in enumerate(indices):
            f_idx = f_idx % len(FACTIONS_DEF)
            fdef = FACTIONS_DEF[f_idx]
            p = Player(
                id=i + 1,
                nombre_faccion=fdef["name"],
                color=fdef["color"],
                reserva_acolitos=5,
                tokens_fe=3,
                losetas_accion=create_default_action_tiles()
            )
            self.players.append(p)

    def log(self, message: str):
        self.log_messages.append(message)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    @property
    def is_in_exodus_b(self) -> bool:
        return self.board_state.fase_actual == "EXODUS_B"

    # -------------------------------------------------------------
    # FASE 1 DE TURNO: ROBAR Y PROCESAR CARTA DE MOISÉS
    # -------------------------------------------------------------
    def start_turn(self):
        """Inicia el turno del jugador activo."""
        player = self.current_player
        if player.eliminado:
            self.next_turn()
            return

        self.actions_remaining_this_turn = 3 if self.board_state.tinieblas_turnos_restantes > 0 else 4
        self.regadios_used_this_turn = False
        self.turn_subphase = "DRAW_MOSES"

        # Penalización acumulada de Úlceras
        if player.ulceras_deuda_turnos > 0:
            sacrifice_acolytes(player, self.board_state, 1)
            player.ulceras_deuda_turnos -= 1
            self.log(f"Efecto de Úlceras: {player.nombre_faccion} sacrifica 1 acólito por la plaga infecciosa ({player.ulceras_deuda_turnos} turnos restantes).")

        self.log(f"--- Turno {self.turn_number} (Ronda {self.round_number}): {player.nombre_faccion} ---")

    def draw_moses_card(self) -> Card:
        """Roba la siguiente carta del mazo de Moisés."""
        if not self.moses_deck:
            self.moses_deck = build_moses_deck()
            self.log("El Mazo de Moisés se ha regenerado y barajado.")

        card = self.moses_deck.pop()
        self.current_moses_card = card
        self.moses_card_history.append({
            "card": card,
            "turn": self.turn_number,
            "round": self.round_number,
            "faction": self.current_player.nombre_faccion,
        })
        self.log(f"Moisés revela: [{card.name}] ({card.card_type.upper()}) - {card.description}")

        # Si tiene símbolo de mandamiento, añadir cubo
        if getattr(card, "has_commandment_symbol", False):
            self.board_state.cubos_mandamiento += 1
            self.log(f"¡Símbolo de las Tablas de la Ley! Se añade +1 cubo al Mandamiento ({self.board_state.cubos_mandamiento}/5 cubos).")
            self._check_commandments()

        self.turn_subphase = "RESOLVE_PLAGUE"
        self._dispatch_moses_card_resolution(card)
        return card

    def _check_commandments(self):
        triggered, mand_num = check_commandments_progress(self.board_state)
        if triggered:
            # Desvelar carta de mandamiento
            if self.commandments_deck:
                mand_card = self.commandments_deck.pop(0)
            else:
                mand_card = CommandmentCard(
                    id="mand_extra", name=f"Mandamiento {mand_num}", card_type="mandamiento",
                    description="La ley sagrada se cumple.", number=mand_num, roman_number=str(mand_num)
                )
            self.active_commandment = mand_card
            self.log("==================================================")
            self.log(f"¡¡TABLA DE LA LEY CUMPLIDA!! {mand_card.name}: '{mand_card.effect_name}'")
            self.log(f"Efecto: {mand_card.description}")
            self.log("==================================================")
            self._apply_commandment_effect(mand_card)

            # Si Moisés alcanza la casilla X (10), finaliza Éxodo A
            if mand_num >= 10:
                self.log("¡¡EL MEEPLE DE MOISÉS HA ALCANZADO LA CASILLA X (FIN DEL ÉXODO A)!!")
                self._evaluate_exodus_a_transition()

    def _apply_commandment_effect(self, mand: CommandmentCard):
        num = mand.number
        if num == 1:
            # Máximo 3 dioses activos
            for p in self.players:
                while len(p.dioses_activos) > 3:
                    discarded = p.dioses_activos.pop()
                    self.log(f"{p.nombre_faccion} descarta a {discarded.god_name} por el Mandamiento I.")
        elif num == 2:
            # Descarta 1 objeto o paga 1 Fe
            for p in self.players:
                if p.objetos_activos:
                    p.objetos_activos.pop()
                    self.log(f"{p.nombre_faccion} descarta un objeto mítico.")
                elif p.tokens_fe > 0:
                    p.tokens_fe -= 1
                    self.log(f"{p.nombre_faccion} pierde 1 token de Fe por el Mandamiento II.")
        elif num == 5:
            # +1 acólito de refuerzo
            for p in self.players:
                p.reserva_acolitos += 1
                self.log(f"{p.nombre_faccion} recibe +1 acólito por Honrar Padre y Madre.")
        elif num == 7:
            # Todos aportan 1 Fe a la Bolsa Azul
            for p in self.players:
                if p.tokens_fe > 0:
                    add_faith_to_blue_bag(p, self.board_state, 1)
                    self.log(f"{p.nombre_faccion} aporta 1 Fe a la Bolsa Azul.")
        elif num == 8:
            # Si cosechas >= 5, retroceden 1
            for crop, val in self.board_state.cosechas.items():
                if val >= 5:
                    self.board_state.cosechas[crop] = max(0, val - 1)
                    self.log(f"La cosecha de {crop} retrocede a {self.board_state.cosechas[crop]}.")
        elif num == 9:
            # Comprobar Bolsa Azul >= 15
            if len(self.board_state.bolsa_almacenamiento_fe) >= 15:
                self.board_state.ira_de_dios = max(0, self.board_state.ira_de_dios - 3)
                self.log("Bolsa Azul tiene >= 15 de Fe: ¡Ira de Dios reducida en 3 puntos!")
        elif num == 10:
            # Ceder 1 acólito al más desfavorecido
            jugador_max = max(self.players, key=lambda p: p.reserva_acolitos)
            jugador_min = min(self.players, key=lambda p: p.reserva_acolitos)
            if jugador_max.id != jugador_min.id and jugador_max.reserva_acolitos > 0:
                jugador_max.reserva_acolitos -= 1
                jugador_min.reserva_acolitos += 1
                self.log(f"Mandamiento X: {jugador_max.nombre_faccion} cede 1 acólito a {jugador_min.nombre_faccion}.")

    def _evaluate_exodus_a_transition(self):
        self.board_state.fase_actual = "TRANSICION"
        exito, motivo, supervivientes = verificar_condiciones_exodo_a(self.board_state, self.players)
        self.log(motivo)
        if exito:
            self.board_state.fase_actual = "EXODUS_B"
            self.exodus_b_engine = ExodusBEngine(self.board_state, supervivientes)
            self.log("¡¡Comienza la Persecución del Faraón en el Mar Rojo!!")
        else:
            self.board_state.fase_actual = "DERROTA"
            self.game_over_reason = motivo

    def _dispatch_moses_card_resolution(self, card: Card):
        """Despacha la resolución de la carta según su tipo."""
        if isinstance(card, PlagueCard):
            self._resolve_plague(card)
        elif card.card_type == "personaje":
            self._resolve_character(card)
        elif card.card_type == "evento":
            self._resolve_event(card)
        elif card.card_type == "edificio":
            self._resolve_building(card)
        else:
            self.turn_subphase = "ACTION_TILES"

    def _resolve_plague(self, card: PlagueCard):
        pot = get_potenciacion(self.board_state.ira_de_dios)
        p_type = card.plague_type

        if p_type == "sangre":
            self.board_state.cartas_sangre_en_mesa += 1
            coste = 2 + pot
            self.pending_choice = {
                "type": "sangre_choice",
                "cost": coste,
                "player_id": self.current_player.id,
                "message": f"Plaga de Sangre: ¿Aumentar Ira de Dios (+{coste}) o Sacrificar {coste} acólitos?",
                "options": [f"Aumentar Ira (+{coste})", f"Sacrificar {coste} acólitos"]
            }
            # Efecto complementario si hay 8 cartas en mesa
            if self.board_state.cartas_sangre_en_mesa >= 8:
                self.log("¡¡8 CARTAS DE SANGRE EN MESA!! Efecto Complementario activado.")
                self.board_state.ira_de_dios = min(50, self.board_state.ira_de_dios + 1)
                for p in self.players:
                    if p.tokens_fe < 3:
                        sacrifice_acolytes(p, self.board_state, 1)
                        self.log(f"{p.nombre_faccion} tiene menos de 3 Fe y sacrifica 1 acólito.")

        elif p_type == "ranas_langostas":
            side = random.choice(["ranas", "langostas"])
            self.log(f"Carta Doble resuelta por el lado: {side.upper()}.")
            if side == "ranas":
                self._flip_random_tiles(self.current_player, 3)
                self.board_state.ira_de_dios = min(50, self.board_state.ira_de_dios + 1)
            else:
                self._flip_random_tiles(self.current_player, 3)
                self.current_player.tokens_fe += 1
                self.board_state.ira_de_dios = min(50, self.board_state.ira_de_dios + 2)

            # Dado Moisés D12 para cosechas
            d12 = random.randint(1, 12)
            crop_target = "trigo" if d12 <= 4 else ("avena" if d12 <= 8 else "cebada")
            delta = 1 + pot
            self.board_state.cosechas[crop_target] = min(10, self.board_state.cosechas[crop_target] + delta)
            self.log(f"Tirada D12 Moisés ({d12}): La cosecha de {crop_target.upper()} avanza +{delta} (Posición actual: {self.board_state.cosechas[crop_target]}/10).")
            famine_logs = check_famine_and_exhaustion(self.board_state)
            for f_log in famine_logs:
                self.log(f_log)
            self.turn_subphase = "ACTION_TILES"

        elif p_type == "moscas_ganado":
            sub = card.sub_type
            if sub == "moscas":
                if self.board_state.ganado > 0:
                    sacrifice_cattle(self.board_state, 1)
                    self.log("Plaga de Moscas: Se sacrifica 1 ganado a la Bolsa Negra.")
                else:
                    sacrifice_acolytes(self.current_player, self.board_state, 2)
                    self.log("Sin ganado disponible: El jugador sacrifica 2 acólitos.")
                self.turn_subphase = "ACTION_TILES"
            elif sub == "mosquitos":
                d6 = random.randint(1, 6)
                loss = 1 if d6 <= 3 else (2 if d6 <= 5 else 3)
                self.log(f"Plaga de Mosquitos (D6={d6}): Se pierden {loss} ganado.")
                actual = sacrifice_cattle(self.board_state, loss)
                if actual < loss:
                    rem = loss - actual
                    sacrifice_acolytes(self.current_player, self.board_state, rem)
                    self.log(f"Falta de ganado compensada sacrificando {rem} acólitos.")
                self.turn_subphase = "ACTION_TILES"
            elif sub == "ganado":
                self.board_state.cartas_ganado_en_mesa += 1
                count = self.board_state.cartas_ganado_en_mesa
                self.log(f"Peste del Ganado (Carta acumulada #{count}).")
                if count == 3:
                    loss = max(1, self.board_state.ganado // 4)
                    sacrifice_cattle(self.board_state, loss)
                    self.log(f"¡Carta #3 alcanzada! Se sacrifica 1/4 del ganado ({loss} cabezas).")
                elif count >= 8:
                    loss = max(1, self.board_state.ganado // 2)
                    sacrifice_cattle(self.board_state, loss)
                    self.log(f"¡Carta #8 alcanzada! Se sacrifica la mitad del ganado ({loss} cabezas).")
                if self.board_state.ganado <= 0:
                    self._destroy_tile_per_faction_or_acolyte()
                self.turn_subphase = "ACTION_TILES"

        elif p_type == "ulceras":
            self.log("Plaga de Úlceras: Cada jugador consulta una divinidad para medir Ra vs Seth...")
            total_ra = 0
            total_seth = 0
            for p in self.players:
                if not self.gods_deck:
                    self.gods_deck = build_gods_deck()
                temp_god = self.gods_deck.pop()
                total_ra += temp_god.ra_symbols
                total_seth += temp_god.seth_symbols
                self.log(f"{p.nombre_faccion} consulta a {temp_god.god_name} (+{temp_god.ra_symbols} Ra, +{temp_god.seth_symbols} Seth).")

            if total_seth > total_ra:
                self.log(f"Mayoría de Seth ({total_seth} vs {total_ra}): ¡Todos los jugadores sacrifican 1 acólito!")
                for p in self.players:
                    sacrifice_acolytes(p, self.board_state, 1)
            elif total_ra > total_seth:
                self.log(f"Mayoría de Ra ({total_ra} vs {total_seth}): Se extrae un cubo de la Bolsa Negra...")
                if self.board_state.bolsa_tumbas_egipcias:
                    item = self.board_state.bolsa_tumbas_egipcias.pop()
                    if isinstance(item, Acolito):
                        revived_player = next((p for p in self.players if p.id == item.player_id), None)
                        if revived_player:
                            revived_player.reserva_acolitos += 1
                            self.log(f"¡MILAGRO! Un acólito de {revived_player.nombre_faccion} ha sido RESUCITADO.")
                    else:
                        self.log("Se extrajo ganado de la bolsa; no revive acólito.")
                else:
                    self.log("La Bolsa Negra está vacía; no hay acólitos que revivir.")
            else:
                self.log("Empate entre Ra y Seth: El jugador activo sufre una afección ulcerosa por 2 turnos.")
                self.current_player.ulceras_deuda_turnos = 2
            self.turn_subphase = "ACTION_TILES"

        elif p_type == "granizo":
            d12 = random.randint(1, 12)
            base_loss = 2 if d12 <= 4 else (3 if d12 <= 8 else 4)
            total_loss = base_loss + pot
            destroyed = destroy_houses(self.board_state, total_loss)
            self.log(f"Granizo y Fuego (D12={d12}): Se destruyen {destroyed} viviendas ({self.board_state.viviendas} restantes).")
            # Por cada 2 viviendas destruidas, sacrificar 1 acólito colectivo
            acolyte_sac = destroyed // 2
            if acolyte_sac > 0:
                sacrifice_acolytes(self.current_player, self.board_state, acolyte_sac)
                self.log(f"El colapso de viviendas obliga a sacrificar {acolyte_sac} acólitos.")
            if self.board_state.viviendas <= 0:
                self.log("¡¡TODAS LAS VIVIENDAS HAN SIDO DESTRUIDAS!!")
                self._evaluate_exodus_a_transition()
            self.turn_subphase = "ACTION_TILES"

        elif p_type == "tinieblas":
            self.board_state.tinieblas_turnos_restantes = 3
            self.actions_remaining_this_turn = min(3, self.actions_remaining_this_turn)
            self.log("¡¡TINIEBLAS SOBRE EGIPTO!! Se bloquean las Divinidades y se limitan las losetas a 3 durante 3 turnos.")
            self.log("Se activa automáticamente la Gracia Extraordinaria del Faraón.")
            self.turn_subphase = "SOLAR_WHEEL"

        elif p_type == "primogenitos":
            pot_amount = 1 + pot
            self.log(f"Ángel Exterminador: Cada jugador debe consagrar {pot_amount} acólitos al umbral.")
            for p in self.players:
                moved = min(p.reserva_acolitos, pot_amount)
                p.reserva_acolitos -= moved
                for _ in range(moved):
                    self.board_state.acolitos_angel_exterminador.append(Acolito(player_id=p.id, faction_name=p.nombre_faccion))
                self.log(f"{p.nombre_faccion} envía {moved} acólitos al Ángel Exterminador.")
            if card.card_number >= 10:
                self.log("¡¡CARTA #10 DEL ÁNGEL EXTERMINADOR!! Todos los acólitos son sacrificados a la Bolsa Negra.")
                for ac in self.board_state.acolitos_angel_exterminador:
                    owner = next((p for p in self.players if p.id == ac.player_id), None)
                    if owner and owner.tiene_portal_seguro:
                        owner.reserva_acolitos += 1
                        self.log(f"{owner.nombre_faccion} tiene Portal Seguro y su acólito se salva.")
                    else:
                        self.board_state.bolsa_tumbas_egipcias.append(ac)
                self.board_state.acolitos_angel_exterminador.clear()
            self.turn_subphase = "ACTION_TILES"
        else:
            self.turn_subphase = "ACTION_TILES"

    def _resolve_character(self, card: Card):
        cid = card.id
        if cid == "personaje_aaron":
            self.board_state.cubos_mandamiento += 1
            self.log("Aarón aporta firmeza: +1 cubo a los Mandamientos.")
            self._check_commandments()
        elif cid == "personaje_miriam":
            self.log("Miriam entona cánticos de alabanza. Cada jugador con Fe puede aportar a la Bolsa Azul.")
            for p in self.players:
                if p.tokens_fe > 0:
                    add_faith_to_blue_bag(p, self.board_state, 1)
            self.board_state.ira_de_dios = max(0, self.board_state.ira_de_dios - 2)
            self.log("La fe ferviente reduce la Ira de Dios en 2.")
        elif cid == "personaje_jetro":
            self.board_state.viviendas += 2
            self.board_state.ganado += 1
            self.log("Consejo de Jetro: +2 viviendas y +1 ganado a las reservas globales.")
        elif cid == "personaje_josue":
            for p in self.players:
                for tile in p.losetas_accion:
                    if tile.state == "destruida":
                        tile.state = "activa"
                        self.log(f"Josué restaura la loseta '{tile.name}' de {p.nombre_faccion}.")
                        break
        self.turn_subphase = "ACTION_TILES"

    def _resolve_event(self, card: Card):
        cid = card.id
        if cid == "evento_zarza":
            self.board_state.ira_de_dios = min(50, self.board_state.ira_de_dios + 2)
            self.board_state.cubos_mandamiento += 1
            self.log("La Zarza Ardiente: Ira de Dios +2 y +1 cubo a Mandamientos.")
            self._check_commandments()
        elif cid == "evento_mana":
            for crop in self.board_state.cosechas:
                self.board_state.cosechas[crop] = max(0, self.board_state.cosechas[crop] - 2)
            self.log("¡Maná del Cielo! Todos los tracks de cosecha se alivian en 2 puntos.")
        elif cid == "evento_columna_fuego":
            self.board_state.tinieblas_turnos_restantes = 0
            for p in self.players:
                p.tokens_fe += 1
            self.log("Columna de Fuego: Disipa las Tinieblas y otorga +1 Fe a cada jugador.")
        elif cid == "evento_agua_roca":
            self.board_state.ganado += 3
            for p in self.players:
                if p.reserva_acolitos < 3:
                    p.reserva_acolitos += 1
            self.log("Agua brotando de la roca: +3 ganado y refuerzo de acólitos a facciones necesitadas.")
        self.turn_subphase = "ACTION_TILES"

    def _resolve_building(self, card: ItemCard):
        self.current_player.objetos_activos.append(card)
        if card.effect_type == "portal_seguro":
            self.current_player.tiene_portal_seguro = True
            self.log(f"¡{self.current_player.nombre_faccion} reclama el PORTAL SEGURO! Inmunidad en el recuento final.")
        else:
            self.log(f"{self.current_player.nombre_faccion} construye el edificio '{card.name}'.")
        self.turn_subphase = "ACTION_TILES"

    def resolve_choice(self, option_index: int):
        """Resuelve una decisión pendiente (ej. Sangre: Ira vs Sacrificio)."""
        if not self.pending_choice:
            return

        c_type = self.pending_choice.get("type")
        cost = self.pending_choice.get("cost", 2)
        player = self.current_player

        if c_type == "sangre_choice":
            if option_index == 0:
                self.board_state.ira_de_dios = min(50, self.board_state.ira_de_dios + cost)
                self.log(f"{player.nombre_faccion} opta por aumentar la Ira de Dios en +{cost} (Total: {self.board_state.ira_de_dios}/50).")
            else:
                sac = sacrifice_acolytes(player, self.board_state, cost)
                self.log(f"{player.nombre_faccion} sacrifica {sac} acólitos a la Bolsa Negra para aplacar la sangre.")

        self.pending_choice = None
        self.turn_subphase = "ACTION_TILES"

    def _flip_random_tiles(self, player: Player, count: int):
        active_tiles = [t for t in player.losetas_accion if t.state == "activa"]
        random.shuffle(active_tiles)
        flipped = active_tiles[:count]
        for t in flipped:
            t.state = "usada_boca_abajo"
            self.log(f"Loseta '{t.name}' de {player.nombre_faccion} volteada boca abajo.")

    def _destroy_tile_per_faction_or_acolyte(self):
        for p in self.players:
            active_tiles = [t for t in p.losetas_accion if t.state == "activa"]
            if active_tiles:
                t = active_tiles[0]
                t.state = "destruida"
                self.log(f"Sin ganado: {p.nombre_faccion} pierde su loseta '{t.name}'.")
            elif p.reserva_acolitos > 0:
                sacrifice_acolytes(p, self.board_state, 1)
                self.log(f"Sin ganado ni losetas: {p.nombre_faccion} sacrifica 1 acólito.")

    # -------------------------------------------------------------
    # FASE 2: USO DE LOSETAS DE ACCIÓN Y DIOSES
    # -------------------------------------------------------------
    def use_action_tile(self, tile_index: int, extra_param: Optional[str] = None) -> bool:
        """Usa una loseta de acción del jugador activo."""
        player = self.current_player
        if tile_index < 0 or tile_index >= len(player.losetas_accion):
            return False

        tile = player.losetas_accion[tile_index]
        if tile.state != "activa":
            self.log(f"La loseta '{tile.name}' no está disponible (estado: {tile.state}).")
            return False

        if self.actions_remaining_this_turn <= 0:
            self.log(f"No te quedan más acciones este turno.")
            return False

        # Ejecutar acción
        tile_id = tile.id_name
        success = True

        if tile_id == "COSECHAR":
            crop = extra_param if extra_param in ("trigo", "avena", "cebada") else "trigo"
            self.board_state.cosechas[crop] = max(0, self.board_state.cosechas[crop] - 2)
            self.log(f"{player.nombre_faccion} usa COSECHAR: Alivia el track de {crop.upper()} a {self.board_state.cosechas[crop]}/10.")

        elif tile_id == "REZAR":
            self.board_state.ira_de_dios = max(0, self.board_state.ira_de_dios - 2)
            self.log(f"{player.nombre_faccion} usa REZAR: La Ira de Dios baja a {self.board_state.ira_de_dios}/50.")

        elif tile_id == "GANADERIA":
            self.board_state.ganado += 2
            self.log(f"{player.nombre_faccion} usa GANADERÍA: +2 ganado (Total global: {self.board_state.ganado}).")

        elif tile_id == "REGADIOS":
            if player.tokens_fe >= 1:
                player.tokens_fe -= 1
                self.actions_remaining_this_turn += 2  # Gasta 1 acción pero suma 2, neto +1
                self.regadios_used_this_turn = True
                self.log(f"{player.nombre_faccion} activa REGADÍOS gastando 1 Fe: +1 acción adicional este turno.")
            else:
                self.log(f"No tienes suficientes fichas de Fe para activar Regadíos.")
                return False

        elif tile_id == "RENACIMIENTO":
            player.reserva_acolitos += 2
            self.log(f"{player.nombre_faccion} usa RENACIMIENTO: +2 acólitos a su reserva (Total: {player.reserva_acolitos}).")

        elif tile_id == "RECONSTRUCCION":
            self.board_state.viviendas += 2
            self.log(f"{player.nombre_faccion} usa RECONSTRUCCIÓN: +2 viviendas (Total global: {self.board_state.viviendas}).")

        elif tile_id == "DIOSES_FAVORABLES":
            player.rerolls_disponibles += 1
            self.log(f"{player.nombre_faccion} usa DIOSES FAVORABLES: +1 relanzamiento de dados acumulado.")

        elif tile_id == "RENDIR_PLEITESIA":
            player.tokens_fe += 2
            self.log(f"{player.nombre_faccion} usa RENDIR PLEITESÍA: +2 tokens de Fe (Total: {player.tokens_fe}).")

        tile.state = "usada_boca_abajo"
        self.actions_remaining_this_turn -= 1
        return success

    def donate_faith(self, amount: int = 1) -> bool:
        """Dona fichas de Fe a la Bolsa Azul comunitaria."""
        player = self.current_player
        if player.tokens_fe < amount:
            self.log("No dispones de suficientes tokens de Fe para donar.")
            return False
        donated = add_faith_to_blue_bag(player, self.board_state, amount)
        self.log(f"{player.nombre_faccion} deposita {donated} Fe en la Bolsa Azul (Total acumulado: {len(self.board_state.bolsa_almacenamiento_fe)}).")
        return True

    def buy_god_card(self) -> Optional[GodCard]:
        """Adquiere una carta de Divinidad pagando 2 tokens de Fe (si no hay tinieblas)."""
        player = self.current_player
        if self.board_state.tinieblas_turnos_restantes > 0:
            self.log("Las Tinieblas impiden comunicarse con las Divinidades.")
            return None
        if len(player.dioses_activos) >= 3:
            self.log("Ya tienes el límite máximo de 3 Divinidades activas.")
            return None
        if player.tokens_fe < 2:
            self.log("Necesitas al menos 2 tokens de Fe para invocar una Divinidad.")
            return None

        if not self.gods_deck:
            self.gods_deck = build_gods_deck()

        god = self.gods_deck.pop()
        player.tokens_fe -= 2
        player.dioses_activos.append(god)
        self.log(f"¡{player.nombre_faccion} invoca a {god.god_name}! ({god.power_name}: {god.power_description}).")
        return god

    def activate_god_power(self, god_index: int) -> bool:
        """Activa el poder de un dios pagando su coste en Fe."""
        player = self.current_player
        if self.board_state.tinieblas_turnos_restantes > 0:
            self.log("Las Tinieblas impiden invocar los poderes divinos.")
            return False
        if god_index < 0 or god_index >= len(player.dioses_activos):
            return False

        god = player.dioses_activos[god_index]
        if player.tokens_fe < god.faith_cost:
            self.log(f"Fe insuficiente para invocar a {god.god_name} (Requiere {god.faith_cost} Fe).")
            return False

        player.tokens_fe -= god.faith_cost
        self._execute_god_effect(god, player)
        return True

    def _execute_god_effect(self, god: GodCard, player: Player):
        name = god.god_name.lower()
        if name == "ra":
            self.board_state.ira_de_dios = max(0, self.board_state.ira_de_dios - 3)
            self.log(f"Poder de Ra: La Ira de Dios disminuye en 3 (Total: {self.board_state.ira_de_dios}).")
        elif name == "seth":
            if self.board_state.bolsa_tumbas_egipcias:
                item = self.board_state.bolsa_tumbas_egipcias.pop()
                player.reserva_acolitos += 1
                self.log(f"Poder de Seth: Acólito recuperado de la Bolsa Negra a la reserva.")
            else:
                self.log("Bolsa Negra vacía; Seth no encuentra almas.")
        elif name == "osiris":
            self.board_state.cosechas["trigo"] = 0
            self.board_state.cosechas["avena"] = 0
            self.board_state.cosechas["cebada"] = 0
            self.log("Poder de Osiris: ¡Todas las cosechas vuelven a la abundancia absoluta (0)!")
        elif name == "horus":
            player.rerolls_disponibles += 2
            self.log(f"Poder de Horus: +2 relanzamientos concedidos a {player.nombre_faccion}.")
        elif name == "isis":
            for _ in range(3):
                self.board_state.bolsa_almacenamiento_fe.append(player.id)
            self.log(f"Poder de Isis: +3 tokens añadidos directamente a la Bolsa Azul.")
        elif name == "hathor":
            self.board_state.ganado += 3
            self.log(f"Poder de Hathor: +3 ganado a la reserva global.")
        elif name == "bastet":
            self.board_state.viviendas += 2
            player.tokens_fe += 1
            self.log(f"Poder de Bastet: +2 viviendas y +1 Fe personal.")
        else:
            player.tokens_fe += 2
            self.log(f"Bendición divina de {god.god_name}: +2 Fe.")

    # -------------------------------------------------------------
    # FASE 3: GRACIA DEL FARAÓN (RUEDA SOLAR)
    # -------------------------------------------------------------
    def roll_solar_wheel(self, inner_steps: int = 1, outer_steps: int = 0) -> Dict[str, Any]:
        """Tira el dado D6 de facción y gira las ruedas concéntricas."""
        player = self.current_player
        d6 = random.randint(1, 6)

        # Distribuir pasos según parámetros si coinciden con d6, de lo contrario distribuir automáticamente
        if inner_steps + outer_steps != d6:
            inner_steps = d6 // 2
            outer_steps = d6 - inner_steps

        res = resolve_solar_wheel(
            roll_total=d6,
            inner_steps=inner_steps,
            outer_steps=outer_steps,
            current_inner=self.board_state.rueda_solar_interna,
            current_outer=self.board_state.rueda_solar_externa,
            player=player
        )

        self.board_state.rueda_solar_interna = res["new_inner_idx"]
        self.board_state.rueda_solar_externa = res["new_outer_idx"]

        self.log(f"Rueda Solar (D6={d6} -> {inner_steps} interna, {outer_steps} externa): [{res['inner_symbol']}] alineado con [{res['outer_god']}].")

        if res["success"]:
            matched_god: GodCard = res["matched_god"]
            player.tokens_fe += 3
            self.log(f"¡¡ALINEACIÓN SAGRADA CON {matched_god.god_name.upper()}!!")
            self.log(f"¡Se activa gratis su poder '{matched_god.power_name}' y ganas +3 tokens de Fe!")
            self._execute_god_effect(matched_god, player)
        else:
            self.log("El disco solar no coincide con ningún dios activo de la facción.")

        self.turn_subphase = "TURN_END"
        return res

    # -------------------------------------------------------------
    # FINALIZACIÓN DE TURNO Y RONDA
    # -------------------------------------------------------------
    def end_turn(self):
        """Finaliza el turno actual y pasa al siguiente jugador."""
        player = self.current_player

        # Avanzar al siguiente jugador
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.turn_number += 1

        # Si volvemos al jugador 1, se completa una ronda
        if self.current_player_idx == 0:
            self.round_number += 1
            self.log(f"=== FIN DE RONDA {self.round_number - 1}. COMIENZA LA RONDA {self.round_number} ===")

            # Reactivar losetas usadas (salvo destruidas)
            for p in self.players:
                for tile in p.losetas_accion:
                    if tile.state == "usada_boca_abajo":
                        tile.state = "activa"

            # Reducir contador de Tinieblas
            if self.board_state.tinieblas_turnos_restantes > 0:
                self.board_state.tinieblas_turnos_restantes -= 1
                if self.board_state.tinieblas_turnos_restantes == 0:
                    self.log("¡Las Tinieblas se disipan! Los sacerdotes pueden orar de nuevo a los Dioses.")

        self.start_turn()

    # -------------------------------------------------------------
    # FLUJO ÉXODO B
    # -------------------------------------------------------------
    def step_exodus_b(self) -> Dict[str, Any]:
        """Ejecuta un paso en el motor de Éxodo B."""
        if not self.exodus_b_engine:
            return {"status": "error", "message": "Éxodo B no iniciado."}
        res = self.exodus_b_engine.execute_turn_phase_1_or_2()
        for msg in self.exodus_b_engine.log_messages[-3:]:
            if msg not in self.log_messages:
                self.log(msg)
        return res
