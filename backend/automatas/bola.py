"""
Enemigo: la bola (Moore).

    Q  = {bF, b0, ..., b27}     b_i = la bola está sobre el cubo i,  bF = fuera de la pirámide
    ΣE = {s, d, X}              s abajo-izq, d abajo-der (solo baja)
                                X Q*bert perdió una vida: la bola se retira
    ΣS = {0, ..., 27, F}        g(b_i) = i,  g(bF) = F

Empieza fuera (bF) y entra por la cima. En cada tic del reloj baja hacia s o
hacia d; desde la fila de abajo sale (bF) y en el tic siguiente vuelve a la cima.
Cuando Q*bert pierde una vida (choque o caída) lee X y sale de la pirámide.
X es el mismo símbolo que lee la máquina de vidas en ese momento.

La bola es determinista: el azar está en quién escribe su palabra de entrada
(una moneda, fuera de este paquete), igual que el teclado escribe la de Q*bert.

Para s y d, las filas b0..b20 son las de la Mealy de movimiento restringida a
{s, d} (tests/automatas/test_bola.py lo comprueba).

Es Moore y no Mealy porque el choque se revisa también cuando la bola está
quieta (Q*bert salta entre dos tics): hace falta su posición en cualquier
momento, y en Moore la salida g(b) está definida en cada estado. En Mealy solo
hay salida al transicionar.
"""

from .mef import Moore, leer_tabla_moore

# Salida de la bola cuando está fuera de la pirámide.
FUERA = "F"

TABLA_BOLA = """
Q/ΣS     s      d      X
→bF/F    b0     b0     bF
b0/0     b1     b2     bF
b1/1     b3     b4     bF
b2/2     b4     b5     bF
b3/3     b6     b7     bF
b4/4     b7     b8     bF
b5/5     b8     b9     bF
b6/6     b10    b11    bF
b7/7     b11    b12    bF
b8/8     b12    b13    bF
b9/9     b13    b14    bF
b10/10   b15    b16    bF
b11/11   b16    b17    bF
b12/12   b17    b18    bF
b13/13   b18    b19    bF
b14/14   b19    b20    bF
b15/15   b21    b22    bF
b16/16   b22    b23    bF
b17/17   b23    b24    bF
b18/18   b24    b25    bF
b19/19   b25    b26    bF
b20/20   b26    b27    bF
b21/21   bF     bF     bF
b22/22   bF     bF     bF
b23/23   bF     bF     bF
b24/24   bF     bF     bF
b25/25   bF     bF     bF
b26/26   bF     bF     bF
b27/27   bF     bF     bF
"""


def crear_bola() -> Moore:
    f, g, q0, finales = leer_tabla_moore(TABLA_BOLA)
    return Moore("bola", f, g, set(g.values()), q0, finales)
