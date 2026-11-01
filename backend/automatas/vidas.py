"""
4.4 Máquina de vidas (Moore).

    ΣE = {p, X}         p: pisó un cubo (no cambia nada)   X: se cayó (resta una)
    ΣS = {3, 2, 1, 0}   cantidad de vidas

GO (game over) es absorbente.
"""

from .mef import Moore, leer_tabla_moore
from .movimiento import CAIDA

# La columna X es el mismo símbolo CAIDA que escribe la Mealy de movimiento.
TABLA_VIDAS = """
Q/ΣS    p     X
→V3/3   V3    V2
V2/2    V2    V1
V1/1    V1    GO
GO/0    GO    GO
"""


def crear_vidas() -> Moore:
    f, g, q0, finales = leer_tabla_moore(TABLA_VIDAS)
    m = Moore("vidas", f, g, set(g.values()), q0, finales)
    assert m.sigma_e == {"p", CAIDA}
    return m
