# MANUAL COMPLETO Y DOCUMENTACIÓN TÉCNICA
## THE SCOURGE OF EGYPT (El Azote de Egipto)

---

## 1. RESUMEN EJECUTIVO Y VISIÓN GENERAL

**The Scourge of Egypt** es una adaptación digital fiel en **Python y Pygame** del juego de mesa histórico-bíblico homónimo. Implementa una arquitectura **Modelo-Vista-Controlador (MVC)** desacoplada, orientada a objetos (POO), que separa estrictamente la validación y ejecución de las reglas de juego de la capa gráfica y de eventos multimedia.

El juego admite partidas multijugador local (*hot-seat*) de **1 a 4 jugadores**, estructuradas en dos grandes actos complementarios:
1. **Éxodo A:** Las 10 Plagas de Egipto, gestión de hambrunas agrarias, acumulación de fe, construcción de defensas míticas, culto divino en la Rueda Solar y el avance implacable del meeple de Moisés a lo largo de las Tablas de la Ley.
2. **Éxodo B (La Persecución en el Mar Rojo):** Carrera de supervivencia sobre un circuito de 30 casillas donde los acólitos supervivientes conducen carros de combate a través del torbellino de fuego y el lecho marino antes de que las aguas colapsen.

---

## 2. ARQUITECTURA DEL SISTEMA (MVC)

El motor está estructurado siguiendo principios limpios de desacoplamiento:

```
+---------------------------------------------------------------------------------+
|                                    MAIN.PY                                      |
|            Controlador del bucle principal Pygame (Ticks a 60 FPS)              |
+---------------------------------------+-----------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
+----------------v--------------------+       +----------------v------------------+
|          CAPA LÓGICA (MODEL)        |       |        CAPA GRÁFICA (VIEW)        |
| - scourge_egypt/models.py           |       | - scourge_egypt/ui/game_screen.py |
| - scourge_egypt/decks.py            |       | - scourge_egypt/ui/board_renderer |
| - scourge_egypt/rules.py            |       | - scourge_egypt/ui/solar_wheel_ui |
| - scourge_egypt/game_engine.py      |       | - scourge_egypt/ui/tile_grid_ui.py|
| - scourge_egypt/exodus_b_engine.py  |       | - scourge_egypt/ui/exodus_b_view  |
| - scourge_egypt/save_load.py        |       | - scourge_egypt/ui/audio.py       |
+-------------------------------------+       +-----------------------------------+
```

---

## 3. ESTRUCTURA DE FICHEROS Y MÓDULOS

```
c:\Users\josep\Desktop\The Scourge of Egypt\
├── The Scourge of Egypt_especificaciones.md   # Pliego de especificaciones original
├── DOCUMENTACION_COMPLETA.md                   # Este manual técnico y de reglas
├── main.py                                     # Punto de entrada de la aplicación
├── tests/                                      # Suite de pruebas automatizadas
│   ├── test_models.py                          # Tests de modelos y serialización
│   ├── test_rules.py                           # Tests de reglas, hambruna y bolsas
│   ├── test_engine.py                          # Tests del motor de turnos y guardado
│   ├── test_exodus_b.py                        # Tests del circuito del Mar Rojo
│   └── test_ui.py                              # Tests de interfaz headless
└── scourge_egypt/                              # Paquete central del motor
    ├── __init__.py
    ├── models.py                               # Entidades y estructuras de datos
    ├── decks.py                                # Generación de mazos (Moisés, Dioses, Mandamientos)
    ├── rules.py                                # Fórmulas, algoritmos de plagas y sol
    ├── game_engine.py                          # Máquina de estados de Éxodo A
    ├── exodus_b_engine.py                      # Motor de la persecución y carros
    ├── save_load.py                            # Persistencia en JSON
    └── ui/
        ├── __init__.py
        ├── theme.py                            # Paleta cromática egipcia y fuentes
        ├── audio.py                            # Síntesis procedural de sonido (NumPy + Mixer)
        ├── components.py                       # Botones con hover, modales y logger
        ├── solar_wheel_ui.py                   # Renderizado animado de la Rueda Solar
        ├── tile_grid_ui.py                     # Grid de las 8 losetas de acción
        ├── board_renderer.py                   # Renderizado del tablero Éxodo A
        ├── exodus_b_view.py                    # Circuito de 30 casillas de Éxodo B
        └── game_screen.py                      # Coordinador de pantallas y estados
```

---

## 4. MODELOS DE DATOS (`models.py`)

### 4.1. `Player` (Jugador / Facción)
Representa a una facción sacerdotal del Antiguo Egipto:
- `id`: Identificador numérico ($1..4$).
- `nombre_faccion`: Nombre canónico (*Sacerdotes de Ra*, *Servidores de Seth*, *Discípulos de Osiris*, *Seguidores de Horus*, *Novicios de Isis*).
- `color`: Tupla RGB con el color heráldico de la facción.
- `reserva_acolitos`: Cubos de acólitos personales en reserva (inicial: 5).
- `tokens_fe`: Fichas de Fe personal (inicial: 3).
- `losetas_accion`: Lista de 8 objetos `ActionTile`.
- `dioses_activos`: Lista de `GodCard` en mesa (máximo 3 tras Mandamiento I).
- `objetos_activos`: Lista de `ItemCard` o edificios míticos construidos.
- `carros_exodo_b`: Lista de objetos `Carro` para la fase de persecución.
- `eliminado`: Booleano que indica si la facción fue destruida en el recuento de sacrificios.
- `tiene_portal_seguro`: Booleano que otorga inmunidad en el umbral de sacrificios.
- `rerolls_disponibles`: Contador de relanzamientos de dados acumulados.

### 4.2. `ActionTile` (Loseta de Acción)
- `id_name`: Clave única (`COSECHAR`, `REZAR`, `GANADERIA`, `REGADIOS`, `RENACIMIENTO`, `RECONSTRUCCION`, `DIOSES_FAVORABLES`, `RENDIR_PLEITESIA`).
- `name`: Nombre visible en la interfaz.
- `description`: Explicación de la acción.
- `symbol_type`: Icono divino impreso (`1 Ra`, `1 Seth`, `1 Ra / 1 Seth`, `2 Ra`, `2 Seth`).
- `state`: Estado actual:
  - `"activa"`: Disponible para usarse en el turno actual (brillo dorado).
  - `"usada_boca_abajo"`: Utilizada durante esta ronda; se reactiva al completar la ronda.
  - `"destruida"`: Destruida por penalizaciones de plagas; requiere cartas de milagro para repararse.

### 4.3. `BoardState` (Estado Global del Tablero)
- `ira_de_dios`: Entero $[0..50]$. Mide el enojo celestial.
- `cosechas`: Diccionario con los 3 cultivos (`trigo`, `avena`, `cebada`), cada uno en el rango $[0..10]$.
- `ganado`: Reserva comunitaria de cubos blancos.
- `viviendas`: Reserva comunitaria de cubos grises. Si llega a $0$, derrota inmediata.
- `bolsa_tumbas_egipcias`: Bolsa Negra donde se depositan acólitos sacrificados y ganado muerto.
- `bolsa_almacenamiento_fe`: Bolsa Azul comunitaria con las fichas de Fe aportadas por los jugadores.
- `cubos_mandamiento`: Cubos blancos acumulados en el altar $[0..5]$.
- `mandamiento_actual`: Casilla del meeple de Moisés $[1..10]$ (del Mandamiento I al X).
- `cartas_sangre_en_mesa`: Conteo acumulado de plagas de sangre.
- `cartas_ganado_en_mesa`: Conteo acumulado de plagas de peste del ganado.
- `acolitos_angel_exterminador`: Acólitos retenidos en el umbral por la plaga de primogénitos.
- `tinieblas_turnos_restantes`: Duración restante del bloqueo de Tinieblas.
- `casillas_activas_mar_rojo`: Casillas abiertas en Éxodo B (comienza en 30 y va colapsando).

---

## 5. GENERACIÓN Y GESTIÓN DE MAZOS (`decks.py`)

### 5.1. Mazo de Moisés
Compuesto por una selección equilibrada de:
1. **Plagas Bíblicas (Cartas de Plaga):**
   - Sangre (4 cartas)
   - Invasión de Ranas / Langostas (Carta doble, 4 cartas)
   - Moscas, Mosquitos y Peste del Ganado (5 cartas)
   - Plaga de Úlceras (3 cartas)
   - Plaga del Granizo Devastador (3 cartas)
   - Plaga de Tinieblas (2 cartas)
   - Ángel Exterminador / Primogénitos (3 cartas)
2. **Personajes Bíblicos:**
   - *Aarón el Portavoz:* Añade inmediatamente +1 cubo al altar de Mandamientos.
   - *Miriam la Profetisa:* Permite orar y aportar Fe para reducir la Ira de Dios.
   - *Jetro de Madián:* Sabiduría administrativa: +2 viviendas y +1 ganado a las reservas globales.
   - *Josué el Conquistador:* Restaura una loseta destruida de cada facción a su estado activo.
3. **Eventos Sagrados:**
   - *La Zarza Ardiente:* Ira de Dios +2 y añade +1 cubo a los Mandamientos.
   - *Maná del Cielo:* Alivia el hambre reduciendo 2 posiciones en todos los tracks de Cosecha.
   - *Columna de Fuego:* Disipa las Tinieblas y otorga +1 Fe a cada jugador.
   - *Agua de la Peña:* Milagro en el desierto: +3 ganado y apoyo a facciones necesitadas.
4. **Edificios Míticos:**
   - *Granero Real de Menfis:* Impide que las plagas avancen las cosechas más allá de la casilla 7.
   - *Portal Seguro:* Otorga salvoconducto contra el recuento de sacrificios de la Bolsa Negra.
   - *Templo Monumental de Karnak:* Otorga acciones adicionales si la Ira de Dios es $\ge 20$.

### 5.2. Mazo de Divinidades (Dioses Egipcios)
Cada carta contiene símbolos de culto y un poder especial:
- **Ra:** 2 Ra | Poder: *Resplandor Solar* (-3 Ira de Dios o +2 viviendas).
- **Seth:** 2 Seth | Poder: *Fuerza del Caos* (Resucita 1 acólito de la Bolsa Negra).
- **Osiris:** 1 Ra, 1 Seth | Poder: *Renovación del Nilo* (Restaura todas las cosechas a 0).
- **Horus:** 1 Ra, 1 Seth | Poder: *Ojo de Horus* (Concede 2 relanzamientos de dados).
- **Isis:** 2 Ra | Poder: *Aliento Sanador* (Aporta +3 fichas a la Bolsa Azul de Fe).
- **Anubis:** 2 Seth | Poder: *Balanza de la Verdad* (Protege contra el siguiente sacrificio).
- **Thoth:** 1 Ra | Poder: *Registro Inmutable* (Descarta una carta de plaga sin sufrir efectos).
- **Hathor:** 1 Ra, 1 Seth | Poder: *Rebaños Sagrados* (+3 ganado a la reserva global).
- **Bastet:** 1 Ra | Poder: *Guardián Doméstico* (+2 viviendas y +1 Fe personal).
- **Sobek:** 1 Seth | Poder: *Empuje de la Marea* (+2 casillas directas de avance en Éxodo B).

### 5.3. Mazo de los Diez Mandamientos (I al X)
- **I:** Límite estricto de máximo 3 Dioses activos por facción.
- **II:** Descartar 1 objeto mítico o pagar 1 token de Fe.
- **III:** Prohibido reducir la Ira de Dios durante la ronda.
- **IV:** Día de reposo: Sólo 2 losetas de acción permitidas en el siguiente turno.
- **V:** Honra a tu padre y a tu madre: +1 acólito de refuerzo a cada jugador.
- **VI:** Prohibido el sacrificio voluntario de acólitos durante 2 turnos.
- **VII:** Aporte obligatorio de 1 Fe de cada jugador a la Bolsa Azul.
- **VIII:** Si las cosechas están $\ge 5$, retroceden 1 casilla hacia la abundancia.
- **IX:** Comprobación de la Bolsa Azul: si contiene $\ge 15$ fichas, reduce 3 puntos la Ira de Dios.
- **X:** Solidaridad: La facción con más acólitos cede 1 a la más desfavorecida. **¡Culmina el Éxodo A!**

---

## 6. LÓGICA DE REGLAS EN ÉXODO A (`rules.py` y `game_engine.py`)

### 6.1. Reservas Iniciales según Jugadores
| Jugadores | Ganado Inicial | Viviendas Iniciales | Fe requerida en Bolsa Azul |
| :---: | :---: | :---: | :---: |
| **1 Jugador** | 15 cubos | 20 cubos | 15 tokens |
| **2 Jugadores** | 20 cubos | 25 cubos | 25 tokens |
| **3 Jugadores** | 30 cubos | 35 cubos | 35 tokens |
| **4 Jugadores** | 40 cubos | 40 cubos | 45 tokens |

### 6.2. Algoritmo de Potenciación por Ira de Dios
$$\text{Potenciación} = \begin{cases} 0 & \text{si } \text{Ira} < 20 \\ 1 & \text{si } 20 \le \text{Ira} < 40 \\ 2 & \text{si } \text{Ira} \ge 40 \end{cases}$$

### 6.3. Tracks de Cosechas y Hambruna
- Cada cultivo (Trigo, Avena, Cebada) avanza hacia la derecha ($0 \rightarrow 10$).
- **Línea de Alerta ($\ge 5$):** Aviso visual de hambruna inminente.
- **Agotamiento Total ($= 10$):** El cultivo colapsa y provoca la pérdida inmediata de 1 cubo de ganado hacia la Bolsa Negra.

### 6.4. Las 8 Losetas de Acción Básicas
1. **COSECHAR:** Selecciona Trigo, Avena o Cebada y reduce en 2 su marcador, mitigando la hambruna.
2. **REZAR:** Reduce en 2 el marcador global de Ira de Dios.
3. **GANADERÍA:** Suma +2 cubos blancos a la reserva de ganado.
4. **REGADÍOS:** Otorga 1 acción adicional este turno a cambio de pagar 1 token de Fe.
5. **RENACIMIENTO:** Suma +2 acólitos a la reserva personal de la facción.
6. **RECONSTRUCCIÓN:** Suma +2 viviendas a la reserva global.
7. **DIOSES FAVORABLES:** Concede 1 relanzamiento de dados disponible para tiradas críticas.
8. **RENDIR PLEITESÍA:** Otorga +2 tokens de Fe a la reserva personal.

### 6.5. Resolución de las 10 Plagas
1. **Plaga de Sangre:**
   - Diálogo modal con elección obligatoria: Aumentar la Ira de Dios en $(2 + \text{pot})$ O Sacrificar $(2 + \text{pot})$ acólitos a la Bolsa Negra.
   - Si se acumulan 8 cartas de sangre en mesa: Todos sacrifican 1 acólito (salvo quienes posean $\ge 3$ Fe) y la Ira aumenta +1.
2. **Ranas / Langostas (Carta Doble):**
   - Ranas: Voltea 3 losetas activas e incrementa Ira en +1.
   - Langostas: Voltea 3 losetas, suma +1 Fe e incrementa Ira en +2.
   - Tirada de Moisés (D12): $1-4$ avanza Trigo; $5-8$ avanza Avena; $9-12$ avanza Cebada.
3. **Moscas / Mosquitos / Ganado:**
   - Moscas: Sacrifica 1 ganado (o 2 acólitos).
   - Mosquitos: Tirada D6 determina la pérdida de 1 a 3 cabezas de ganado.
   - Peste de Ganado: Al acumular la 3ª carta se sacrifica $1/4$ del ganado; con la 8ª carta se sacrifica la mitad.
4. **Plaga de Úlceras:**
   - Se revelan cartas de divinidad para contabilizar símbolos Ra vs Seth. Si domina Seth, todos sacrifican 1 acólito. Si domina Ra, se extrae un alma de la Bolsa Negra que resucita. Si hay empate, la facción activa sufre una deuda de sacrificios por 2 turnos.
5. **Plaga de Granizo:**
   - Dado D12 de Moisés destruye de 2 a 4 viviendas $(+ \text{pot})$. Por cada 2 viviendas destruidas, los jugadores deben sacrificar 1 acólito.
6. **Plaga de Tinieblas:**
   - Oscuridad total durante 3 turnos: prohíbe invocar y usar divinidades, y limita las acciones por turno a 3. Se activa una sesión extraordinaria de la Gracia del Faraón.
7. **Muerte de los Primogénitos:**
   - Los jugadores entregan $(1 + \text{pot})$ acólitos al Ángel Exterminador. En la carta 10, todos son arrastrados a la Bolsa Negra (salvo quien posea el *Portal Seguro*).

### 6.6. La Rueda Solar (Gracia del Faraón)
La Rueda Solar interactiva consta de:
- **Anillo Exterior (8 Dioses):** Ra, Seth, Osiris, Horus, Isis, Anubis, Thoth, Hathor.
- **Anillo Interior (4 Fases Solares):** SOL RADIANTE, ECLIPSE, SOL NACIENTE, SOL PONIENTE.

El jugador activo lanza su D6 y distribuye el avance angular entre ambos anillos. Si el **SOL RADIANTE** coincide en el cenit con un **Dios Activo** de su facción:
- ¡Se activa el poder sagrado de ese Dios **completamente gratis** (sin coste en Fe)!
- La facción recibe además una bonificación de **+3 tokens de Fe**.

---

## 7. CONDICIONES DE VICTORIA Y TRANSICIÓN (FIN DE ÉXODO A)

Al alcanzar el meeple de Moisés la casilla **X** (Mandamiento 10), el motor evalúa las tres condiciones canónicas en orden estricto:

```python
def verificar_condiciones_exodo_a(board_state, players):
    # Condición 1: Viviendas
    if board_state.viviendas <= 0:
        return False, "DERROTA: Todas las viviendas fueron destruidas.", []
    
    # Condición 2: Almacenamiento de Fe (Bolsa Azul)
    req = REQUISITO_FE_EXODO_A.get(len(players), 45)
    total_fe = len(board_state.bolsa_almacenamiento_fe)
    if total_fe < req:
        return False, f"DERROTA: Fe insuficiente en la Bolsa Azul ({total_fe}/{req}).", []
    
    # Condición 3: Recuento de Sacrificios (Bolsa Negra)
    # Se elimina la facción que más acólitos sacrificó, salvo si tiene Portal Seguro
    ...
```

Si al menos una facción sobrevive, el juego realiza una transición automática a la **Fase Éxodo B**.

---

## 8. REGLAS DE ÉXODO B: LA PERSECUCIÓN EN EL MAR ROJO (`exodus_b_engine.py`)

El tablero se transforma en un circuito de **30 casillas**:
- Cada facción convierte sus acólitos restantes en **Carros de Combate** (máximo 3).
- El primer carro inicia en la casilla 1; los demás aguardan en la salida.

### 8.1. Fase I: Torbellino de Fuego (Casillas 1 a 19)
- En su turno, el jugador lanza su Dado de Facción (D6), roba 1 carta de Divinidad (obteniendo símbolos Ra + Seth) y lanza el Dado de Moisés (D12).
$$\text{Avance} = (\text{D6} + \text{Símbolos Divinos}) - \text{D12}$$
- **Si Avance $> 0$:** El carro avanza ese número de casillas (hasta un máximo de la casilla 20).
- **Si Avance $\le 0$:** El carro se detiene. El jugador puede elegir **Arriesgar** gastando 1 cubo de reserva:
  - Roba una carta del mazo de Moisés. Si la carta posee icono de avance de Ira ($+1$ o $+2$), el carro avanza esas casillas.
  - Si no posee icono de avance, **¡el carro queda DESTRUIDO!**

### 8.2. Fase II: Internarse en el Mar Rojo (Casillas 20 a 30)
- Se activa al pisar la casilla 20.
- Los avances exitosos mueven **estrictamente 1 casilla**.
- Los resultados negativos fuerzan la prueba de arriesgar de forma automática sin gastar cubos extras.
- Alcanzar la casilla 20 permite introducir un **2º carro** en carrera desde la salida.

### 8.3. Subfase II: Las Aguas Empiezan a Cerrarse
- Se activa cuando un **segundo carro** (del mismo o diferente jugador) alcanza la casilla 20.
- **¡Cataclismo!** Todos los carros que no hayan alcanzado la casilla 21 son engullidos de inmediato.
- Al avanzar dentro del mar, se roba una carta de Moisés y se compara su valor de Ira con los símbolos divinos:
  - **Símbolos Divinos > Ira de Moisés:** El jugador puede elegir entre:
    1. **Avanzar +1 casilla** hacia adelante.
    2. **Colapsar la última casilla activa del mar** (ej. casilla 30, luego 29...). Si algún carro rival queda en la casilla destruida, se ve obligado a retroceder o perece.
  - **Símbolos Divinos < Ira de Moisés:** El carro se ve obligado a avanzar hacia el fondo del mar.

### 8.4. Fase III: Escape y Fin de la Partida
- Al llegar al confín de las aguas o decidir la huida, los carros invierten su rumbo y deben regresar a la **casilla 20** (*Carros Supervivientes*).
- **Victoria:** La facción que logre retornar el mayor número de carros con vida a la casilla 20 es proclamada vencedora absoluta de **The Scourge of Egypt**.

---

## 9. INTERFAZ GRÁFICA Y PRESENTACIÓN 2D (`ui/`)

### 9.1. Especificaciones de Pantalla
- **Resolución:** $1280 \times 720$ (16:9 HD nítido).
- **Tasa de refresco:** 60 fotogramas por segundo sincronizados con `pygame.time.Clock`.

### 9.2. Distribución Espacial de la Interfaz
```
+---------------------------------------------------------------------------------+
| HUD SUPERIOR: Ira de Dios [|||||-----] | Moisés: Mandamiento V | Facción Activa |
+---------------------------+-----------------------------------------------------+
| TRACKS DE COSECHAS        | CARTA DE MOISÉS ACTIVA                              |
| Trigo  [==|====] 3/10     | [ Plaga de Sangre / Evento / Personaje ]            |
| Avena  [====|==] 5/10 !   +-----------------------------------------------------+
| Cebada [=|=====] 1/10     | ACCIONES DE TURNO Y LOSETAS                         |
+---------------------------+ - [Robar Moisés] [Donar Fe] [Invocar Dios]          |
| RESERVAS Y BOLSAS         | - Grid de 8 Losetas de Acción Interactivas          |
| Ganado: 20 | Viviendas: 25|   (Cosechar, Rezar, Ganadería, Regadíos, etc.)      |
| Bolsa Negra: 2 Sacrificios+-----------------------------------------------------+
| Bolsa Azul:  12/25 Fe     | RUEDA SOLAR INTERACTIVA (Gracia del Faraón)         |
+---------------------------+-----------------------------------------------------+
| LOGGER HISTÓRICO DE EVENTOS CON SCROLL (Últimas jugadas, tiradas y avisos)      |
+---------------------------------------------------------------------------------+
```

### 9.3. Sistema de Sonido Procedural (`audio.py`)
Utiliza la potencia de `numpy` y `pygame.sndarray` para sintetizar dinámicamente ondas de audio sin requerir dependencias de archivos `.wav` o `.mp3`:
- Sonido sutil de pulsación de botones (*Click* a 800 Hz).
- Ruido percusivo de dados rodando (*Dice burst*).
- Deslizamiento rápido de cartas (*Card swoop* a frecuencia modulada).
- Campana grave ceremonial para plagas y catástrofes (*Egyptian Gong* con armónicos en 110 Hz, 220 Hz y 330 Hz).
- Fanfarria de trompetas doradas para victorias (*Major Arpeggio* Do-Mi-Sol-Do).
- Alarma pulsante para alertas de hambruna y agotamiento de recursos.

---

## 10. PERSISTENCIA (GUARDAR Y CARGAR) (`save_load.py`)

El sistema permite serializar y deserializar el estado completo del juego en archivos **JSON** legibles:
- Estado del tablero (`BoardState`): contadores, bolsas, cosechas y marcadores.
- Estado de los jugadores (`Player`): acólitos, fe, estado individual de cada una de las 8 losetas y cartas activas.
- Mazos de juego: cartas restantes y orden en los mazos de Moisés, Divinidades y Mandamientos.
- Historial de eventos y turnos.

Guardado desde la interfaz pulsando el botón **"GUARDAR"** o cargando partidas anteriores desde el **Menú Principal**.

---

## 11. GUÍA DE INSTALACIÓN Y EJECUCIÓN

### 11.1. Requisitos Previos
- Python 3.10 o superior (verificado en Python 3.12).
- Bibliotecas requeridas:
  ```bash
  pip install pygame numpy
  ```

### 11.2. Ejecución del Juego
Para iniciar la interfaz gráfica completa con el Menú Principal y todos los modos:
```bash
python main.py
```

### 11.3. Ejecución en Modo Smoke-Test (Sin Ventana)
Para verificar la integridad del motor y simular un turno completo sin abrir ventana gráfica:
```bash
python main.py --smoke-test
```

### 11.4. Ejecución de la Suite de Pruebas Unitarias
Para correr los 22 tests unitarios del proyecto:
```bash
python -m unittest discover tests
```
Resultado verificado:
```
......................
----------------------------------------------------------------------
Ran 22 tests in 0.206s

OK
```

---

## 12. SISTEMA DE TUTORIALES INTERACTIVOS ("ACADEMIA DEL FARAÓN")

Para facilitar la curva de aprendizaje de nuevos jugadores, el juego incluye un módulo completo de tutoriales interactivos accesible directamente desde el Menú Principal mediante el botón **"TUTORIAL (CÓMO JUGAR)"**:

### 12.1. Las 6 Lecciones Estructuradas
1. **Lección 1: ¿De qué trata el juego?**
   - Introducción a las 5 facciones egipcias.
   - Visión general de los dos grandes actos: Éxodo A (Plagas y Gestión) y Éxodo B (Persecución en el Mar Rojo).
   - Condiciones de victoria final.
2. **Lección 2: Recursos Críticos y Bolsas Sagradas**
   - Explicación de la barra de Ira de Dios (0..50) y los umbrales de rayo (20 y 40).
   - Tracks de Cosechas (Trigo, Avena, Cebada), alerta en 5 y agotamiento en 10.
   - Bolsa Negra (recuento letal de sacrificios) y Bolsa Azul (meta comunitaria de Fe).
   - *Sandbox Interactivo:* Simulador de track de cosecha con botones para subir hambruna o aliviarla.
3. **Lección 3: El Flujo de Turno y las Plagas de Moisés**
   - Cómo robar la carta de Moisés y resolver los tipos de cartas (Plagas, Personajes, Eventos, Edificios).
   - Altar de Mandamientos: acumular 5 cubos blancos para avanzar a Moisés.
   - *Sandbox Interactivo:* Simulador de decisión ante la Plaga de Sangre (Aumentar Ira vs Sacrificar Acólitos).
4. **Lección 4: Las 8 Losetas de Acción y el Culto a los Dioses**
   - Explicación de las 8 losetas básicas (Cosechar, Rezar, Ganadería, Regadíos, Renacimiento, Reconstrucción, Dioses Favorables, Rendir Pleitesía).
   - Estados de losetas (Activa, Usada boca abajo, Destruida) y reactivación al final de ronda.
   - *Sandbox Interactivo:* Uso de loseta en vivo y reactivación de ronda.
5. **Lección 5: La Gracia del Faraón (Rueda Solar)**
   - Mecánica de los dos círculos concéntricos (Sol interior y Dioses exterior).
   - Alineación del Sol Radiante con Dioses activos para obtener poderes gratuitos y +3 Fe.
   - *Sandbox Interactivo:* Rueda solar funcional con tirada de dado D6 en tiempo real.
6. **Lección 6: El Fin de Éxodo A y la Carrera en el Mar Rojo (Éxodo B)**
   - Juicio de transición (viviendas, bolsa azul y eliminación de la bolsa negra).
   - Torbellino de fuego (casillas 1-19) y riesgo con cubos de reserva.
   - Entrada en el Mar Rojo (casillas 20-30), cataclismo de aguas cerrándose y huida a la casilla 20.
   - *Sandbox Interactivo:* Mini circuito con avance de carros mediante tiradas D6 + D12.

---

## 13. SISTEMA DE ICONOS Y ELEMENTOS VISUALES PROCEDURALES

El juego incorpora un módulo de iconos procedurales (`scourge_egypt/ui/icons.py`) que genera gráficos vectoriales nítidos mediante primitivas de Pygame sin dependencias externas:

| Icono | Elemento UI Representado | Significado / Efecto |
| :--- | :--- | :--- |
| **Llama Divina** | Barra superior HUD / Cartas de Plaga | Nivel de Ira de Dios (0-50) y potenciación |
| **Espiga de Cereal** | Tracks de Cosecha / Loseta COSECHAR | Trigo, Avena, Cebada y avance de hambruna |
| **Cabeza de Bovino** | Reserva de Ganado / Loseta GANADERÍA | Cubos de alimento y prevención de catástrofe |
| **Pirámide / Morada** | Reserva de Viviendas / RECONSTRUCCIÓN | Refugios disponibles y cartas de Edificio |
| **Palmas en Oración** | Losetas REZAR y RENDIR PLEITESÍA | Aplacamiento de la cólera divina y obtención de Fe |
| **Acólito / Figura** | Loseta RENACIMIENTO | Aumento de acólitos del jugador |
| **Dado de 6 Caras** | Loseta DIOSES FAVORABLES | Relanzamiento de tiradas de dados |
| **Olas de Agua** | Loseta REGADÍOS | Acciones extra de loseta en el turno |
| **Sol Radiante** | Cartas de Evento Sagrado / Rueda Solar | Bendiciones de Ra y fases del sol |
| **Pergamino** | Cartas de Personaje Bíblico | Líderes y prodigios del Éxodo |
| **Calavera Ritual** | Bolsa Negra (Tumbas y Sacrificios) | Pérdida de vidas y peligro de derrota |
| **Estrella Sagrada** | Bolsa Azul (Almacenamiento de Fe) | Requisito colectivo para superar el Éxodo A |
| **Carro de Guerra** | Fase Éxodo B (El Mar Rojo) | Posición y avance de los líderes en la carrera |
| **Ojo de Horus / Ankh** | Pantalla de Menú Principal / Decoración | Atmósfera y simbología temática egipcia |

---

## 14. CONTROLES Y JUGABILIDAD

| Acción | Control |
| :--- | :--- |
| **Interactuar / Seleccionar** | Clic izquierdo del ratón sobre botones, cartas y losetas |
| **Aprender a Jugar** | Botón dorado "TUTORIAL (CÓMO JUGAR)" en el Menú Principal |
| **Robar Carta de Moisés** | Botón dorado superior en el panel de acciones |
| **Usar Loseta de Acción** | Clic sobre cualquiera de las 8 losetas activas del jugador |
| **Girar Rueda Solar** | Clic en el botón "GRACIA DEL FARAÓN (D6)" bajo la rueda |
| **Donar Fe a la Bolsa Azul** | Clic en "DONAR 1 FE" |
| **Invocar Dios** | Clic en "INVOCAR DIOS" (Cuesta 2 tokens de Fe) |
| **Scroll en Logger / Reglas** | Rueda del ratón (*Mouse Wheel*) arriba / abajo |
| **Guardar Partida** | Clic en "GUARDAR" (Crea `partida_guardada.json`) |
| **Volver al Menú / Cancelar** | Clic en "MENÚ" o tecla `ESCAPE` |

---
*Desarrollado con arquitectura POO y MVC para The Scourge of Egypt.*
