/**
 * La pirámide en perspectiva isométrica, en SVG. Recibe todo calculado:
 * la posición (fila, columna) de cada cubo viene del backend (/api/piramide)
 * y los colores y las posiciones de Q*bert y de la bola, del estado de la partida.
 */

import type { EstadoPartida, Paso, Piramide as DatosPiramide } from "../api/cliente";
import { BolaSprite } from "./BolaSprite";
import { COLORES } from "./colores";
import { type Fase, QbertSprite } from "./QbertSprite";
import { TAMANO_QBERT } from "./qbertDimensiones";
import { useSalto } from "./useSalto";
import { MS_SALTO, type Evento, type VistaQbert } from "./useJuego";

const LADO = 72;       // ancho de la cara superior de un cubo
const ALTO_CARA = 40;  // alto de las caras laterales
const MEDIO = LADO / 2;
const CUARTO = LADO / 4;

// Cómo saltan. Un salto normal mide un poco más de medio cubo; uno mucho más
// largo (reaparecer arriba después de caerse) no se anima.
const SALTO_QBERT = { duracion: MS_SALTO, altura: 30, maximo: LADO * 1.6 };
// Al caerse salta fuera de la pirámide y sigue cayendo: sin límite de distancia.
const CAIDA_QBERT = { duracion: MS_SALTO, altura: 30, maximo: Infinity };
const CAIDA_EXTRA = 140;   // cuánto más abajo del borde termina la caída

// Cómo cambia (fila, columna) con cada tecla, igual que en backend/automatas/piramide.py.
const DESPLAZAMIENTOS = { w: [-1, 0], a: [-1, -1], s: [1, 0], d: [1, 1] } as const;
const SALTO_BOLA = { duracion: 260, altura: 18, maximo: LADO * 1.6 };

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

/** Con qué animación arranca Q*bert después del último evento. */
function faseInicial(ultimo: Evento | null): Fase {
  if (!ultimo) return "quieto";
  if (ultimo.paso.vidas?.e === "X") return "golpe";   // se cayó o lo chocó la bola
  return ultimo.tipo === "salto" ? "salto" : "quieto";
}

function Qbert({ x, y, cayendo, ultimo, ultimoSalto, clave, explosion }: {
  x: number; y: number; cayendo: boolean; ultimo: Evento | null; ultimoSalto: Paso | null;
  clave: string; explosion: { id: number; src: string } | null;
}) {
  const pos = useSalto(x, y, cayendo ? CAIDA_QBERT : SALTO_QBERT);
  return (
    // El <g> salta en arco de cubo a cubo (useSalto). El sprite de adentro se
    // vuelve a montar (key) en cada salto y en cada vida perdida, para que
    // arranque la animación de salto o de golpe.
    // Al caerse además se desvanece, así se ve que sale de la pirámide por cualquier borde.
    <g className="qbert" transform={`translate(${pos.x}, ${pos.y})`}
      style={cayendo ? { opacity: 0, transition: `opacity ${MS_SALTO}ms ease-in` } : undefined}>
      <QbertSprite key={clave} tecla={ultimoSalto?.movimiento.e ?? "d"} inicial={faseInicial(ultimo)} />
      {explosion && (
        <image
          key={explosion.id}
          href={explosion.src}
          x={-TAMANO_QBERT.ancho / 2}
          y={-TAMANO_QBERT.alto + 10}
          width={TAMANO_QBERT.ancho}
          height={TAMANO_QBERT.alto}
          className="sprite explosion"
          pointerEvents="none"
        />
      )}
    </g>
  );
}

function Bola({ x, y, cubo }: { x: number; y: number; cubo: number }) {
  const pos = useSalto(x, y, SALTO_BOLA);
  return (
    // El <g> salta en arco de cubo a cubo; el sprite se vuelve a montar (key)
    // en cada cubo nuevo para que haga el rebote.
    <g className="bola" transform={`translate(${pos.x}, ${pos.y})`}>
      <BolaSprite key={cubo} />
    </g>
  );
}

export function Piramide({ datos, estado, ultimo, ultimoSalto, coloresCongelados, vistaQbert, explosion, gameoverGif }: {
  datos: DatosPiramide; estado: EstadoPartida; ultimo: Evento | null; ultimoSalto: Paso | null;
  coloresCongelados: string[] | null; vistaQbert: VistaQbert;
  explosion: { id: number; src: string } | null;
  gameoverGif: { src: string; duracionMs: number } | null;
}) {
  const cubos = datos.cubos.map((c) => ({ ...c, ...centro(c.fila, c.columna) }));
  const colores = coloresCongelados ?? estado.colores;

  // Hacia dónde se dibuja Q*bert. Al caerse, el backend ya lo tiene en q0;
  // en pantalla salta al lugar donde estaría el cubo de afuera y sigue cayendo.
  let qbert = cubos[estado.posicion];
  if (vistaQbert.tipo === "cayendo") {
    const desde = cubos[vistaQbert.desde];
    const [df, dc] = DESPLAZAMIENTOS[vistaQbert.tecla];
    const afuera = centro(desde.fila + df, desde.columna + dc);
    qbert = { ...desde, x: afuera.x, y: afuera.y + CAIDA_EXTRA };
  }
  const bola = estado.posicion_bola === null ? null : cubos[estado.posicion_bola];
  const ancho = datos.filas * LADO;
  const alto = (datos.filas - 1) * (MEDIO + ALTO_CARA) + CUARTO + ALTO_CARA;

  return (
    <>
      <svg className="piramide" viewBox={`${-ancho / 2} ${-CUARTO - 40} ${ancho} ${alto + CUARTO + 50}`}>
        {cubos.map((c) => (
          <Cubo key={c.numero} x={c.x} y={c.y} color={COLORES[colores[c.numero]] ?? "#888"} />
        ))}
        {bola && <Bola x={bola.x} y={bola.y} cubo={bola.numero} />}
        {/* Oculto mientras espera para reaparecer: al volver se monta de nuevo en la cima. */}
        {(!estado.game_over || explosion !== null) && vistaQbert.tipo !== "oculto" && (
          <Qbert x={qbert.x} y={qbert.y} cayendo={vistaQbert.tipo === "cayendo"}
            ultimo={ultimo} ultimoSalto={ultimoSalto}
            clave={`${estado.salida_mealy.length}-${estado.vidas}`} explosion={explosion} />
        )}
      </svg>
      {gameoverGif && <img className="gameover-overlay" src={gameoverGif.src} alt="Game over" />}
    </>
  );
}
