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
    Piramide.tsx   la pirámide isométrica y Q*bert (SVG)
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

Mínimo jugable: la pirámide, Q*bert, los controles (W/A/S/D, ENTER para pasar de nivel,
R para reiniciar) y un panel con vidas, avance y lo que hizo cada máquina en el último salto.

Pendiente: paneles con las máquinas completas (tabla/diagrama con el estado actual resaltado).
