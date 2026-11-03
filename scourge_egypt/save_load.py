"""
Sistema de persistencia (Guardado y Carga de partidas en formato JSON)
para The Scourge of Egypt.
"""
from __future__ import annotations
import json
import os
from typing import Dict, Any, Optional
from scourge_egypt.models import BoardState, Player, Card, PlagueCard, GodCard, CommandmentCard, ItemCard
from scourge_egypt.game_engine import GameEngine


def serialize_card(card: Optional[Card]) -> Optional[Dict[str, Any]]:
    if not card:
        return None
    d = card.to_dict()
    d["_class"] = card.__class__.__name__
    return d


def deserialize_card(data: Optional[Dict[str, Any]]) -> Optional[Card]:
    if not data:
        return None
    cls_name = data.get("_class", "Card")
    if cls_name == "PlagueCard":
        return PlagueCard.from_dict(data)
    elif cls_name == "GodCard":
        return GodCard.from_dict(data)
    elif cls_name == "CommandmentCard":
        return CommandmentCard.from_dict(data)
    elif cls_name == "ItemCard":
        return ItemCard.from_dict(data)
    return Card(
        id=data["id"],
        name=data["name"],
        card_type=data["card_type"],
        description=data["description"]
    )


def save_game_to_file(engine: GameEngine, filepath: str = "partida_guardada.json") -> bool:
    try:
        data = {
            "num_players": engine.num_players,
            "turn_number": engine.turn_number,
            "round_number": engine.round_number,
            "current_player_idx": engine.current_player_idx,
            "turn_subphase": engine.turn_subphase,
            "actions_remaining_this_turn": engine.actions_remaining_this_turn,
            "regadios_used_this_turn": engine.regadios_used_this_turn,
            "board_state": engine.board_state.to_dict(),
            "players": [p.to_dict() for p in engine.players],
            "current_moses_card": serialize_card(engine.current_moses_card),
            "active_commandment": serialize_card(engine.active_commandment),
            "moses_deck": [serialize_card(c) for c in engine.moses_deck],
            "gods_deck": [serialize_card(g) for g in engine.gods_deck],
            "commandments_deck": [serialize_card(m) for m in engine.commandments_deck],
            "log_messages": engine.log_messages[-100:]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        engine.log(f"Partida guardada exitosamente en '{filepath}'.")
        return True
    except Exception as e:
        engine.log(f"Error al guardar la partida: {e}")
        return False


def load_game_from_file(filepath: str = "partida_guardada.json") -> Optional[GameEngine]:
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        engine = GameEngine(num_players=data["num_players"])
        engine.turn_number = data.get("turn_number", 1)
        engine.round_number = data.get("round_number", 1)
        engine.current_player_idx = data.get("current_player_idx", 0)
        engine.turn_subphase = data.get("turn_subphase", "DRAW_MOSES")
        engine.actions_remaining_this_turn = data.get("actions_remaining_this_turn", 4)
        engine.regadios_used_this_turn = data.get("regadios_used_this_turn", False)

        engine.board_state = BoardState.from_dict(data["board_state"])
        engine.players = [Player.from_dict(pd) for pd in data["players"]]

        engine.current_moses_card = deserialize_card(data.get("current_moses_card"))
        engine.active_commandment = deserialize_card(data.get("active_commandment"))

        if "moses_deck" in data:
            engine.moses_deck = [deserialize_card(c) for c in data["moses_deck"] if c]
        if "gods_deck" in data:
            engine.gods_deck = [deserialize_card(g) for g in data["gods_deck"] if g]
        if "commandments_deck" in data:
            engine.commandments_deck = [deserialize_card(m) for m in data["commandments_deck"] if m]

        engine.log_messages = data.get("log_messages", [])
        engine.log(f"Partida cargada exitosamente desde '{filepath}'.")
        return engine
    except Exception as e:
        print(f"Error al cargar la partida: {e}")
        return None
