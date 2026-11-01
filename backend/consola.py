"""
Consola para probar las máquinas sin ventana.

    python consola.py                     # modo interactivo (escribí 'help')
    python consola.py traducir mov sdw    # un solo comando y sale

Máquinas disponibles:  mov, cubo1, cubo2, cubo3, vidas
"""

from __future__ import annotations

import cmd
import shlex
import sys

from automatas import (CANTIDAD_CUBOS, FILAS, MAQUINAS, MEF, NIVELES, Partida, crear_cubo,
                       crear_cubo_sobre_salida, descripcion_nivel, numero_cubo)

COLOR_ANSI = {"A": "\033[93m", "B": "\033[94m", "C": "\033[92m"}
RESET = "\033[0m"


def _pintar(letra: str) -> str:
    if not sys.stdout.isatty():
        return letra
    return f"{COLOR_ANSI.get(letra, '')}{letra}{RESET}"


def dibujar_piramide(celda) -> str:
    """celda(i) -> texto de 3 caracteres visibles para el cubo i."""
    lineas = []
    for r in range(FILAS):
        sangria = " " * (2 * (FILAS - 1 - r))
        lineas.append(sangria + " ".join(celda(numero_cubo(r, k)) for k in range(r + 1)))
    return "\n".join(lineas)


def dibujar_partida(p: Partida) -> str:
    def celda(i):
        c = _pintar(p.color(i))
        return f"[{c}]" if i == p.posicion() and not p.game_over() else f" {c} "
    estado = (f"Nivel {p.nivel}  |  vidas: {p.cantidad_vidas()}  |  "
              f"cubos en objetivo: {p.cubos_en_objetivo()}/{CANTIDAD_CUBOS}  |  "
              f"Q*bert en {p.estado_mov} ([ ])")
    return dibujar_piramide(celda) + "\n" + estado


def _maquina(nombre: str) -> MEF:
    if nombre not in MAQUINAS:
        raise ValueError(f"máquina desconocida '{nombre}'. Opciones: {', '.join(MAQUINAS)}")
    return MAQUINAS[nombre]()


class Consola(cmd.Cmd):
    intro = "Q*bert con autómatas. Escribí 'help' para ver los comandos, 'salir' para terminar."
    prompt = "qbert> "

    # --- utilidades --------------------------------------------------------
    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except (ValueError, KeyError, IndexError) as e:
            print(f"Error: {e}")

    def emptyline(self):
        pass

    def default(self, line):
        print(f"Comando desconocido: {line.split()[0]}. Escribí 'help'.")

    # --- comandos ----------------------------------------------------------
    def do_maquinas(self, arg):
        """maquinas
        Lista las máquinas con su quíntupla resumida."""
        for nombre, crear in MAQUINAS.items():
            m = crear()
            print(f"{nombre:<6} {m.tipo:<6} |Q|={len(m.Q):<3} ΣE={sorted(m.sigma_e)}  "
                  f"|ΣS|={len(m.sigma_s)}")

    def do_tabla(self, arg):
        """tabla <maquina>
        Muestra la matriz f/g en el formato del apunte (→ inicial, * final).
        Ej: tabla mov | tabla cubo2 | tabla vidas"""
        m = _maquina(arg.strip())
        print(f"{m.tipo} {m.nombre}  ΣS = {{{', '.join(sorted(m.sigma_s, key=_orden))}}}")
        print(m.tabla())

    def do_traducir(self, arg):
        """traducir <maquina> <palabra> [estado_inicial]
        Traduce la palabra paso a paso y muestra la salida.
        Ej: traducir mov sdw | traducir cubo3 ppp | traducir vidas pXpXX | traducir mov w q4"""
        partes = arg.split()
        if len(partes) < 2:
            raise ValueError("uso: traducir <maquina> <palabra> [estado_inicial]")
        m = _maquina(partes[0])
        q = partes[2] if len(partes) > 2 else None
        pasos = m.traza(partes[1], q)
        for n, t in enumerate(pasos, 1):
            izq = f"f({t.q}, {t.e}) = {t.q_nuevo}"
            print(f"  {n:>2}. {izq:<18}{m.explicar_salida(t)}")
        salida = [t.s for t in pasos]
        print(f"  entrada: {partes[1]}  (|{len(partes[1])}|)")
        print(f"  salida:  {' '.join(salida)}  (|{len(salida)}|)")

    def do_mapa(self, arg):
        """mapa
        Muestra la numeración de los cubos (estado q_i = Q*bert sobre el cubo i)."""
        print(dibujar_piramide(lambda i: f"{i:>2} "))
        print("w: arriba-der   a: arriba-izq   s: abajo-izq   d: abajo-der")

    def do_interseccion(self, arg):
        """interseccion <nivel> <cubos> <salidas de la Mealy...>
        Construye con automata-lib el AFD intersección de los cubos indicados
        (sección 3.3) y evalúa la palabra de salida de la Mealy.
        Ej: interseccion 3 0,1,2 0 1 2
            interseccion 2 1,2 1 2 X 1 2"""
        partes = arg.split()
        if len(partes) < 2:
            raise ValueError("uso: interseccion <nivel> <cubos> <salidas...>")
        nivel = int(partes[0])
        cubos = [int(c) for c in partes[1].split(",")]
        palabra = partes[2:]
        afds = [crear_cubo_sobre_salida(nivel, i) for i in cubos]
        producto = afds[0]
        for a in afds[1:]:
            producto = producto & a
        por_componente = all(a.accepts_input(palabra) for a in afds)
        print(f"  nivel {nivel}, cubos {cubos}: |Q| de cada uno = {len(afds[0].states)}, "
              f"|Q| intersección = {len(producto.states)}")
        print(f"  palabra {' '.join(palabra) or 'λ'}:")
        print(f"    aceptada por la intersección: {producto.accepts_input(palabra)}")
        print(f"    aceptada por cada cubo:       {por_componente}")

    def do_jugar(self, arg):
        """jugar [nivel]
        Partida en la consola. Escribí una o más teclas (wasd) y Enter.
        Dentro del juego: 'n' siguiente nivel, 'r' reiniciar, 'v' ver traza on/off, 'q' volver."""
        nivel = int(arg) if arg.strip() else 1
        p = Partida(nivel)
        ver_traza = True
        print(dibujar_partida(p))
        while True:
            try:
                linea = input("jugar> ").strip().lower()
            except EOFError:
                print()
                return
            if linea == "q":
                return
            if linea == "r":
                p = Partida(nivel)
            elif linea == "v":
                ver_traza = not ver_traza
                print(f"traza {'activada' if ver_traza else 'desactivada'}")
                continue
            elif linea == "n":
                try:
                    p.pasar_de_nivel()
                except ValueError as e:
                    print(f"No se puede: {e}.")
                    continue
            else:
                invalidas = set(linea) - set("wasd")
                if invalidas:
                    print(f"Teclas inválidas: {''.join(sorted(invalidas))}. Usá w, a, s, d.")
                    continue
                for paso in p.jugar(linea):
                    if ver_traza:
                        print("  " + "\n  ".join(paso.lineas()))
            print(dibujar_partida(p))
            if p.game_over():
                print("GAME OVER  ('r' reinicia, 'q' sale)")
            elif p.nivel_completo():
                print("¡Ganaste todos los niveles!" if p.ultimo_nivel()
                      else "¡Nivel completo! ('n' siguiente nivel)")

    def do_diagrama(self, arg):
        """diagrama <maquina> <archivo.png>
        Dibuja el grafo de transición y salida (necesita pygraphviz).
        Mealy: arcos e/s.  Moore: nodos q/s.
        Ej: diagrama vidas vidas.png"""
        partes = arg.split()
        if len(partes) != 2:
            raise ValueError("uso: diagrama <maquina> <archivo.png>")
        try:
            import pygraphviz as pgv
        except ImportError:
            print("Falta pygraphviz: sudo apt install graphviz graphviz-dev && pip install pygraphviz")
            return
        m = _maquina(partes[0])
        G = pgv.AGraph(directed=True, rankdir="LR")
        G.add_node("_ini", shape="point")
        for q in m.orden:
            forma = "doublecircle" if q in m.finales else "circle"
            G.add_node(q, label=m.etiqueta_estado(q), shape=forma)
        G.add_edge("_ini", m.q0)
        arcos = {}
        for q in m.orden:
            for e in m.simbolos:
                q2 = m.f.transitions[q][e]
                arcos.setdefault((q, q2), []).append(m.etiqueta_arco(q, e))
        for (q, q2), etiquetas in arcos.items():
            G.add_edge(q, q2, label=", ".join(etiquetas))
        G.draw(partes[1], prog="dot")
        print(f"Guardado en {partes[1]}")

    def do_niveles(self, arg):
        """niveles
        Describe el comportamiento de los cubos en cada nivel."""
        for n in NIVELES:
            cubo = crear_cubo(n)
            objetivo = ", ".join(f"{q}/{cubo.g[q]}" for q in sorted(cubo.finales))
            print(f"  nivel {n}: {descripcion_nivel(n)}, objetivo {objetivo}")

    def do_salir(self, arg):
        """salir
        Cierra la consola."""
        return True

    do_exit = do_quit = do_salir
    do_EOF = do_salir


def _orden(s):
    return (0, int(s)) if s.isdigit() else (1, s)


if __name__ == "__main__":
    consola = Consola()
    if len(sys.argv) > 1:
        consola.onecmd(shlex.join(sys.argv[1:]))
    else:
        try:
            consola.cmdloop()
        except KeyboardInterrupt:
            print()
