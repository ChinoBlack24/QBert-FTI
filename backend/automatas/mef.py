"""
Máquina Secuencial genérica, como la define la cátedra:  MEF = <Q, ΣE, ΣS, f, g>

    f: Q x ΣE -> Q          función de transición
    Mealy  g: Q x ΣE -> ΣS  la salida va en la transición
    Moore  g: Q -> ΣS       la salida es la del estado al que se transiciona

automata-lib no trae máquinas de Mealy ni de Moore, pero sí AFD. Por eso:

  - f se guarda como un DFA de automata-lib. Al construirlo, la librería
    valida que f sea total y determinista (todo par (q, e) tiene un único
    destino). Si falta una celda en una tabla, el programa no arranca.
  - g se guarda aparte, y esta clase valida que esté definida en todo su
    dominio y que solo devuelva símbolos de ΣS.

Las máquinas se escriben como tablas de texto con el mismo formato que el
informe y que imprime tabla():

    Mealy                         Moore
    Q     w      a                Q/ΣS    p
    →q0   q1/1   q0/X             →q0/A   q1
    q1    q0/0   q0/X             q1/B*   q1

→ marca el estado inicial y * los finales.
"""

from __future__ import annotations

from typing import NamedTuple

from automata.fa.dfa import DFA

INICIAL = "→"
FINAL = "*"


class Transicion(NamedTuple):
    """Un paso de una MEF: estando en q lee e, pasa a q_nuevo y escribe s."""
    q: str
    e: str
    q_nuevo: str
    s: str


class MEF:
    """Base común de Mealy y Moore: <Q, ΣE, ΣS, f, g>."""

    tipo = "MEF"

    def __init__(self, nombre: str, f: dict, g: dict, sigma_s, q0: str, finales=()):
        self.nombre = nombre
        self.orden = list(f)  # estados en el orden de la tabla
        self.simbolos = list(next(iter(f.values())))  # ΣE en el orden de las columnas
        self.f = DFA(
            states=set(f),
            input_symbols=set(self.simbolos),
            transitions=f,
            initial_state=q0,
            final_states=set(finales),
        )
        self.g = g
        self.sigma_s = frozenset(sigma_s)
        self._validar_g()

    # --- componentes de la quíntupla ---------------------------------------
    @property
    def Q(self):
        return self.f.states

    @property
    def sigma_e(self):
        return self.f.input_symbols

    @property
    def q0(self):
        return self.f.initial_state

    @property
    def finales(self):
        return self.f.final_states

    # --- funcionamiento ----------------------------------------------------
    def paso(self, q: str, e: str) -> tuple[str, str]:
        """Lee e estando en q. Devuelve (nuevo estado, salida)."""
        raise NotImplementedError

    def traza(self, palabra, q=None) -> list[Transicion]:
        """Las transiciones al leer la palabra desde q (por defecto q0)."""
        q = self.q0 if q is None else q
        if q not in self.Q:
            raise ValueError(f"'{q}' no pertenece a Q")
        pasos = []
        for e in palabra:
            if e not in self.sigma_e:
                raise ValueError(f"'{e}' no pertenece a ΣE = {sorted(self.sigma_e)}")
            nuevo, s = self.paso(q, e)
            pasos.append(Transicion(q, e, nuevo, s))
            q = nuevo
        return pasos

    def traducir(self, palabra, q=None):
        """Devuelve (salida, estado final). |salida| = |palabra|, como pide la cátedra."""
        pasos = self.traza(palabra, q)
        final = pasos[-1].q_nuevo if pasos else (self.q0 if q is None else q)
        return [t.s for t in pasos], final

    # --- tabla en el formato del informe -----------------------------------
    def tabla(self) -> str:
        raise NotImplementedError

    def _marca(self, q: str) -> str:
        return INICIAL + q if q == self.q0 else q

    def __repr__(self):
        return f"<{self.tipo} {self.nombre}: |Q|={len(self.Q)}, ΣE={sorted(self.sigma_e)}>"


class Mealy(MEF):
    tipo = "Mealy"

    def _validar_g(self):
        for q in self.Q:
            for e in self.sigma_e:
                if e not in self.g.get(q, {}):
                    raise ValueError(f"g({q}, {e}) no está definida")
                if self.g[q][e] not in self.sigma_s:
                    raise ValueError(f"g({q}, {e}) = {self.g[q][e]} no pertenece a ΣS")

    def paso(self, q, e):
        return self.f.transitions[q][e], self.g[q][e]

    def tabla(self):
        filas = [["Q"] + self.simbolos]
        for q in self.orden:
            fin = FINAL if q in self.finales else ""
            filas.append([f"{self._marca(q)}{fin}"] +
                         [f"{self.f.transitions[q][e]}/{self.g[q][e]}" for e in self.simbolos])
        return _formatear(filas)


class Moore(MEF):
    tipo = "Moore"

    def _validar_g(self):
        for q in self.Q:
            if q not in self.g:
                raise ValueError(f"g({q}) no está definida")
            if self.g[q] not in self.sigma_s:
                raise ValueError(f"g({q}) = {self.g[q]} no pertenece a ΣS")

    def paso(self, q, e):
        p = self.f.transitions[q][e]
        return p, self.g[p]  # salida del estado al que se transiciona

    def tabla(self):
        filas = [["Q/ΣS"] + self.simbolos]
        for q in self.orden:
            fin = FINAL if q in self.finales else ""
            filas.append([f"{self._marca(q)}/{self.g[q]}{fin}"] +
                         [self.f.transitions[q][e] for e in self.simbolos])
        return _formatear(filas)


def _formatear(filas):
    anchos = [max(len(str(f[c])) for f in filas) for c in range(len(filas[0]))]
    lineas = ["  ".join(str(x).ljust(a) for x, a in zip(f, anchos)).rstrip() for f in filas]
    lineas.insert(1, "  ".join("-" * a for a in anchos))
    return "\n".join(lineas)


# ===========================================================================
# Lectura de tablas
# ===========================================================================
def _filas(texto: str):
    """Filas de la tabla, sin líneas vacías ni la línea de guiones de tabla()."""
    filas = [linea.split() for linea in texto.strip().splitlines()]
    return [f for f in filas if f and not f[0].startswith("-")]


def _sacar_marcas(celda: str, q0, finales):
    """'→q0/A*' -> 'q0/A', y anota si es inicial o final."""
    es_inicial = celda.startswith(INICIAL)
    es_final = celda.endswith(FINAL)
    celda = celda.removeprefix(INICIAL).removesuffix(FINAL)
    estado = celda.split("/")[0]
    if es_inicial:
        q0.append(estado)
    if es_final:
        finales.add(estado)
    return celda


def _un_inicial(q0: list) -> str:
    if len(q0) != 1:
        raise ValueError(f"la tabla tiene que marcar exactamente un estado inicial con {INICIAL}")
    return q0[0]


def leer_tabla_mealy(texto: str):
    """Tabla de Mealy -> (f, g, q0, finales). Cada celda es estado_nuevo/salida."""
    encabezado, *filas = _filas(texto)
    simbolos = encabezado[1:]
    f, g, q0, finales = {}, {}, [], set()
    for primera, *celdas in filas:
        q = _sacar_marcas(primera, q0, finales)
        f[q], g[q] = {}, {}
        for e, celda in zip(simbolos, celdas, strict=True):
            f[q][e], g[q][e] = celda.split("/")
    return f, g, _un_inicial(q0), finales


def leer_tabla_moore(texto: str):
    """Tabla de Moore -> (f, g, q0, finales). La primera columna es estado/salida."""
    encabezado, *filas = _filas(texto)
    simbolos = encabezado[1:]
    f, g, q0, finales = {}, {}, [], set()
    for primera, *celdas in filas:
        q, salida = _sacar_marcas(primera, q0, finales).split("/")
        g[q] = salida
        f[q] = dict(zip(simbolos, celdas, strict=True))
    return f, g, _un_inicial(q0), finales
