"""
Mealy de Coily: huevo, eclosión y persecución simplificada.

Estados:
    fuera       Coily todavía no apareció o ya se cayó.
    h0..h27     el huevo está en un cubo; solo avanza con las entradas S/D.
    c0..c27     Coily está cazando desde su propio cubo; lee una tecla elegida por la partida.

Entradas:
    w/a/s/d     dirección elegida para Coily durante la persecución.
    S/D         tic del reloj hacia abajo-izquierda/derecha; el huevo baja como la bola roja.
    X           Q*bert se cayó: retirar Coily.
    J           Q*bert usó un disco: retirar Coily.

La aparición desde fuera empieza en la cima; al alcanzar la fila inferior el
huevo eclosiona en el mismo cubo. X y J son eventos de despeje, no movimiento.
El azar de los tics y de la espera de aparición lo decide quien llama a la MEF.
"""

from .bola import crear_bola
from .mef import Mealy
from .movimiento import CAIDA, crear_movimiento
from .piramide import CANTIDAD_CUBOS

SALTO_DISCO = "J"
TIC_IZQUIERDA = "S"
TIC_DERECHA = "D"
TICS_COILY = (TIC_IZQUIERDA, TIC_DERECHA)
ENTRADAS_COILY = ("w", "a", "s", "d", *TICS_COILY, CAIDA, SALTO_DISCO)
FUERA_COILY = "fuera"
NULA = "N"
FILA_BASE = 6

_HUEVO = tuple(f"h{i}" for i in range(CANTIDAD_CUBOS))
_CAZA = tuple(f"c{i}" for i in range(CANTIDAD_CUBOS))
_ESTADOS = (FUERA_COILY, *_HUEVO, *_CAZA)
SIGMA_S_COILY = frozenset(
    {NULA, CAIDA}
    | {f"H{i}" for i in range(CANTIDAD_CUBOS)}
    | {f"C{i}" for i in range(CANTIDAD_CUBOS)}
)


def _fase_salida(estado: str) -> str:
    if estado.startswith("h"):
        return "H" + estado[1:]
    if estado.startswith("c"):
        return "C" + estado[1:]
    return NULA


def _crear_transiciones() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Construye la tabla total reutilizando la geometría de bola y movimiento."""
    bola = crear_bola()
    movimiento = crear_movimiento()
    f: dict[str, dict[str, str]] = {}
    g: dict[str, dict[str, str]] = {}

    for estado in _ESTADOS:
        f[estado] = {}
        g[estado] = {}
        for entrada in ENTRADAS_COILY:
            nuevo = estado
            salida = _fase_salida(estado)

            if entrada in (CAIDA, SALTO_DISCO):
                nuevo, salida = FUERA_COILY, NULA
            elif estado == FUERA_COILY and entrada in TICS_COILY:
                nuevo, salida = "h0", "H0"
            elif estado.startswith("h") and entrada in TICS_COILY:
                posicion = int(estado[1:])
                if posicion >= FILA_BASE * (FILA_BASE + 1) // 2:
                    nuevo = f"c{posicion}"
                else:
                    direccion = "s" if entrada == TIC_IZQUIERDA else "d"
                    destino, _ = bola.paso(f"b{posicion}", direccion)
                    destino_posicion = int(destino[1:])
                    if destino_posicion >= FILA_BASE * (FILA_BASE + 1) // 2:
                        nuevo = f"c{destino_posicion}"
                    else:
                        nuevo = f"h{destino_posicion}"
                salida = _fase_salida(nuevo)
            elif estado.startswith("c") and entrada in ("w", "a", "s", "d"):
                posicion = int(estado[1:])
                destino, cubo = movimiento.paso(f"q{posicion}", entrada)
                if cubo == CAIDA:
                    nuevo, salida = FUERA_COILY, CAIDA
                else:
                    nuevo, salida = f"c{int(cubo)}", f"C{cubo}"

            f[estado][entrada] = nuevo
            g[estado][entrada] = salida

    return f, g


def crear_coily() -> Mealy:
    """Crea la Mealy determinista de Coily; las entradas aleatorias vienen del juego."""
    f, g = _crear_transiciones()
    return Mealy("coily", f, g, SIGMA_S_COILY, FUERA_COILY)
