"""
Generador y gestor de mazos para The Scourge of Egypt:
- Mazo de Moisés (Plagas, Personajes Bíblicos, Eventos Bíblicos, Edificios Míticos)
- Mazo de Divinidades
- Mazo de Mandamientos (I al X)
"""
from __future__ import annotations
import random
from typing import List, Dict, Any
from scourge_egypt.models import PlagueCard, GodCard, CommandmentCard, ItemCard, Card


def build_moses_deck() -> List[Card]:
    deck: List[Card] = []

    # 1. Plagas de Sangre (4 cartas)
    for i in range(1, 5):
        deck.append(PlagueCard(
            id=f"plaga_sangre_{i}",
            name="Plaga de Sangre",
            card_type="plaga",
            description="El Nilo se tiñe de sangre. Elige: Avanzar Ira de Dios (2 + pot) O Sacrificar (2 + pot) acólitos.",
            plague_type="sangre",
            potency_base=2,
            has_commandment_symbol=True,
            wrath_increment=2,
            card_number=i
        ))

    # 2. Ranas / Langostas (Carta Doble) (4 cartas)
    for i in range(1, 5):
        deck.append(PlagueCard(
            id=f"plaga_ranas_langostas_{i}",
            name="Invasión de Ranas / Langostas",
            card_type="plaga",
            description="Carta Doble: Ranas voltean 3 losetas e Ira +1; Langostas voltean 3 losetas, +1 Fe e Ira +2. Avanza cosechas.",
            plague_type="ranas_langostas",
            potency_base=1,
            has_commandment_symbol=True,
            wrath_increment=1,
            card_number=i,
            sub_type="ranas"
        ))

    # 3. Moscas / Mosquitos / Ganado (5 cartas)
    deck.append(PlagueCard(
        id="plaga_moscas_1",
        name="Plaga de Moscas",
        card_type="plaga",
        description="Enjambres de moscas azotan las casas. Sacrificar 1 ganado (o 2 acólitos entre jugadores).",
        plague_type="moscas_ganado",
        potency_base=1,
        has_commandment_symbol=True,
        wrath_increment=1,
        sub_type="moscas"
    ))
    deck.append(PlagueCard(
        id="plaga_mosquitos_1",
        name="Plaga de Mosquitos",
        card_type="plaga",
        description="El polvo se convierte en mosquitos. Tirada D6: 1-3 (1 ganado), 4-5 (2 ganado), 6 (3 ganado).",
        plague_type="moscas_ganado",
        potency_base=1,
        has_commandment_symbol=True,
        wrath_increment=1,
        sub_type="mosquitos"
    ))
    for i in range(1, 4):
        deck.append(PlagueCard(
            id=f"plaga_ganado_{i}",
            name=f"Peste del Ganado #{i}",
            card_type="plaga",
            description="Mortalidad en los rebaños. Se acumula en mesa. En carta 3: 1/4 ganado; en carta 8: 1/2 ganado.",
            plague_type="moscas_ganado",
            potency_base=1,
            has_commandment_symbol=True,
            wrath_increment=1,
            sub_type="ganado",
            card_number=i
        ))

    # 4. Plaga de Úlceras (3 cartas)
    for i in range(1, 4):
        deck.append(PlagueCard(
            id=f"plaga_ulceras_{i}",
            name="Plaga de Úlceras e Infecciones",
            card_type="plaga",
            description="Ceniza arrojada al cielo produce sarpullidos. Cada jugador roba Divinidad: Mayoría Seth (sacrificio), Ra (revive acólito de Bolsa Negra).",
            plague_type="ulceras",
            potency_base=1,
            has_commandment_symbol=True,
            wrath_increment=1,
            card_number=i
        ))

    # 5. Plaga del Granizo y Fuego (3 cartas)
    for i in range(1, 4):
        deck.append(PlagueCard(
            id=f"plaga_granizo_{i}",
            name="Plaga del Granizo Devastador",
            card_type="plaga",
            description="Lluvia de hielo y fuego. Tirada D12 destruye 2 a 4 viviendas (+ pot). Por cada 2 viviendas destruidas, sacrificar 1 acólito.",
            plague_type="granizo",
            potency_base=2,
            has_commandment_symbol=True,
            wrath_increment=2,
            card_number=i
        ))

    # 6. Plaga de Tinieblas (2 cartas)
    for i in range(1, 3):
        deck.append(PlagueCard(
            id=f"plaga_tinieblas_{i}",
            name="Plaga de Tinieblas",
            card_type="plaga",
            description="Oscuridad total durante 3 turnos. Bloquea Divinidades y limita a 3 losetas. Activa Gracia Extraordinaria del Faraón.",
            plague_type="tinieblas",
            potency_base=1,
            has_commandment_symbol=True,
            wrath_increment=2,
            card_number=i
        ))

    # 7. Muerte de los Primogénitos (3 cartas)
    for i in range(1, 4):
        deck.append(PlagueCard(
            id=f"plaga_primogenitos_{i}",
            name=f"Ángel Exterminador: Primogénitos #{i}",
            card_type="plaga",
            description="Cada jugador envía (1 + pot) acólitos al Ángel Exterminador. En carta #10 todos son sacrificados a la Bolsa Negra.",
            plague_type="primogenitos",
            potency_base=1,
            has_commandment_symbol=True,
            wrath_increment=3,
            card_number=i
        ))

    # 8. Personajes Bíblicos (4 cartas)
    deck.append(Card(
        id="personaje_aaron",
        name="Aarón el Portavoz",
        card_type="personaje",
        description="Aarón extiende su vara. Añade de inmediato +1 cubo de mandamiento al altar de Moisés."
    ))
    deck.append(Card(
        id="personaje_miriam",
        name="Miriam la Profetisa",
        card_type="personaje",
        description="Canto de victoria. Cada jugador puede aportar 1 Fe a la Bolsa Azul para reducir 2 de Ira de Dios."
    ))
    deck.append(Card(
        id="personaje_jetro",
        name="Jetro de Madián",
        card_type="personaje",
        description="Consejo sabio a los líderes: Se reconstruyen +2 viviendas y +1 ganado a las reservas globales."
    ))
    deck.append(Card(
        id="personaje_josue",
        name="Josué el Conquistador",
        card_type="personaje",
        description="Inspiración bélica: Todos los jugadores recuperan 1 loseta destruida a su estado activo."
    ))

    # 9. Eventos Bíblicos (4 cartas)
    deck.append(Card(
        id="evento_zarza",
        name="La Zarza Ardiente",
        card_type="evento",
        description="La presencia divina estremece Egipto. Ira de Dios +2, pero se añade 1 cubo a mandamientos."
    ))
    deck.append(Card(
        id="evento_mana",
        name="Maná del Cielo",
        card_type="evento",
        description="El alimento cae del cielo. Se reducen 2 posiciones en todos los tracks de Cosecha (alivia la hambruna)."
    ))
    deck.append(Card(
        id="evento_columna_fuego",
        name="Columna de Fuego y Nube",
        card_type="evento",
        description="Disipa cualquier efecto de Tinieblas activo inmediatamente y otorga +1 Fe a cada jugador."
    ))
    deck.append(Card(
        id="evento_agua_roca",
        name="Agua brotando de la Peña",
        card_type="evento",
        description="Abundancia milagrosa: +3 ganado y +1 acólito a cada jugador que tenga menos de 3."
    ))

    # 10. Edificios Míticos (3 cartas)
    deck.append(ItemCard(
        id="edificio_granero",
        name="Granero Real de Menfis",
        card_type="edificio",
        description="Almacén fortificado: Las cosechas no pueden avanzar más allá de la posición 7 por plagas.",
        effect_type="granero"
    ))
    deck.append(ItemCard(
        id="edificio_portal_seguro",
        name="Portal Marcado (Portal Seguro)",
        card_type="edificio",
        description="La sangre del cordero en los postes: Inmunidad total al recuento de eliminaciones de la Bolsa Negra.",
        effect_type="portal_seguro"
    ))
    deck.append(ItemCard(
        id="edificio_templo_karnak",
        name="Templo Monumental de Karnak",
        card_type="edificio",
        description="Los sacerdotes consagran el templo: Permite usar 1 loseta extra por turno si la Ira de Dios es >= 20.",
        effect_type="templo"
    ))

    random.shuffle(deck)
    return deck


def build_gods_deck() -> List[GodCard]:
    gods: List[GodCard] = [
        GodCard(
            id="dios_ra",
            name="Ra, Señor del Sol",
            card_type="divinidad",
            description="Dios creador y soberano de la luz solar.",
            god_name="Ra",
            ra_symbols=2,
            seth_symbols=0,
            power_name="Resplandor Solar",
            power_description="-3 a la Ira de Dios global o +2 viviendas a la reserva.",
            faith_cost=2
        ),
        GodCard(
            id="dios_seth",
            name="Seth, Señor del Caos",
            card_type="divinidad",
            description="Señor de las tormentas, el desierto y la guerra.",
            god_name="Seth",
            ra_symbols=0,
            seth_symbols=2,
            power_name="Fuerza del Caos",
            power_description="Extrae 1 acólito de la Bolsa Negra y devuélvelo a tu reserva.",
            faith_cost=2
        ),
        GodCard(
            id="dios_osiris",
            name="Osiris, Señor de la Resurrección",
            card_type="divinidad",
            description="Gobernante del inframundo y la fertilidad agraria.",
            god_name="Osiris",
            ra_symbols=1,
            seth_symbols=1,
            power_name="Renovación del Nilo",
            power_description="Restaura un track de cereal a la posición 0.",
            faith_cost=2
        ),
        GodCard(
            id="dios_horus",
            name="Horus, el Halcón Vengador",
            card_type="divinidad",
            description="Hijo de Isis y Osiris, protector del Faraón y la justicia.",
            god_name="Horus",
            ra_symbols=1,
            seth_symbols=1,
            power_name="Ojo de Horus",
            power_description="Otorga 2 relanzamientos de dados (válidos en Éxodo A y Éxodo B).",
            faith_cost=1
        ),
        GodCard(
            id="dios_isis",
            name="Isis, Reina de la Magia",
            card_type="divinidad",
            description="Madre divina y maestra de las artes protectoras.",
            god_name="Isis",
            ra_symbols=2,
            seth_symbols=0,
            power_name="Aliento Sanador",
            power_description="Deposita +3 tokens directos en la Bolsa Azul de Fe.",
            faith_cost=2
        ),
        GodCard(
            id="dios_anubis",
            name="Anubis, Guía de las Almas",
            card_type="divinidad",
            description="Señor de la necrópolis y guardián del pesaje del corazón.",
            god_name="Anubis",
            ra_symbols=0,
            seth_symbols=2,
            power_name="Balanza de la Verdad",
            power_description="Evita el próximo sacrificio de acólitos que fueras a sufrir.",
            faith_cost=2
        ),
        GodCard(
            id="dios_thoth",
            name="Thoth, Sabio de los Jeroglíficos",
            card_type="divinidad",
            description="Dios del conocimiento, la escritura y el equilibrio cósmico.",
            god_name="Thoth",
            ra_symbols=1,
            seth_symbols=0,
            power_name="Registro Inmutable",
            power_description="Cancela y descarta la carta de plaga actual sin sufrir efectos.",
            faith_cost=3
        ),
        GodCard(
            id="dios_hathor",
            name="Hathor, Madre de la Fertilidad",
            card_type="divinidad",
            description="Diosa del amor, la música y la abundancia ganadera.",
            god_name="Hathor",
            ra_symbols=1,
            seth_symbols=1,
            power_name="Rebaños Sagrados",
            power_description="+3 cubos de ganado a la reserva global.",
            faith_cost=1
        ),
        GodCard(
            id="dios_bastet",
            name="Bastet, Protectora del Hogar",
            card_type="divinidad",
            description="Defensora felina contra los malos espíritus y las plagas.",
            god_name="Bastet",
            ra_symbols=1,
            seth_symbols=0,
            power_name="Guardián Doméstico",
            power_description="+2 viviendas a la reserva global y +1 Fe personal.",
            faith_cost=1
        ),
        GodCard(
            id="dios_sobek",
            name="Sobek, Fuerza del Cocodrilo",
            card_type="divinidad",
            description="Furia de las corrientes y potencia implacable.",
            god_name="Sobek",
            ra_symbols=0,
            seth_symbols=1,
            power_name="Empuje de la Marea",
            power_description="+2 casillas directas de avance para un carro en Éxodo B.",
            faith_cost=2
        )
    ]
    random.shuffle(gods)
    return gods


def build_commandments_deck() -> List[CommandmentCard]:
    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    texts = [
        ("No tendrás dioses ajenos delante de mí", "Límite estricto de máximo 3 Dioses activos por jugador en mesa."),
        ("No te harás imágenes talladas", "Cada jugador descarta 1 objeto mítico o debe pagar 1 token de Fe."),
        ("No tomarás el nombre en vano", "La Ira de Dios no puede reducirse bajo ninguna acción en esta ronda."),
        ("Acuérdate del día de reposo para santificarlo", "En el siguiente turno, cada jugador sólo puede usar 2 losetas de acción."),
        ("Honra a tu padre y a tu madre", "Cada facción recibe +1 acólito de refuerzo a su reserva."),
        ("No matarás", "Prohibido sacrificar acólitos voluntariamente durante los próximos 2 turnos."),
        ("No cometerás adulterio", "Cada jugador aporta obligatoriamente 1 Fe a la Bolsa Azul."),
        ("No hurtarás", "Si algún track de cosecha supera la posición 5, retrocede 1 casilla hacia la abundancia."),
        ("No darás falso testimonio", "Se comprueba la Bolsa Azul: Si tiene >= 15 fichas, la Ira de Dios baja 3 puntos."),
        ("No codiciarás los bienes ajenos", "El jugador con más acólitos cede 1 al jugador con menos. ¡Fin del Éxodo A!")
    ]

    deck = []
    for num, (name, desc) in enumerate(texts, start=1):
        deck.append(CommandmentCard(
            id=f"mandamiento_{num}",
            name=f"Mandamiento {romans[num-1]}",
            card_type="mandamiento",
            description=desc,
            number=num,
            roman_number=romans[num-1],
            effect_name=name
        ))
    return deck
