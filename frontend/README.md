# Frontend

React + TypeScript, armado con Vite. **Solo dibuja**: toda la lógica de los
autómatas está en `backend/automatas/`, y el frontend la usa a través de la API.

## Levantarlo

Necesita Node.js 20 o más nuevo (`node --version`).

**La primera vez**, desde `frontend/`:

```bash
npm install
```

**Cada vez**, con dos terminales:

```bash
# Terminal 1: el backend (ver ../backend/README.md)
cd backend
source .venv/bin/activate
uvicorn api.main:app --reload

# Terminal 2: el frontend
cd frontend
npm run dev
```

Abrir `http://localhost:5173`. Los cambios en el código se ven sin recargar.

Si la página dice **"No se pudo conectar con el backend: Bad Gateway"**, es que el
backend no está corriendo. En desarrollo, Vite reenvía todo lo que empieza con `/api`
a `http://localhost:8000` (ver `vite.config.ts`). Si ahí no hay nadie, responde Bad Gateway.

## Otros comandos

```bash
npm run build    # chequea tipos y arma la versión final en dist/
npm run lint     # revisa el código
npm run tipos    # regenera src/api/esquema.d.ts desde ../contrato-api/openapi.yaml
```

## Cómo hablar con el backend

```
src/
  api/
    esquema.d.ts   tipos generados del contrato (no editar a mano: npm run tipos)
    cliente.ts     funciones que hacen fetch a la API
  juego/
    useJuego.ts    estado del juego: manda cada acción al backend y guarda la respuesta
    Piramide.tsx   la pirámide isométrica, Q*bert, la bola y Coily (SVG)
    QbertSprite.tsx  Q*bert con sprites (hacia dónde mira = última tecla de la Mealy)
    BolaSprite.tsx   la bola roja con sprites (rebota al caer en cada cubo)
    useSalto.ts      el salto en arco (parábola) de los personajes entre cubos
    Panel.tsx      nivel, vidas, colores y la traza del último salto
    colores.ts     color de pantalla de cada salida A, B, C
  App.tsx          arma la pantalla y escucha el teclado
  estilos.css
  main.tsx
```

Los componentes **nunca hacen `fetch` directo**: usan las funciones de `src/api/cliente.ts`.
Es el único archivo que conoce las URLs.

```ts
import { crearPartida, saltar } from "./api/cliente";

const partida = await crearPartida(1);
const { paso, estado } = await saltar(partida.id, "s");
// paso.movimiento: { q: "q0", e: "s", q_nuevo: "q1", s: "1" }
// estado.colores[1] === "B"
```

Si la API devuelve un error, se lanza `ErrorApi` con `status` (404, 409, …) y el mensaje del backend.

### Si cambia la API

1. Se edita `../contrato-api/openapi.yaml`.
2. `npm run tipos` regenera los tipos.
3. `npm run build` muestra todo lo que dejó de compilar por el cambio.

`npm run tipos` usa su propio TypeScript 5 vía `npx`, porque openapi-typescript
todavía no soporta TypeScript 7, que es el que usa el proyecto. No hace falta instalarlo aparte.

## Estado

Mínimo jugable: la pirámide, Q*bert, la bola, Coily, los controles (W/A/S/D, ENTER para pasar de nivel,
R para reiniciar) y un panel con vidas, avance y lo que hizo cada máquina en el último evento.
Cada cambio real de color de un cubo suma 30 puntos y completar un nivel suma 100. El puntaje
actual se reinicia al empezar una partida nueva; el récord se conserva en `localStorage` del navegador.

El reloj de la bola está en `src/juego/useJuego.ts`: manda `POST /tic` cada `MS_POR_TIC`
(800 ms) mientras la bola baja, y espera un tiempo al azar (`MS_REAPARECER`, 1,5 a 4 s)
cuando está fuera, antes de que vuelva a aparecer. Arranca con el primer salto de cada
nivel. Es solo el ritmo: dónde va la bola y qué pasa al chocar lo decide el backend.

El huevo de Coily usa su propio temporizador: aparece después de una espera aleatoria de
1,5 a 4 s y baja cada 800 ms siguiendo la misma geometría que la bola. Al llegar a la
fila inferior eclosiona; durante la persecución avanza cada 1 s (el doble de los 500 ms
de duración del salto de Q*bert) y decide una diagonal hacia él comparando primero la
fila y luego la columna. Si su movimiento lo saca de la pirámide, despeja a la bola y
suma 50 puntos. Se representa provisionalmente con formas SVG básicas, sin archivos de
sprite.

Hay platos voladores reutilizables junto a los cubos 10 y 14. Desde el cubo 10, pulsa
A para saltar hacia afuera y volver a la cima; desde el 14, usa W. Los platos están
elevados y más separados de los cubos. El viaje animado hasta la cima dura 2 segundos;
durante ese tiempo se pausan los enemigos y los controles. El plato evita la pérdida
de vida y despeja a la bola y a Coily.

Los sprites están en `public/sprites/` (créditos en `public/sprites/CREDITOS.md`).

Pendiente: paneles con las máquinas completas (tabla/diagrama con el estado actual resaltado).
