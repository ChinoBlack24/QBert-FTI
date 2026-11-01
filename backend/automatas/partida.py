"""
4.5 Integración de las máquinas.

Cada tecla (w, a, s, d) es una entrada de la Mealy de movimiento. Su salida s
se reparte así:

    s = i (0..27)  ->  el cubo i lee p          y la máquina de vidas lee h(i) = p
    s = X          ->  ningún cubo lee nada     y la máquina de vidas lee h(X) = X

El nivel está completo cuando los 28 cubos están en su estado objetivo, es
decir cuando la tupla de estados pertenece a F_0 x F_1 x ... x F_27: la
condición de aceptación del AFD intersección de la sección 3.3. No se
construye ese producto (tendría hasta 3^28 estados en el nivel 2); alcanza con
revisar cada componente. tests/automatas/test_partida.py comprueba que las dos formas
dan lo mismo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from automata.fa.dfa import DFA

from .cubo import NIVELES, crear_cubo
from .mef import Transicion
from .movimiento import CAIDA, CUBO_DEL_ESTADO, SIGMA_S_MOVIMIENTO, crear_movimiento
from .piramide import CANTIDAD_CUBOS
from .vidas import crear_vidas


# ===========================================================================
# Conexión entre máquinas
# ===========================================================================
def entrada_vidas(s: str) -> str:
    """h: ΣS(movimiento) -> ΣE(vidas).  h(i) = p para todo cubo i,  h(X) = X."""
    return CAIDA if s == CAIDA else "p"


def crear_cubo_sobre_salida(nivel: int, i: int) -> DFA:
    """
    AF_i: el cubo i visto como AFD que lee directamente la salida de la Mealy
    (alfabeto ΣS = {0..27, X}):

        f_i(q, x) = f(q, p)   si x = i
        f_i(q, x) = q         si x ≠ i

    Así todos los cubos leen el mismo alfabeto y se pueden intersecar (3.3).
    """
    cubo = crear_cubo(nivel)
    f = {q: {x: (cubo.f.transitions[q]["p"] if x == str(i) else q) for x in SIGMA_S_MOVIMIENTO}
         for q in cubo.Q}
    return DFA(states=set(f), input_symbols=set(SIGMA_S_MOVIMIENTO), transitions=f,
               initial_state=cubo.q0, final_states=set(cubo.finales))


# ===========================================================================
# Un salto
# ===========================================================================
class PasoCubo(NamedTuple):
    """El cubo pisado y su transición: q --p--> q_nuevo, con salida color."""
    cubo: int
    q: str
    q_nuevo: str
    color: str


@dataclass
class Paso:
    """Lo que hizo cada máquina en un salto."""
    mov: Transicion           # Mealy de movimiento
    cubo: PasoCubo | None     # None si fue una caída
    vidas: Transicion         # Moore de vidas

    def lineas(self) -> list[str]:
        m, v = self.mov, self.vidas
        out = [f"Mealy:  f({m.q}, {m.e}) = {m.q_nuevo}    g({m.q}, {m.e}) = {m.s}"]
        if self.cubo:
            c = self.cubo
            out.append(f"Cubo {c.cubo}: {c.q} --p--> {c.q_nuevo}/{c.color}")
        out.append(f"Vidas:  {v.q} --{v.e}--> {v.q_nuevo}/{v.s}")
        return out

    def __str__(self):
        return "\n".join(self.lineas())


class Partida:
    def __init__(self, nivel: int = 1):
        self.movimiento = crear_movimiento()
        self.vidas = crear_vidas()
        self.estado_vidas = self.vidas.q0
        self.empezar_nivel(nivel)

    def empezar_nivel(self, nivel: int):
        self.cubo = crear_cubo(nivel)  # la misma definición sirve para los 28 cubos
        self.nivel = nivel
        self.estado_mov = self.movimiento.q0
        self.estados_cubos = [self.cubo.q0] * CANTIDAD_CUBOS
        self.salida_mealy = []  # palabra de salida de la Mealy en este nivel
        self.ultimo_paso: Paso | None = None

    # --- salidas que se muestran -------------------------------------------
    def color(self, i: int) -> str:
        return self.cubo.g[self.estados_cubos[i]]

    def cantidad_vidas(self) -> int:
        return int(self.vidas.g[self.estado_vidas])

    def posicion(self) -> int:
        return CUBO_DEL_ESTADO[self.estado_mov]

    def cubos_en_objetivo(self) -> int:
        return sum(q in self.cubo.finales for q in self.estados_cubos)

    # --- condiciones de fin ------------------------------------------------
    def nivel_completo(self) -> bool:
        return self.cubos_en_objetivo() == CANTIDAD_CUBOS

    def ultimo_nivel(self) -> bool:
        return self.nivel == max(NIVELES)

    def game_over(self) -> bool:
        return self.cantidad_vidas() == 0

    def terminada(self) -> bool:
        return self.game_over() or self.nivel_completo()

    # --- un salto ----------------------------------------------------------
    def saltar(self, tecla: str) -> Paso | None:
        """Procesa una tecla. Devuelve el Paso, o None si el nivel/partida ya terminó."""
        if tecla not in self.movimiento.sigma_e:
            raise ValueError(f"'{tecla}' no pertenece a ΣE = {sorted(self.movimiento.sigma_e)}")
        if self.terminada():
            return None

        # 1) Mealy de movimiento
        [mov] = self.movimiento.traza(tecla, self.estado_mov)
        self.estado_mov = mov.q_nuevo
        self.salida_mealy.append(mov.s)

        # 2) cubos: solo el cubo s lee p
        paso_cubo = None
        if mov.s != CAIDA:
            i = int(mov.s)
            [t] = self.cubo.traza("p", self.estados_cubos[i])
            self.estados_cubos[i] = t.q_nuevo
            paso_cubo = PasoCubo(i, t.q, t.q_nuevo, t.s)

        # 3) vidas: lee h(s)
        [vid] = self.vidas.traza(entrada_vidas(mov.s), self.estado_vidas)
        self.estado_vidas = vid.q_nuevo

        self.ultimo_paso = Paso(mov, paso_cubo, vid)
        return self.ultimo_paso

    def pasar_de_nivel(self):
        """Empieza el nivel siguiente, conservando las vidas."""
        if not self.nivel_completo():
            raise ValueError("todavía no completaste el nivel")
        if self.ultimo_nivel():
            raise ValueError("ya estás en el último nivel")
        self.empezar_nivel(self.nivel + 1)

    def jugar(self, teclas: str) -> list[Paso]:
        """Procesa varias teclas seguidas; se detiene si la partida termina."""
        pasos = []
        for t in teclas:
            p = self.saltar(t)
            if p is None:
                break
            pasos.append(p)
        return pasos
