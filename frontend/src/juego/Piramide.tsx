/**
 * La pirámide en perspectiva isométrica, en SVG. Recibe todo calculado:
 * la posición (fila, columna) de cada cubo viene del backend (/api/piramide)
 * y los colores y la posición de Q*bert, del estado de la partida.
 */

import type { EstadoPartida, Piramide as DatosPiramide } from "../api/cliente";
import { COLORES } from "./colores";

const LADO = 72;       // ancho de la cara superior de un cubo
const ALTO_CARA = 40;  // alto de las caras laterales
const MEDIO = LADO / 2;
const CUARTO = LADO / 4;

function centro(fila: number, columna: number) {
  return { x: (columna - fila / 2) * LADO, y: fila * (MEDIO + ALTO_CARA) };
}

const puntos = (ps: [number, number][]) => ps.map(([x, y]) => `${x},${y}`).join(" ");

function Cubo({ x, y, color }: { x: number; y: number; color: string }) {
  return (
    <g>
      <polygon className="cara-izq"
        points={puntos([[x - MEDIO, y], [x, y + CUARTO], [x, y + CUARTO + ALTO_CARA], [x - MEDIO, y + ALTO_CARA]])} />
      <polygon className="cara-der"
        points={puntos([[x + MEDIO, y], [x, y + CUARTO], [x, y + CUARTO + ALTO_CARA], [x + MEDIO, y + ALTO_CARA]])} />
      <polygon className="cara-sup" fill={color}
        points={puntos([[x, y - CUARTO], [x + MEDIO, y], [x, y + CUARTO], [x - MEDIO, y]])} />
    </g>
  );
}

function Qbert({ x, y }: { x: number; y: number }) {
  return (
    <g className="qbert" style={{ transform: `translate(${x}px, ${y - 14}px)` }}>
      <circle r={15} className="qbert-cuerpo" />
      <circle cx={13} cy={6} r={7} className="qbert-cuerpo" />
      <circle cx={2} cy={-4} r={5} fill="#fff" />
      <circle cx={4} cy={-4} r={2} fill="#000" />
    </g>
  );
}

export function Piramide({ datos, estado }: { datos: DatosPiramide; estado: EstadoPartida }) {
  const cubos = datos.cubos.map((c) => ({ ...c, ...centro(c.fila, c.columna) }));
  const qbert = cubos[estado.posicion];
  const ancho = datos.filas * LADO;
  const alto = (datos.filas - 1) * (MEDIO + ALTO_CARA) + CUARTO + ALTO_CARA;

  return (
    <svg className="piramide" viewBox={`${-ancho / 2} ${-CUARTO - 40} ${ancho} ${alto + CUARTO + 50}`}>
      {cubos.map((c) => (
        <Cubo key={c.numero} x={c.x} y={c.y} color={COLORES[estado.colores[c.numero]] ?? "#888"} />
      ))}
      {!estado.game_over && <Qbert x={qbert.x} y={qbert.y} />}
    </svg>
  );
}
