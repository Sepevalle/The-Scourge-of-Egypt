"""
Modelos de datos y entidades para The Scourge of Egypt.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any


@dataclass
class Acolito:
    player_id: int
    faction_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {"player_id": self.player_id, "faction_name": self.faction_name}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Acolito:
        return cls(player_id=data["player_id"], faction_name=data["faction_name"])


@dataclass
class ActionTile:
    id_name: str               # e.g., 'COSECHAR'
    name: str                  # Display name
    description: str
    symbol_type: str           # '1 Ra', '1 Seth', '1 Ra / 1 Seth', '2 Ra', '2 Seth'
    state: str = "activa"      # 'activa', 'usada_boca_abajo', 'destruida'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_name": self.id_name,
            "name": self.name,
            "description": self.description,
            "symbol_type": self.symbol_type,
            "state": self.state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ActionTile:
        return cls(
            id_name=data["id_name"],
            name=data["name"],
            description=data["description"],
            symbol_type=data["symbol_type"],
            state=data.get("state", "activa")
        )


@dataclass
class Card:
    id: str
    name: str
    card_type: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "card_type": self.card_type,
            "description": self.description
        }


@dataclass
class PlagueCard(Card):
    plague_type: str = ""       # 'sangre', 'ranas_langostas', 'moscas_ganado', 'ulceras', 'granizo', 'tinieblas', 'primogenitos', etc.
    potency_base: int = 1
    has_commandment_symbol: bool = True
    wrath_increment: int = 1
    card_number: int = 1
    sub_type: str = ""          # for double cards: 'ranas' or 'langostas', 'moscas', 'mosquitos', 'ganado'
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "plague_type": self.plague_type,
            "potency_base": self.potency_base,
            "has_commandment_symbol": self.has_commandment_symbol,
            "wrath_increment": self.wrath_increment,
            "card_number": self.card_number,
            "sub_type": self.sub_type,
            "extra_data": self.extra_data
        })
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlagueCard:
        return cls(
            id=data["id"],
            name=data["name"],
            card_type=data["card_type"],
            description=data["description"],
            plague_type=data.get("plague_type", ""),
            potency_base=data.get("potency_base", 1),
            has_commandment_symbol=data.get("has_commandment_symbol", True),
            wrath_increment=data.get("wrath_increment", 1),
            card_number=data.get("card_number", 1),
            sub_type=data.get("sub_type", ""),
            extra_data=data.get("extra_data", {})
        )


@dataclass
class GodCard(Card):
    god_name: str = ""
    ra_symbols: int = 0
    seth_symbols: int = 0
    power_name: str = ""
    power_description: str = ""
    faith_cost: int = 1

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "god_name": self.god_name,
            "ra_symbols": self.ra_symbols,
            "seth_symbols": self.seth_symbols,
            "power_name": self.power_name,
            "power_description": self.power_description,
            "faith_cost": self.faith_cost
        })
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GodCard:
        return cls(
            id=data["id"],
            name=data["name"],
            card_type=data["card_type"],
            description=data["description"],
            god_name=data.get("god_name", ""),
            ra_symbols=data.get("ra_symbols", 0),
            seth_symbols=data.get("seth_symbols", 0),
            power_name=data.get("power_name", ""),
            power_description=data.get("power_description", ""),
            faith_cost=data.get("faith_cost", 1)
        )


@dataclass
class CommandmentCard(Card):
    number: int = 1
    roman_number: str = "I"
    effect_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "number": self.number,
            "roman_number": self.roman_number,
            "effect_name": self.effect_name
        })
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CommandmentCard:
        return cls(
            id=data["id"],
            name=data["name"],
            card_type=data["card_type"],
            description=data["description"],
            number=data.get("number", 1),
            roman_number=data.get("roman_number", "I"),
            effect_name=data.get("effect_name", "")
        )


@dataclass
class ItemCard(Card):
    effect_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["effect_type"] = self.effect_type
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ItemCard:
        return cls(
            id=data["id"],
            name=data["name"],
            card_type=data["card_type"],
            description=data["description"],
            effect_type=data.get("effect_type", "")
        )


@dataclass
class Carro:
    player_id: int
    carro_id: int
    position: int = 0          # 0: Salida; 1..19: Torbellino; 20..30: Mar Rojo
    status: str = "espera"     # 'espera', 'en_carrera', 'escapado', 'destruido'
    reverse_to_20: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "carro_id": self.carro_id,
            "position": self.position,
            "status": self.status,
            "reverse_to_20": self.reverse_to_20
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Carro:
        return cls(
            player_id=data["player_id"],
            carro_id=data["carro_id"],
            position=data.get("position", 0),
            status=data.get("status", "espera"),
            reverse_to_20=data.get("reverse_to_20", False)
        )


FACTIONS_DEF = [
    {
        "name": "Sacerdotes de Ra",
        "color": (230, 160, 40),      # Gold / Orange
        "bonus_desc": "+1 al rezar o activar poderes solares."
    },
    {
        "name": "Servidores de Seth",
        "color": (190, 40, 50),       # Deep Red
        "bonus_desc": "Mayor resistencia ante pérdidas de acólitos."
    },
    {
        "name": "Discípulos de Osiris",
        "color": (30, 150, 90),       # Green
        "bonus_desc": "+1 adicional al renovar cosechas y alimentos."
    },
    {
        "name": "Seguidores de Horus",
        "color": (30, 120, 210),      # Blue
        "bonus_desc": "Bonificación en tiradas de combate y avance en Éxodo B."
    },
    {
        "name": "Novicios de Isis",
        "color": (160, 60, 190),      # Purple
        "bonus_desc": "Mayor afinidad con la Fe y almacenamiento de fichas."
    }
]


def create_default_action_tiles() -> List[ActionTile]:
    return [
        ActionTile(
            id_name="COSECHAR",
            name="Cosechar",
            description="+2 a un track de cereal elegido (Trigo, Avena o Cebada)",
            symbol_type="1 Ra"
        ),
        ActionTile(
            id_name="REZAR",
            name="Rezar",
            description="-2 al marcador global de Ira de Dios",
            symbol_type="1 Ra / 1 Seth"
        ),
        ActionTile(
            id_name="GANADERIA",
            name="Ganadería",
            description="+2 a la reserva de ganado",
            symbol_type="1 Seth"
        ),
        ActionTile(
            id_name="REGADIOS",
            name="Regadíos",
            description="Permite usar 1 loseta adicional este turno pagando 1 Fe",
            symbol_type="1 Ra"
        ),
        ActionTile(
            id_name="RENACIMIENTO",
            name="Renacimiento",
            description="+2 acólitos a tu reserva personal",
            symbol_type="1 Seth"
        ),
        ActionTile(
            id_name="RECONSTRUCCION",
            name="Reconstrucción",
            description="+2 viviendas a la reserva global",
            symbol_type="2 Ra"
        ),
        ActionTile(
            id_name="DIOSES_FAVORABLES",
            name="Dioses Favorables",
            description="Otorga 1 relanzamiento de dados para cualquier tirada",
            symbol_type="2 Seth"
        ),
        ActionTile(
            id_name="RENDIR_PLEITESIA",
            name="Rendir Pleitesía",
            description="+2 tokens de Fe a tu reserva personal",
            symbol_type="1 Ra / 1 Seth"
        )
    ]


@dataclass
class Player:
    id: int
    nombre_faccion: str
    color: Tuple[int, int, int]
    reserva_acolitos: int = 5
    tokens_fe: int = 3
    losetas_accion: List[ActionTile] = field(default_factory=create_default_action_tiles)
    dioses_activos: List[GodCard] = field(default_factory=list)
    objetos_activos: List[ItemCard] = field(default_factory=list)
    carros_exodo_b: List[Carro] = field(default_factory=list)
    eliminado: bool = False
    tiene_portal_seguro: bool = False
    rerolls_disponibles: int = 0
    ulceras_deuda_turnos: int = 0     # Ulcers tie penalty (2 turns must sacrifice 1 acolyte)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nombre_faccion": self.nombre_faccion,
            "color": list(self.color),
            "reserva_acolitos": self.reserva_acolitos,
            "tokens_fe": self.tokens_fe,
            "losetas_accion": [t.to_dict() for t in self.losetas_accion],
            "dioses_activos": [g.to_dict() for g in self.dioses_activos],
            "objetos_activos": [o.to_dict() for o in self.objetos_activos],
            "carros_exodo_b": [c.to_dict() for c in self.carros_exodo_b],
            "eliminado": self.eliminado,
            "tiene_portal_seguro": self.tiene_portal_seguro,
            "rerolls_disponibles": self.rerolls_disponibles,
            "ulceras_deuda_turnos": self.ulceras_deuda_turnos
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Player:
        p = cls(
            id=data["id"],
            nombre_faccion=data["nombre_faccion"],
            color=tuple(data["color"]),
            reserva_acolitos=data.get("reserva_acolitos", 5),
            tokens_fe=data.get("tokens_fe", 3),
            eliminado=data.get("eliminado", False),
            tiene_portal_seguro=data.get("tiene_portal_seguro", False),
            rerolls_disponibles=data.get("rerolls_disponibles", 0),
            ulceras_deuda_turnos=data.get("ulceras_deuda_turnos", 0)
        )
        p.losetas_accion = [ActionTile.from_dict(t) for t in data.get("losetas_accion", [])]
        p.dioses_activos = [GodCard.from_dict(g) for g in data.get("dioses_activos", [])]
        p.objetos_activos = [ItemCard.from_dict(o) for o in data.get("objetos_activos", [])]
        p.carros_exodo_b = [Carro.from_dict(c) for c in data.get("carros_exodo_b", [])]
        return p


@dataclass
class BoardState:
    ira_de_dios: int = 0
    cosechas: Dict[str, int] = field(default_factory=lambda: {"trigo": 0, "avena": 0, "cebada": 0})
    ganado: int = 20
    viviendas: int = 25
    bolsa_tumbas_egipcias: List[Any] = field(default_factory=list)      # Contains Acolito or "ganado"
    bolsa_almacenamiento_fe: List[int] = field(default_factory=list)    # Contains player_ids of donated tokens
    cubos_mandamiento: int = 0                                         # 0..5 white cubes
    mandamiento_actual: int = 1                                        # 1..10 (I to X)
    cartas_sangre_en_mesa: int = 0
    cartas_ganado_en_mesa: int = 0
    acolitos_angel_exterminador: List[Acolito] = field(default_factory=list)
    tinieblas_turnos_restantes: int = 0
    fase_actual: str = "EXODUS_A"                                       # 'EXODUS_A', 'TRANSICION', 'EXODUS_B', 'VICTORIA', 'DERROTA'
    rueda_solar_interna: int = 0                                       # 0..3 (Sol radiante, Eclipse, etc.)
    rueda_solar_externa: int = 0                                       # 0..7 (Nombres de dioses)
    casillas_activas_mar_rojo: int = 30                                # Casillas activas en éxodo B
    segundo_carro_en_20: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ira_de_dios": self.ira_de_dios,
            "cosechas": dict(self.cosechas),
            "ganado": self.ganado,
            "viviendas": self.viviendas,
            "bolsa_tumbas_egipcias": [
                item.to_dict() if isinstance(item, Acolito) else item
                for item in self.bolsa_tumbas_egipcias
            ],
            "bolsa_almacenamiento_fe": list(self.bolsa_almacenamiento_fe),
            "cubos_mandamiento": self.cubos_mandamiento,
            "mandamiento_actual": self.mandamiento_actual,
            "cartas_sangre_en_mesa": self.cartas_sangre_en_mesa,
            "cartas_ganado_en_mesa": self.cartas_ganado_en_mesa,
            "acolitos_angel_exterminador": [a.to_dict() for a in self.acolitos_angel_exterminador],
            "tinieblas_turnos_restantes": self.tinieblas_turnos_restantes,
            "fase_actual": self.fase_actual,
            "rueda_solar_interna": self.rueda_solar_interna,
            "rueda_solar_externa": self.rueda_solar_externa,
            "casillas_activas_mar_rojo": self.casillas_activas_mar_rojo,
            "segundo_carro_en_20": self.segundo_carro_en_20
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BoardState:
        bs = cls(
            ira_de_dios=data.get("ira_de_dios", 0),
            cosechas=data.get("cosechas", {"trigo": 0, "avena": 0, "cebada": 0}),
            ganado=data.get("ganado", 20),
            viviendas=data.get("viviendas", 25),
            bolsa_almacenamiento_fe=data.get("bolsa_almacenamiento_fe", []),
            cubos_mandamiento=data.get("cubos_mandamiento", 0),
            mandamiento_actual=data.get("mandamiento_actual", 1),
            cartas_sangre_en_mesa=data.get("cartas_sangre_en_mesa", 0),
            cartas_ganado_en_mesa=data.get("cartas_ganado_en_mesa", 0),
            tinieblas_turnos_restantes=data.get("tinieblas_turnos_restantes", 0),
            fase_actual=data.get("fase_actual", "EXODUS_A"),
            rueda_solar_interna=data.get("rueda_solar_interna", 0),
            rueda_solar_externa=data.get("rueda_solar_externa", 0),
            casillas_activas_mar_rojo=data.get("casillas_activas_mar_rojo", 30),
            segundo_carro_en_20=data.get("segundo_carro_en_20", False)
        )
        bs.bolsa_tumbas_egipcias = [
            Acolito.from_dict(it) if isinstance(it, dict) else it
            for it in data.get("bolsa_tumbas_egipcias", [])
        ]
        bs.acolitos_angel_exterminador = [
            Acolito.from_dict(a) for a in data.get("acolitos_angel_exterminador", [])
        ]
        return bs
