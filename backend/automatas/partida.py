"""
4.5 Integración de las máquinas.

El sistema recibe dos tipos de evento, y cada uno va solo a la máquina que le
corresponde, más los tics independientes del huevo de Coily:

    tecla e ∈ {w, a, s, d}   (el jugador)  ->  la Mealy de movimiento lee e
    tic con moneda c ∈ {s, d} (el reloj)   ->  la Moore de la bola lee c
    tic de Coily S/D                         ->  la Mealy de Coily lee S o D
    tic de caza                              ->  Coily elige una dirección hacia Q*bert

Cada máquina lee su propia palabra de entrada; los eventos llegan intercalados.
Cuando Coily ya eclosionó, elige su propia tecla según las filas y columnas
de ambos personajes.

Con una tecla, la salida s de la Mealy se reparte así:

    s = i (0..27)  ->  el cubo i lee p
    s = X          ->  ningún cubo lee nada
    la máquina de vidas lee X si s = X, si Q*bert salta a la bola o si
    Q*bert y Coily terminan el evento en el mismo cubo; en otro caso lee p.

Con un tic de la bola, su salida j se compara con el cubo donde está Q*bert.
Con un tic de Coily, se mueve el huevo o aparece desde fuera; si eclosiona
directamente en el cubo de Q*bert, la máquina de vidas lee X.

Cada vez que la máquina de vidas lee X (caída o choque), los enemigos activos
también leen X y salen de la pirámide. Así no pueden quitar dos vidas seguidas.

La persecución usa una regla voraz fila/columna, no una búsqueda de ruta óptima.

El nivel está completo cuando los 28 cubos están en su estado objetivo, es
decir cuando la tupla de estados pertenece a F_0 x F_1 x ... x F_27: la
condición de aceptación del AFD intersección de la sección 3.3. No se
construye ese producto (tendría hasta 3^28 estados en el nivel 2); alcanza con
revisar cada componente. tests/automatas/test_partida.py comprueba que las dos
formas dan lo mismo. La bola no pinta cubos, así que no cambia esta condición.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from automata.fa.dfa import DFA

from .bola import FUERA, crear_bola
from .coily import SALTO_DISCO, crear_coily
from .cubo import NIVELES, crear_cubo
from .mef import Transicion
from .movimiento import CAIDA, CUBO_DEL_ESTADO, SIGMA_S_MOVIMIENTO, crear_movimiento
from .piramide import CANTIDAD_CUBOS, fila_columna
from .vidas import crear_vidas

# Lo que puede traer un tic del reloj. X no: la bola lo lee solo por la integración.
DIRECCIONES_BOLA = ("s", "d")
PLATOS = {10: "a", 14: "w"}


# ===========================================================================
# Conexión entre máquinas
# ===========================================================================
def entrada_vidas(s: str, j: str) -> str:
    """
    h': ΣS(movimiento) x ΣS(bola) -> ΣE(vidas).
    s es la salida de la Mealy, j la salida de la bola.
    """
    return CAIDA if s == CAIDA or s == j else "p"


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
# Lo que pasa en cada evento
# ===========================================================================
class PasoCubo(NamedTuple):
    """El cubo pisado y su transición: q --p--> q_nuevo, con salida color."""
    cubo: int
    q: str
    q_nuevo: str
    color: str


@dataclass
class Paso:
    """Lo que hizo cada máquina en un salto de Q*bert (evento tecla)."""
    mov: Transicion           # Mealy de movimiento
    cubo: PasoCubo | None     # None si no aterrizó en un cubo
    choque: bool              # saltó al cubo donde está la bola
    choque_coily: bool
    uso_plato: bool
    vidas: Transicion         # Moore de vidas, leyendo p o X por caída/choque
    retiro_bola: Transicion | None  # la bola leyendo X, si se perdió una vida
    retiro_coily: Transicion | None

    def lineas(self) -> list[str]:
        m, v = self.mov, self.vidas
        out = [f"Mealy:  f({m.q}, {m.e}) = {m.q_nuevo}    g({m.q}, {m.e}) = {m.s}"]
        if self.cubo:
            c = self.cubo
            out.append(f"Cubo {c.cubo}: {c.q} --p--> {c.q_nuevo}/{c.color}")
        if self.choque:
            out.append(f"Choque: Q*bert saltó al cubo de la bola ({m.s})")
        if self.choque_coily:
            out.append("Choque: Q*bert alcanzó a Coily")
        out.append(f"Vidas:  {v.q} --{v.e}--> {v.q_nuevo}/{v.s}")
        if self.retiro_bola:
            b = self.retiro_bola
            out.append(f"Bola:   {b.q} --{b.e}--> {b.q_nuevo}/{b.s}")
        if self.retiro_coily:
            c = self.retiro_coily
            out.append(f"Coily:  {c.q} --{c.e}--> {c.q_nuevo}/{c.s}")
        return out

    def __str__(self):
        return "\n".join(self.lineas())


@dataclass
class PasoTic:
    """Lo que hizo cada máquina en un tic del reloj."""
    bola: Transicion            # Moore de la bola, leyendo s o d
    choque: bool                # la bola cayó en el cubo de Q*bert
    vidas: Transicion | None    # Moore de vidas; solo lee (X) si hubo choque
    retiro_bola: Transicion | None  # la bola leyendo X, si hubo choque
    retiro_coily: Transicion | None

    def lineas(self) -> list[str]:
        b = self.bola
        out = [f"Bola:   {b.q} --{b.e}--> {b.q_nuevo}/{b.s}"]
        if self.choque:
            out.append(f"Choque: la bola cayó en el cubo de Q*bert ({b.s})")
        if self.vidas:
            v = self.vidas
            out.append(f"Vidas:  {v.q} --{v.e}--> {v.q_nuevo}/{v.s}")
        if self.retiro_bola:
            r = self.retiro_bola
            out.append(f"Bola:   {r.q} --{r.e}--> {r.q_nuevo}/{r.s}")
        if self.retiro_coily:
            c = self.retiro_coily
            out.append(f"Coily:  {c.q} --{c.e}--> {c.q_nuevo}/{c.s}")
        return out

    def __str__(self):
        return "\n".join(self.lineas())


@dataclass
class PasoTicCoily:
    """Un tic independiente de Coily: entrada del huevo o aparición desde fuera."""
    coily: Transicion
    choque: bool
    bono_caida: bool
    vidas: Transicion | None
    retiro_bola: Transicion | None
    retiro_coily: Transicion | None


class Partida:
    def __init__(self, nivel: int = 1):
        self.movimiento = crear_movimiento()
        self.bola = crear_bola()
        self.coily = crear_coily()
        self.vidas = crear_vidas()
        self.estado_vidas = self.vidas.q0
        self.empezar_nivel(nivel)

    def empezar_nivel(self, nivel: int):
        self.cubo = crear_cubo(nivel)  # la misma definición sirve para los 28 cubos
        self.nivel = nivel
        self.estado_mov = self.movimiento.q0
        self.estado_bola = self.bola.q0
        self.estado_coily = self.coily.q0
        self.estados_cubos = [self.cubo.q0] * CANTIDAD_CUBOS
        self.salida_mealy = []  # palabra de salida de la Mealy en este nivel
        self.ultimo_paso: Paso | PasoTic | PasoTicCoily | None = None

    # --- salidas que se muestran -------------------------------------------
    def color(self, i: int) -> str:
        return self.cubo.g[self.estados_cubos[i]]

    def cantidad_vidas(self) -> int:
        return int(self.vidas.g[self.estado_vidas])

    def posicion(self) -> int:
        return CUBO_DEL_ESTADO[self.estado_mov]

    def salida_bola(self) -> str:
        """g_bola del estado actual: el cubo donde está la bola, o F si está fuera."""
        return self.bola.g[self.estado_bola]

    def posicion_bola(self) -> int | None:
        j = self.salida_bola()
        return None if j == FUERA else int(j)

    def fase_coily(self) -> str:
        if self.estado_coily.startswith("h"):
            return "huevo"
        if self.estado_coily.startswith("c"):
            return "persecucion"
        return "fuera"

    def posicion_coily(self) -> int | None:
        if self.fase_coily() == "fuera":
            return None
        return int(self.estado_coily[1:])

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

    # --- evento tecla: salta Q*bert ----------------------------------------
    def saltar(self, tecla: str) -> Paso | None:
        """Procesa una tecla. Devuelve el Paso, o None si el nivel/partida ya terminó."""
        if tecla not in self.movimiento.sigma_e:
            raise ValueError(f"'{tecla}' no pertenece a ΣE = {sorted(self.movimiento.sigma_e)}")
        if self.terminada():
            return None

        # Los saltos hacia afuera desde estos cubos conectan con los platos.
        usa_plato = PLATOS.get(self.posicion()) == tecla

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

        # 3) Q*bert pierde si aterriza en Coily; la caída también lo retira.
        coily_activo = self.fase_coily() != "fuera"
        choque_coily = (
            not usa_plato
            and mov.s != CAIDA
            and self.fase_coily() == "persecucion"
            and self.posicion_coily() == self.posicion()
        )

        # 4) vidas: lee X por caída o choque con cualquiera de los enemigos.
        j = self.salida_bola()
        choque_bola = not usa_plato and mov.s == j
        entrada = (
            CAIDA
            if (mov.s == CAIDA and not usa_plato) or choque_bola or choque_coily
            else "p"
        )
        [vid] = self.vidas.traza(entrada, self.estado_vidas)
        self.estado_vidas = vid.q_nuevo

        # 5) al perder una vida, ambos enemigos se retiran para evitar otro choque.
        retiro = self._retirar_bola() if vid.e == CAIDA or usa_plato else None
        retiro_coily = None
        if usa_plato and coily_activo:
            retiro_coily = self._transicionar_coily(SALTO_DISCO)
        elif vid.e == CAIDA and coily_activo:
            retiro_coily = self._retirar_coily()

        self.ultimo_paso = Paso(
            mov, paso_cubo, choque_bola, choque_coily, usa_plato, vid, retiro, retiro_coily,
        )
        return self.ultimo_paso

    # --- evento tic: se mueve la bola --------------------------------------
    def tic(self, direccion: str) -> PasoTic | None:
        """
        Pasa el tiempo: la bola lee direccion (s o d). Quien llama decide la
        dirección (en el juego, una moneda); así los tests pueden fijarla.
        Devuelve el PasoTic, o None si el nivel/partida ya terminó.
        """
        if direccion not in DIRECCIONES_BOLA:
            raise ValueError(f"la dirección de la bola tiene que ser s o d, no '{direccion}'")
        if self.terminada():
            return None

        # 1) Moore de la bola
        [bola] = self.bola.traza(direccion, self.estado_bola)
        self.estado_bola = bola.q_nuevo

        # 2) choque: la salida de la bola es el cubo donde está Q*bert
        choque = bola.s == str(self.posicion())
        vid = retiro = retiro_coily = None
        if choque:
            # 3) vidas lee X y la bola también, y se retira
            [vid] = self.vidas.traza(CAIDA, self.estado_vidas)
            self.estado_vidas = vid.q_nuevo
            retiro = self._retirar_bola()
            if self.fase_coily() != "fuera":
                retiro_coily = self._retirar_coily()

        self.ultimo_paso = PasoTic(bola, choque, vid, retiro, retiro_coily)
        return self.ultimo_paso

    def tic_coily(self, direccion: str) -> PasoTicCoily | None:
        """Aparece, baja el huevo o mueve a Coily un paso hacia Q*bert."""
        if direccion not in DIRECCIONES_BOLA:
            raise ValueError(f"la dirección de Coily tiene que ser s o d, no '{direccion}'")
        if self.terminada():
            return None

        if self.fase_coily() == "persecucion":
            movimiento = self._direccion_hacia_qbert()
            coily = self._transicionar_coily(movimiento)
            bono_caida = coily.s == CAIDA
        else:
            entrada = "S" if direccion == "s" else "D"
            coily = self._transicionar_coily(entrada)
            bono_caida = False

        choque = (
            self.fase_coily() == "persecucion"
            and self.posicion_coily() == self.posicion()
        )
        vidas = retiro_bola = retiro_coily = None
        if bono_caida:
            retiro_bola = self._retirar_bola()
        elif choque:
            [vidas] = self.vidas.traza(CAIDA, self.estado_vidas)
            self.estado_vidas = vidas.q_nuevo
            retiro_bola = self._retirar_bola()
            retiro_coily = self._retirar_coily()
        paso = PasoTicCoily(coily, choque, bono_caida, vidas, retiro_bola, retiro_coily)
        self.ultimo_paso = paso
        return paso

    def _direccion_hacia_qbert(self) -> str:
        """Elige una dirección greedy: primero reduce diferencia de fila, luego columna."""
        posicion_coily = self.posicion_coily()
        if posicion_coily is None:
            raise RuntimeError("Coily solo puede perseguir desde un cubo")
        fila_coily, columna_coily = fila_columna(posicion_coily)
        fila_qbert, columna_qbert = fila_columna(self.posicion())

        if fila_qbert > fila_coily:
            return "s" if columna_qbert <= columna_coily else "d"
        if fila_qbert < fila_coily:
            return "a" if columna_qbert < columna_coily else "w"
        if columna_qbert < columna_coily:
            return "a"
        return "d"

    def _transicionar_coily(self, entrada: str) -> Transicion:
        [paso] = self.coily.traza(entrada, self.estado_coily)
        self.estado_coily = paso.q_nuevo
        return paso

    def _retirar_coily(self) -> Transicion:
        return self._transicionar_coily(CAIDA)

    def _retirar_bola(self) -> Transicion:
        [t] = self.bola.traza(CAIDA, self.estado_bola)
        self.estado_bola = t.q_nuevo
        return t

    # --- otros -------------------------------------------------------------
    def pasar_de_nivel(self):
        """Empieza el nivel siguiente, conservando las vidas."""
        if not self.nivel_completo():
            raise ValueError("todavía no completaste el nivel")
        if self.ultimo_nivel():
            raise ValueError("ya estás en el último nivel")
        self.empezar_nivel(self.nivel + 1)

    def jugar(self, teclas: str) -> list[Paso]:
        """Procesa varias teclas seguidas, sin tics; se detiene si la partida termina."""
        pasos = []
        for t in teclas:
            p = self.saltar(t)
            if p is None:
                break
            pasos.append(p)
        return pasos
