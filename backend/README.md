# Backend

Tiene dos partes separadas:

```
backend/
  automatas/      LA LÓGICA: las máquinas del informe. Solo depende de automata-lib.
    mef.py          MEF = <Q, ΣE, ΣS, f, g>: clases Mealy y Moore, lectura de tablas
    movimiento.py   4.2  Mealy de movimiento
    cubo.py         4.3  Moore de color de cubo (una tabla por nivel)
    vidas.py        4.4  Moore de vidas
    partida.py      4.5  conexión entre máquinas (h, AF_i) y un salto
    piramide.py          geometría de la pirámide (no es una máquina)

  api/            LA API: expone automatas/ por HTTP con FastAPI. No tiene lógica propia.
    esquemas.py     modelos JSON (mismos nombres que contrato-api/openapi.yaml)
    conversion.py   objetos de automatas/ -> JSON
    rutas.py        endpoints
    main.py         la app

  consola.py      consola para probar las máquinas sin API ni frontend
  juego.py        ventana con pygame (opcional)
  tests/
    automatas/    tests de la lógica (incluye que automatas/ no dependa de la API)
    api/          tests de la API y de que cumpla el contrato
```

La regla: **`automatas/` no importa nada de `api/`, FastAPI ni pygame**.
`tests/automatas/test_independencia.py` falla si alguien rompe esa regla. Así la lógica
se puede leer, probar y presentar sola, y la API o el frontend se pueden cambiar sin tocarla.

## Levantarlo

Todos los comandos se corren desde `backend/`.

**La primera vez**, crear el entorno e instalar dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Cada vez**:

```bash
source .venv/bin/activate
uvicorn api.main:app --reload
```

- La API queda en `http://localhost:8000/api/...`.
- `http://localhost:8000/docs` muestra todas las rutas y permite probarlas desde el navegador.
- Con `--reload`, el servidor se reinicia solo cuando cambia el código.
- Para el frontend, dejar esta terminal abierta y seguir `../frontend/README.md` en otra.

## Tests

```bash
python -m pytest                    # todo
python -m pytest tests/automatas    # solo la lógica
```

Correrlos siempre antes de commitear.

## Probar la lógica sin API

```bash
python consola.py                   # modo interactivo; escribí "help"
python consola.py traducir mov sdw  # un comando suelto
```

```
qbert> mapa                          # numeración de los cubos
qbert> tabla mov                     # matriz f/g de la Mealy
qbert> traducir mov sdw              # traza paso a paso
qbert> traducir mov w q4             # arrancando desde q4
qbert> traducir vidas pXpXX
qbert> interseccion 3 0,1,2 0 1 2    # AFD intersección de los cubos 0, 1, 2
qbert> jugar 1                       # partida en texto (wasd + Enter)
qbert> diagrama vidas vidas.png      # grafo (necesita pygraphviz)
qbert> niveles
```

Máquinas: `mov`, `cubo1`, `cubo2`, `cubo3`, `vidas`.

Desde Python:

```python
>>> from automatas import crear_movimiento, Partida
>>> m = crear_movimiento()
>>> m.paso("q1", "a")
('q0', 'X')
>>> m.traducir("sdw")
(['1', '4', '2'], 'q2')
>>> p = Partida(1)
>>> print(p.saltar("s"))
Mealy:  f(q0, s) = q1    g(q0, s) = 1
Cubo 1: q0 --p--> q1/B
Vidas:  V3 --p--> V3/3
```

Ventana con pygame (opcional):

```bash
pip install pygame-ce
python juego.py         # W/A/S/D, ENTER siguiente nivel, R reiniciar, ESC salir
```

## Cómo están escritas las máquinas

automata-lib no tiene máquinas de Mealy ni de Moore. Cada $MEF = \langle Q, \Sigma_E, \Sigma_S, f, g\rangle$ se arma así:

- **f**: un `DFA` de automata-lib. Al crearlo, la librería valida que sea determinista y completo.
- **g**: una tabla aparte. En Mealy va por transición y en Moore por estado. La clase valida que esté definida en todo $Q$ y que solo devuelva símbolos de $\Sigma_S$.

Cada máquina se define con una tabla de texto con el mismo formato que el informe (`→` inicial, `*` final). Por ejemplo, el cubo del nivel 2 en `automatas/cubo.py`:

```
Q/ΣS    p
→q0/A   q1
q1/B    q2
q2/C*   q2
```

Si cambia una tabla en el informe, se cambia acá igual. `tabla <maquina>` en la consola la imprime en el mismo formato.

La caída se representa con `X` y no con `C`, para no confundirla con el color C del nivel 2.

## Qué comprueban los tests

- las 28 × 4 celdas de la tabla de movimiento coinciden con la geometría de la pirámide;
- cada tabla impresa se puede volver a leer y da la misma máquina;
- la salida de cada máquina tiene la misma longitud que la entrada;
- los niveles 1 y 2 se pueden completar sin perder vidas;
- la integración (4.5) da el mismo resultado que los AFD $AF_i$ leyendo la salida de la Mealy;
- la intersección de `automata-lib` (3.3) acepta exactamente cuando aceptan todos los cubos;
- `automatas/` no depende de la API;
- la API cumple `contrato-api/openapi.yaml`.
