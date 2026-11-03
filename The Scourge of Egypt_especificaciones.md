# ESPECIFICACIÓN TÉCNICA DE DESARROLLO - THE SCOURGE OF EGYPT

## 1. RESUMEN EJECUTIVO Y OBJETIVO
El objetivo de este proyecto es implementar el juego de mesa **"The Scourge of Egypt"** en Python, con una arquitectura basada en Programación Orientada a Objetos (POO) y una interfaz gráfica funcional 2D utilizando **Pygame**. 

El sistema debe permitir jugar tanto de forma cooperativa/semi-competitiva local (turnos hot-seat) como validar todas las reglas complejas descritas en el reglamento original.

---

## 2. ARQUITECTURA GENERAL DEL SISTEMA

El proyecto debe seguir una arquitectura **Model-View-Controller (MVC)** o **Entity-Component-System (ECS) simplificada** para separar la lógica estricta de las reglas de la presentación visual.

```
+-------------------------------------------------------------+
|                      GameEngine (Main)                      |
|  - Controls Game Loop (Ticks, Events, Rendering)            |
|  - Manages GameState (MENU, EXODUS_A, EXODUS_B, GAME_OVER)  |
+------------------------------+------------------------------+
                               |
       +-----------------------+-----------------------+
       |                                               |
+------v----------------------+             +----------v------------------+
|      GameLogic / Rules      |             |     Pygame View / UI        |
| - BoardState (Tracks/Pools) |             | - BoardRenderer             |
| - PlayerManager             |             | - CardRenderer              |
| - Decks (Moses, Gods, Mand) |             | - ActionPanel & Dialogs     |
| - Combat / Dice Engine      |             | - HUD (Resources & Logs)    |
+-----------------------------+             +-----------------------------+
```

---

## 3. MODELO DE DATOS Y ESTADOS (MODEL)

### 3.1. Recursos Globales y Tablero (`BoardState`)
El estado global del tablero en **Éxodo A** contiene:
- `ira_de_dios`: Integer $[0..50]$.
  - Umbral 1 Rayo: Casilla 20 (potencia plagas $+1$).
  - Umbral 2 Rayos: Casilla 40 (potencia plagas $+2$).
- `cosechas`: Diccionario `{"trigo": int, "avena": int, "cebada": int}` (Rango $[0..10]$ por track).
  - Umbral 1ª Línea Discontinua: Posición $\ge 5$ (Alerta de hambruna).
  - Umbral 2ª Línea Discontinua: Posición 10 (Agotamiento total).
- `ganado`: Reserva de cubos blancos.
  - 1 Jugador: 15 cubos.
  - 2 Jugadores: 20 cubos.
  - 3 Jugadores: 30 cubos.
  - 4 Jugadores: 40 cubos.
- `viviendas`: Reserva de cubos grises.
  - 1 Jugador: 20 cubos.
  - 2 Jugadores: 25 cubos.
  - 3 Jugadores: 35 cubos.
  - 4 Jugadores: 40 cubos.
- `bolsa_tumbas_egipcias`: Lista/Bolsa de acólitos sacrificados y ganado (bolsa negra).
- `bolsa_almacenamiento_fe`: Lista/Bolsa de tokens de fe aportados por jugadores (bolsa azul).
- `track_mandamientos`: Progreso de cubos blancos en mandamientos $[0..5]$ y casilla de Moisés $[I..X]$.

### 3.2. Jugador y Facción (`Player`)
Cada facción contiene:
- `id`: Integer.
- `nombre_faccion`: String (`"Sacerdotes de Ra"`, `"Servidores de Seth"`, `"Discípulos de Osiris"`, `"Seguidores de Horus"`, `"Novicios de Isis"`).
- `color`: RGB Tuple.
- `reserva_acolitos`: Integer (Cubos personales).
- `tokens_fe`: Integer.
- `losetas_accion`: Lista de 8 objetos `ActionTile` (Estado: `activa`, `usada_boca_abajo`, `destruida`).
- `dioses_activos`: Lista de `GodCard` en mesa (Máximo 3 tras Mandamiento I).
- `objetos_activos`: Lista de `ItemCard`.
- `carros_exodo_b`: Lista de posiciones de carros en Éxodo B.

### 3.3. Estructura de Las Losetas de Acción Básicas
Cada jugador inicia con 8 losetas:
1. `COSECHAR` (Símbolo: 1 Ra) -> $+2$ a un track de cereal.
2. `REZAR` (Símbolo: 1 Ra / 1 Seth) -> $-2$ al marcador de Ira de Dios.
3. `GANADERÍA` (Símbolo: 1 Seth) -> $+2$ a la reserva de ganado.
4. `REGADÍOS` (Símbolo: 1 Ra) -> Usa 1 loseta adicional si paga su coste.
5. `RENACIMIENTO` (Símbolo: 1 Seth) -> $+2$ acólitos a tu reserva.
6. `RECONSTRUCCIÓN` (Símbolo: 2 Ra) -> $+2$ viviendas a la reserva.
7. `DIOSES FAVORABLES` (Símbolo: 2 Seth) -> Permite relanzar dado.
8. `RENDIR PLEITESÍA` (Símbolo: 1 Ra / 1 Seth) -> $+2$ tokens de fe personales.

---

## 4. LÓGICA DE REGLAS Y EVENTOS (GAME LOGIC)

### 4.1. Mazo de Moisés y Resolución de Plagas
El `Mazo de Moisés` debe construirse barajando: Cartas de Plaga, Personajes Bíblicos, Eventos Bíblicos y Edificios Míticos.

#### Algoritmo de Potenciación de Plagas
```python
def get_potenciacion(ira_de_dios):
    if ira_de_dios >= 40:
        return 2
    elif ira_de_dios >= 20:
        return 1
    return 0
```

#### Reglas de Procesamiento de Plagas:
1. **Plaga de Sangre:**
   - Opciones: Avanzar Ira de Dios $(2 + \text{potenciación})$ O Sacrificar $(2 + \text{potenciación})$ acólitos.
   - Acción de Fe opcional: Tirada Dado Facción ($1-3$: Pierde turno acciones; $4-6$: $+1$ o $+2$ tokens a Bolsa Azul).
   - Colocar carta en tablero. Si se colocan 8 cartas boca arriba -> Efecto Complementario: Todos sacrifican 1 acólito (salvo que tengan $\ge 3$ Fe personal) e Ira de Dios $+1$.
2. **Invasión de Ranas / Plaga de Langostas (Carta Doble):**
   - Lado Ranas: Voltear 3 losetas. Ira de Dios $+1$.
   - Lado Langostas: Voltear 3 losetas, $+1$ Fe personal, Ira de Dios $+2$.
   - Avanzar track de Cosecha hacia la derecha según número impreso $+$ potenciación.
   - Tirada Dado Moisés (12 caras):
     - $1-4$: Trigo $+1$ posición (o elimina 1 cubo de cosecha).
     - $5-8$: Avena $+1$ posición (o elimina 1 cubo de cosecha).
     - $9-12$: Cebada $+1$ posición (o elimina 1 cubo de cosecha).
3. **Plaga de Moscas / Mosquitos / Ganado:**
   - Moscas: Sacrificar 1 ganado. Opción: Sacrificar 2 acólitos entre jugadores para evitarlo.
   - Mosquitos: Tirada Dado Facción ($1-3$: Sacrificar 1 ganado; $4-5$: Sacrificar 2 ganado; $6$: Sacrificar 3 ganado). Opción de sustituir por acólitos.
   - Plaga del Ganado: Se acumulan cartas en zona de ganado. Carta #3 -> Sacrificar $1/4$ del ganado actual. Carta #8 -> Sacrificar $1/2$ del ganado actual. Si se extermina el ganado, robar esta carta obliga a destruir 1 loseta básica por facción (o sacrificar 1 acólito).
4. **Plaga de Úlceras:**
   - Cada jugador roba 1 carta del Mazo de Divinidades. Se cuentan los símbolos de Ra/Seth:
     - Mayoría Seth: Todos sacrifican 1 acólito.
     - Mayoría Ra: Se extrae 1 cubo de la Bolsa Negra al azar. Si coincide con una facción, el acólito revive.
     - Empate: Un jugador recibe la carta en su zona. Durante 2 turnos debe sacrificar 1 acólito al inicio de su turno.
5. **Plaga del Granizo:**
   - Tirada Dado Moisés (D12): $1-4 \rightarrow$ Destruir 2 viviendas; $5-8 \rightarrow$ Destruir 3 viviendas; $9-12 \rightarrow$ Destruir 4 viviendas (sumar potenciación).
   - Por cada 2 viviendas destruidas, los jugadores deben sacrificar 1 acólito en total (redondeado a la baja).
   - Si no quedan viviendas: Tirada Dado Facción ($1-3$: Destruir loseta o sacrificar 1 ganado; $4-6$: Destruir cosecha o sacrificar 1 acólito).
6. **Plaga de Tinieblas:**
   - Bloquea el uso de Divinidades (no se pueden comprar ni usar).
   - Limita a 3 losetas de acción por turno.
   - Dura 3 turnos completos. Se activa automáticamente una **Fase Extraordinaria de Gracia del Faraón**.
7. **Plaga Muerte de los Primogénitos:**
   - Cada jugador retira $(1 + \text{potenciación})$ acólitos y los coloca en la zona del "Ángel Exterminador".
   - Al colocar la carta **#10**, todos los acólitos en dicha zona se SACRIFICAN a la Bolsa Negra (salvo quien juegue la carta *Portal Seguro*).

### 4.2. Track de Moisés y Mazo de los Diez Mandamientos
- Cuando una carta de plaga muestre el símbolo de tablas de la ley, se añade 1 cubo blanco al Mandamiento actual.
- Al acumular 5 cubos blancos:
  1. Se extrae la siguiente carta del `Mazo de Mandamientos` ($I \rightarrow X$).
  2. Se aplica de inmediato el efecto global del mandamiento.
  3. El meeple de Moisés avanza 1 casilla. Se limpian los 5 cubos.
- **Fin del Éxodo A:** Cuando el meeple de Moisés alcanza la casilla **X**.

### 4.3. Fase Gracia del Faraón (Rueda Solar)
- El jugador activo lanza su dado de facción (D6).
- Mueve las 2 ruedas del Disco Solar (Rueda interna con símbolos de Sol, Rueda externa con Nombres de Dioses) repartiendo el número de pasos obtenido.
- Si logra hacer coincidir el **SOL RADIANTE** con el **Nombre de un Dios** activo en su área:
  - Usa el poder de ese Dios **GRATIS** (sin pagar coste en Fe/símbolos).
  - Gana $+3$ tokens de Fe personales.

---

## 5. REVISION DE CONDICIONES DE VICTORIA (TRANSICIÓN A ÉXODO B)

Al finalizar el Éxodo A (casilla X de Moisés), el motor ejecuta las siguientes validaciones en orden estricto:

```python
def verificar_condiciones_exodo_a(board_state, players):
    # Condición 1: Viviendas
    if board_state.viviendas <= 0:
        return False, "DERROTA: Todas las viviendas fueron destruidas."
    
    # Condición 2: Almacenamiento de Fe (Bolsa Azul)
    requisito_fe = {1: 15, 2: 25, 3: 35, 4: 45}
    total_fe_bolsa = len(board_state.bolsa_almacenamiento_fe)
    if total_fe_bolsa < requisito_fe[len(players)]:
        return False, f"DERROTA: Fe insuficiente en la Bolsa Azul ({total_fe_bolsa}/{requisito_fe[len(players)]})."
    
    # Condición 3: Recuento de Sacrificios (Bolsa Negra)
    # Contar acólitos por color en bolsa_tumbas_egipcias
    conteo_sacrificios = {p.id: 0 for p in players}
    for item in board_state.bolsa_tumbas_egipcias:
        if isinstance(item, Acolito):
            conteo_sacrificios[item.player_id] += 1
            
    max_sacrificios = max(conteo_sacrificios.values())
    
    # Filtrar eliminados (los que tienen max_sacrificios, salvo si tienen Portal Seguro)
    supervivientes = []
    for p in players:
        if conteo_sacrificios[p.id] == max_sacrificios and not p.tiene_portal_seguro:
            p.eliminado = True
        else:
            supervivientes.append(p)
            
    if len(supervivientes) == 0:
        return False, "DERROTA: Todos los jugadores fueron eliminados por exceso de sacrificios."
        
    return True, supervivientes
```

---

## 6. LÓGICA DE FASE ÉXODO B (LA PERSECUCIÓN)

El tablero cambia a un circuito unilineal de **30 casillas**.
- Cada jugador conserva sus acólitos restantes en reserva convertidos en **Carros** (máximo 3 carros en casilla de Salida).

### 6.1. Subfases del Éxodo B
1. **Fase I: Torbellino de Fuego (Casillas 1 a 19):**
   - El jugador tira Dado Facción (D6), roba 1 carta de Divinidad (obtiene símbolos Ra/Seth) y lanza Dado de Moisés (D12).
   - $\text{Avance} = (\text{Resultado D6} + \text{Símbolos Divinidad}) - \text{Resultado D12}$.
   - Si $\text{Avance} > 0$: Avanza ese número de casillas (máximo hasta la casilla 20).
   - Si $\text{Avance} \le 0$:
     - Opción de arriesgar: Gastar 1 cubo de reserva para convertir en $0$ y robar 1 carta del Mazo de Moisés. Si la carta tiene ícono de avance de Ira de Dios ($+1/+2$), avanza esas casillas. Si no lo tiene, **el carro se destruye**.
2. **Fase II: Internarse en el Mar Rojo (Casillas 20 a 30):**
   - Se activa cuando el carro llega a la casilla 20.
   - Los resultados positivos avanzan **únicamente 1 casilla**.
   - Resultados negativos obligan a intentar el arriesgar sin gastar cubos extras.
   - Permite meter un $2º$ carro en juego desde la Salida.
3. **Subfase II: Las aguas empiezan a cerrarse:**
   - Se activa cuando un **segundo jugador** (o un $2º$ carro del mismo jugador) llega a la casilla 20.
   - Todos los carros que no hayan alcanzado la casilla 21 son eliminados automáticamente.
   - Al avanzar, se roba 1 carta de Moisés y 1 de Divinidad:
     - Símbolos Ra/Seth > Avanza Ira de Dios: El jugador elige entre AVANZAR 1 casilla o DESTRUIR la última casilla activa del tablero (ej. la 30, luego la 29). Si está a $\le 1$ casilla del agua, debe retroceder.
     - Símbolos Ra/Seth < Avanza Ira de Dios: El carro DEBE avanzar obligatoriamente hacia adelante.
4. **Fase III: Escapar a la Casilla 20 (Fin del Juego):**
   - Los carros deben dar la vuelta y regresar a la **casilla 20** ("Carros Supervivientes").
   - Gana el jugador que logre meter más carros de vuelta en la casilla 20.

---

## 7. DISEÑO DE LA INTERFAZ GRÁFICA Y GUI (PYGAME)

La representación 2D funcional debe estructurarse mediante regiones en pantalla (resolución recomendada: $1280 \times 720$ o $1920 \times 1080$).

```
+---------------------------------------------------------------------------------+
| HEADER HUD: Ira de Dios [||||||||--] | Moisés: Mandamiento V | Fase: ÉXODO A    |
+------------------------------------+--------------------------------------------+
|                                    | AREA DE CARTAS ACTIVAS                     |
| TABLERO PRINCIPAL                  | - Carta Moisés Actual                      |
| - Track Cosechas (Trigo/Avena/Ceb) | - Divinidades en Dioses Olvidados          |
| - Contador Ganado (Cubos Blancos)  | - Edificios Míticos en Construcción        |
| - Contador Viviendas (Cubos Gris)  |                                            |
| - Rueda Solar (Visual Interactiva) +--------------------------------------------+
|                                    | PANEL DEL JUGADOR ACTIVO                   |
|                                    | - Facción: Sacerdotes de Ra                |
|                                    | - Mis Acólitos: 4 | Fe Personal: 6         |
|                                    | - Grid de 8 Losetas de Acción (Clickable)  |
|                                    | - Mis Dioses Activos                       |
+------------------------------------+--------------------------------------------+
| LOGS DE EVENTOS Y BARRAS DE TEXTO (Scrollable)                                  |
+---------------------------------------------------------------------------------+
```

### Componentes UI Requeridos:
1. **`BoardRenderer`:** Dibuja los tracks numéricos con cubos/fichas de colores.
2. **`SolarWheelUI`:** Representación gráfica de dos círculos concéntricos que giran con animación suave al ejecutar la Fase Gracia del Faraón.
3. **`TileGridUI`:** Muestra las 8 losetas del jugador activo. Cambia de color/estado cuando la loseta se usa (se pone gris/boca abajo) o se destruye.
4. **`DialogPrompt`:** Ventana emergente modal para tomar decisiones de las plagas (ej: "¿Sacrificar 2 acólitos o avanzar Ira de Dios +2?").
5. **`GameLogger`:** Panel inferior de texto que imprime cada evento ocurrido durante el turno para fácil depuración.

---

## 8. PLAN DE IMPLEMENTACIÓN PASO A PASO

El asistente de código o desarrollador debe ejecutar el desarrollo en las siguientes fases:

1. **Fase 1: Módulos Core de Datos (`models.py`)**
   - Definir clases `Player`, `Card`, `GodCard`, `PlagueCard`, `ActionTile`, `BoardState`.
2. **Fase 2: Motor de Reglas sin UI (`game_engine.py`)**
   - Implementar la lógica del turno, robos de mazo, cálculo de Ira de Dios, resolución de las 10 plagas y testear vía consolas/unit tests.
3. **Fase 3: Capa Gráfica Base (`gui_base.py`)**
   - Crear la ventana de Pygame, dibujar rectángulos contenedores, HUD de recursos y el Game Logger.
4. **Fase 4: Integración de Interacciones de Éxodo A (`exodus_a_gui.py`)**
   - Conectar clics de ratón en losetas de acción, modales de decisión de plagas y animación básica de la Rueda Solar.
5. **Fase 5: Reglas y Módulo de Éxodo B (`exodus_b_engine.py`)**
   - Crear la vista del circuito de 30 casillas, tiradas de dados animadas y la lógica del cierre de aguas.
6. **Fase 6: Polishing y Balanceo**
   - Sonidos, resaltados de cartas al pasar el cursor (hover), y soporte para persistencia (Guardar/Cargar partida en JSON).
```
eof