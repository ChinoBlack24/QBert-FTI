"""
4.2 Máquina de movimiento (Mealy).

    Q  = {q0, ..., q27}         q_i = Q*bert está sobre el cubo i
    ΣE = {w, a, s, d}           w arriba-der, a arriba-izq, s abajo-izq, d abajo-der
    ΣS = {0, ..., 27, X}        el cubo pisado, o X si se cae

Si se cae, la salida es X y vuelve a q0. Se eligió Mealy porque a q0 se llega
por dos eventos distintos que solo la salida distingue:

    f(q1, w) = q0, g(q1, w) = 0     salta a la cima
    f(q1, a) = q0, g(q1, a) = X     se cae
"""

from .piramide import CANTIDAD_CUBOS

from .mef import Mealy, leer_tabla_mealy

# Símbolo de salida cuando Q*bert se cae de la pirámide.
# Es X (y no C) para no confundirlo con el color C del nivel 2.
CAIDA = "X"

SIGMA_S_MOVIMIENTO = frozenset({str(i) for i in range(CANTIDAD_CUBOS)} | {CAIDA})

# Tabla del informe. Cada celda es estado_nuevo/salida.
# tests/automatas/test_movimiento.py comprueba que coincida con la geometría de la pirámide.
TABLA_MOVIMIENTO = """
Q      w        a        s        d
→q0    q0/X     q0/X     q1/1     q2/2
q1     q0/0     q0/X     q3/3     q4/4
q2     q0/X     q0/0     q4/4     q5/5
q3     q1/1     q0/X     q6/6     q7/7
q4     q2/2     q1/1     q7/7     q8/8
q5     q0/X     q2/2     q8/8     q9/9
q6     q3/3     q0/X     q10/10   q11/11
q7     q4/4     q3/3     q11/11   q12/12
q8     q5/5     q4/4     q12/12   q13/13
q9     q0/X     q5/5     q13/13   q14/14
q10    q6/6     q0/X     q15/15   q16/16
q11    q7/7     q6/6     q16/16   q17/17
q12    q8/8     q7/7     q17/17   q18/18
q13    q9/9     q8/8     q18/18   q19/19
q14    q0/X     q9/9     q19/19   q20/20
q15    q10/10   q0/X     q21/21   q22/22
q16    q11/11   q10/10   q22/22   q23/23
q17    q12/12   q11/11   q23/23   q24/24
q18    q13/13   q12/12   q24/24   q25/25
q19    q14/14   q13/13   q25/25   q26/26
q20    q0/X     q14/14   q26/26   q27/27
q21    q15/15   q0/X     q0/X     q0/X
q22    q16/16   q15/15   q0/X     q0/X
q23    q17/17   q16/16   q0/X     q0/X
q24    q18/18   q17/17   q0/X     q0/X
q25    q19/19   q18/18   q0/X     q0/X
q26    q20/20   q19/19   q0/X     q0/X
q27    q0/X     q20/20   q0/X     q0/X
"""

# q_i <-> cubo i
ESTADO_DEL_CUBO = {i: f"q{i}" for i in range(CANTIDAD_CUBOS)}
CUBO_DEL_ESTADO = {q: i for i, q in ESTADO_DEL_CUBO.items()}


def crear_movimiento() -> Mealy:
    f, g, q0, finales = leer_tabla_mealy(TABLA_MOVIMIENTO)
    return Mealy("movimiento", f, g, SIGMA_S_MOVIMIENTO, q0, finales)
