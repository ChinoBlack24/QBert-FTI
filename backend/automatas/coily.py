"""
Máquina de movimiento de Coily (Mealy).

    MEF_coily = <Q, E, S, f, g>
    Q = {fuera, h0, ..., h27, c0, ..., c27}
        fuera = Coily todavía no apareció o ya se cayó
        h_i   = el huevo está en el cubo i
        c_i   = Coily persigue desde el cubo i
    E = {w, a, s, d, S, D, X, J}
        w/a/s/d = movimientos de caza: arriba-der, arriba-izq,
                  abajo-izq y abajo-der
        S/D     = tic del huevo hacia abajo-izq/abajo-der
        X       = Q*bert se cayó; retirar a Coily
        J       = Q*bert tomó un disco; retirar a Coily
    S = {N, X, H0, ..., H27, C0, ..., C27}
        N = Coily está fuera; X = Coily cae durante la persecución
        H_i/C_i = huevo/Coily está en el cubo i

    f: Q x E -> Q        transición de estado
    g: Q x E -> S        salida en cada transición

Tabla de transiciones completa (cada celda es estado_nuevo/salida):

    Q      | w       | a       | s       | d       | S         | D         | X       | J
    -------|---------|---------|---------|---------|-----------|-----------|---------|--------
    fuera  | fuera/N | fuera/N | fuera/N | fuera/N | h0/H0     | h0/H0     | fuera/N | fuera/N
    h0     | h0/H0   | h0/H0   | h0/H0   | h0/H0   | h1/H1     | h2/H2     | fuera/N | fuera/N
    h1     | h1/H1   | h1/H1   | h1/H1   | h1/H1   | h3/H3     | h4/H4     | fuera/N | fuera/N
    h2     | h2/H2   | h2/H2   | h2/H2   | h2/H2   | h4/H4     | h5/H5     | fuera/N | fuera/N
    h3     | h3/H3   | h3/H3   | h3/H3   | h3/H3   | h6/H6     | h7/H7     | fuera/N | fuera/N
    h4     | h4/H4   | h4/H4   | h4/H4   | h4/H4   | h7/H7     | h8/H8     | fuera/N | fuera/N
    h5     | h5/H5   | h5/H5   | h5/H5   | h5/H5   | h8/H8     | h9/H9     | fuera/N | fuera/N
    h6     | h6/H6   | h6/H6   | h6/H6   | h6/H6   | h10/H10   | h11/H11   | fuera/N | fuera/N
    h7     | h7/H7   | h7/H7   | h7/H7   | h7/H7   | h11/H11   | h12/H12   | fuera/N | fuera/N
    h8     | h8/H8   | h8/H8   | h8/H8   | h8/H8   | h12/H12   | h13/H13   | fuera/N | fuera/N
    h9     | h9/H9   | h9/H9   | h9/H9   | h9/H9   | h13/H13   | h14/H14   | fuera/N | fuera/N
    h10    | h10/H10 | h10/H10 | h10/H10 | h10/H10 | h15/H15   | h16/H16   | fuera/N | fuera/N
    h11    | h11/H11 | h11/H11 | h11/H11 | h11/H11 | h16/H16   | h17/H17   | fuera/N | fuera/N
    h12    | h12/H12 | h12/H12 | h12/H12 | h12/H12 | h17/H17   | h18/H18   | fuera/N | fuera/N
    h13    | h13/H13 | h13/H13 | h13/H13 | h13/H13 | h18/H18   | h19/H19   | fuera/N | fuera/N
    h14    | h14/H14 | h14/H14 | h14/H14 | h14/H14 | h19/H19   | h20/H20   | fuera/N | fuera/N
    h15    | h15/H15 | h15/H15 | h15/H15 | h15/H15 | c21/C21   | c22/C22   | fuera/N | fuera/N
    h16    | h16/H16 | h16/H16 | h16/H16 | h16/H16 | c22/C22   | c23/C23   | fuera/N | fuera/N
    h17    | h17/H17 | h17/H17 | h17/H17 | h17/H17 | c23/C23   | c24/C24   | fuera/N | fuera/N
    h18    | h18/H18 | h18/H18 | h18/H18 | h18/H18 | c24/C24   | c25/C25   | fuera/N | fuera/N
    h19    | h19/H19 | h19/H19 | h19/H19 | h19/H19 | c25/C25   | c26/C26   | fuera/N | fuera/N
    h20    | h20/H20 | h20/H20 | h20/H20 | h20/H20 | c26/C26   | c27/C27   | fuera/N | fuera/N
    h21    | h21/H21 | h21/H21 | h21/H21 | h21/H21 | c21/C21   | c21/C21   | fuera/N | fuera/N
    h22    | h22/H22 | h22/H22 | h22/H22 | h22/H22 | c22/C22   | c22/C22   | fuera/N | fuera/N
    h23    | h23/H23 | h23/H23 | h23/H23 | h23/H23 | c23/C23   | c23/C23   | fuera/N | fuera/N
    h24    | h24/H24 | h24/H24 | h24/H24 | h24/H24 | c24/C24   | c24/C24   | fuera/N | fuera/N
    h25    | h25/H25 | h25/H25 | h25/H25 | h25/H25 | c25/C25   | c25/C25   | fuera/N | fuera/N
    h26    | h26/H26 | h26/H26 | h26/H26 | h26/H26 | c26/C26   | c26/C26   | fuera/N | fuera/N
    h27    | h27/H27 | h27/H27 | h27/H27 | h27/H27 | c27/C27   | c27/C27   | fuera/N | fuera/N
    c0     | fuera/X | fuera/X | c1/C1   | c2/C2   | c0/C0     | c0/C0     | fuera/N | fuera/N
    c1     | c0/C0   | fuera/X | c3/C3   | c4/C4   | c1/C1     | c1/C1     | fuera/N | fuera/N
    c2     | fuera/X | c0/C0   | c4/C4   | c5/C5   | c2/C2     | c2/C2     | fuera/N | fuera/N
    c3     | c1/C1   | fuera/X | c6/C6   | c7/C7   | c3/C3     | c3/C3     | fuera/N | fuera/N
    c4     | c2/C2   | c1/C1   | c7/C7   | c8/C8   | c4/C4     | c4/C4     | fuera/N | fuera/N
    c5     | fuera/X | c2/C2   | c8/C8   | c9/C9   | c5/C5     | c5/C5     | fuera/N | fuera/N
    c6     | c3/C3   | fuera/X | c10/C10 | c11/C11 | c6/C6     | c6/C6     | fuera/N | fuera/N
    c7     | c4/C4   | c3/C3   | c11/C11 | c12/C12 | c7/C7     | c7/C7     | fuera/N | fuera/N
    c8     | c5/C5   | c4/C4   | c12/C12 | c13/C13 | c8/C8     | c8/C8     | fuera/N | fuera/N
    c9     | fuera/X | c5/C5   | c13/C13 | c14/C14 | c9/C9     | c9/C9     | fuera/N | fuera/N
    c10    | c6/C6   | fuera/X | c15/C15 | c16/C16 | c10/C10   | c10/C10   | fuera/N | fuera/N
    c11    | c7/C7   | c6/C6   | c16/C16 | c17/C17 | c11/C11   | c11/C11   | fuera/N | fuera/N
    c12    | c8/C8   | c7/C7   | c17/C17 | c18/C18 | c12/C12   | c12/C12   | fuera/N | fuera/N
    c13    | c9/C9   | c8/C8   | c18/C18 | c19/C19 | c13/C13   | c13/C13   | fuera/N | fuera/N
    c14    | fuera/X | c9/C9   | c19/C19 | c20/C20 | c14/C14   | c14/C14   | fuera/N | fuera/N
    c15    | c10/C10 | fuera/X | c21/C21 | c22/C22 | c15/C15   | c15/C15   | fuera/N | fuera/N
    c16    | c11/C11 | c10/C10 | c22/C22 | c23/C23 | c16/C16   | c16/C16   | fuera/N | fuera/N
    c17    | c12/C12 | c11/C11 | c23/C23 | c24/C24 | c17/C17   | c17/C17   | fuera/N | fuera/N
    c18    | c13/C13 | c12/C12 | c24/C24 | c25/C25 | c18/C18   | c18/C18   | fuera/N | fuera/N
    c19    | c14/C14 | c13/C13 | c25/C25 | c26/C26 | c19/C19   | c19/C19   | fuera/N | fuera/N
    c20    | fuera/X | c14/C14 | c26/C26 | c27/C27 | c20/C20   | c20/C20   | fuera/N | fuera/N
    c21    | c15/C15 | fuera/X | fuera/X | fuera/X | c21/C21   | c21/C21   | fuera/N | fuera/N
    c22    | c16/C16 | c15/C15 | fuera/X | fuera/X | c22/C22   | c22/C22   | fuera/N | fuera/N
    c23    | c17/C17 | c16/C16 | fuera/X | fuera/X | c23/C23   | c23/C23   | fuera/N | fuera/N
    c24    | c18/C18 | c17/C17 | fuera/X | fuera/X | c24/C24   | c24/C24   | fuera/N | fuera/N
    c25    | c19/C19 | c18/C18 | fuera/X | fuera/X | c25/C25   | c25/C25   | fuera/N | fuera/N
    c26    | c20/C20 | c19/C19 | fuera/X | fuera/X | c26/C26   | c26/C26   | fuera/N | fuera/N
    c27    | fuera/X | c20/C20 | fuera/X | fuera/X | c27/C27   | c27/C27   | fuera/N | fuera/N

Para h_i, "avanza por bola" reutiliza la transición s o d de la Moore de la
bola roja; al entrar a la fila inferior, el huevo eclosiona en ese mismo cubo
(h_i -> c_i) y la salida pasa de H_i a C_i. Para los estados c_i, w/a/s/d
reutiliza la Mealy de movimiento: si la dirección lleva a un cubo j, transita
a c_j/C_j; si se cae fuera de la pirámide, transita a fuera/X.

La tabla completa se construye en _crear_transiciones para todas las posiciones
de la pirámide. El azar de los tics y de la espera de aparición lo decide quien
llama a la MEF; X y J son eventos de despeje, no movimientos.
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
