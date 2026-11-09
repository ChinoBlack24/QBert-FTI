/**
 * Panel lateral: nivel, vidas, avance, colores del nivel y qué hizo cada
 * máquina en el último evento (salto de Q*bert o tic de la bola).
 */

import type { EstadoPartida, Transicion } from "../api/cliente";
import { COLORES } from "./colores";
import type { Evento } from "./useJuego";

type Linea = { texto: string; choque?: boolean };

const moore = (nombre: string, t: Transicion): Linea =>
  ({ texto: `${nombre} ${t.q} --${t.e}--> ${t.q_nuevo}/${t.s}` });

function lineasEvento(ev: Evento): Linea[] {
  if (ev.tipo === "salto") {
    const { movimiento: m, cubo: c, choque, choque_coily, uso_plato, vidas, retiro_bola,
      retiro_coily } = ev.paso;
    return [
      { texto: `Mealy:  f(${m.q}, ${m.e}) = ${m.q_nuevo}` },
      { texto: `        g(${m.q}, ${m.e}) = ${m.s}` },
      ...(c ? [{ texto: `Cubo ${c.cubo}: ${c.q} --p--> ${c.q_nuevo}/${c.color}` }] : []),
      ...(choque ? [{ texto: `¡Choque! Saltó sobre la bola`, choque: true }] : []),
      ...(choque_coily ? [{ texto: "¡Choque con Coily!", choque: true }] : []),
      ...(uso_plato ? [{ texto: "¡Plato volador! Q*bert vuelve a la cima y despeja los enemigos" }] : []),
      moore("Vidas: ", vidas),
      ...(retiro_bola ? [moore("Bola:  ", retiro_bola)] : []),
      ...(retiro_coily ? [moore("Coily:", retiro_coily)] : []),
    ];
  }
  if (ev.tipo === "tic") {
    const { bola, choque, vidas, retiro_bola, retiro_coily } = ev.paso;
    return [
      moore("Bola:  ", bola),
      ...(choque ? [{ texto: "¡Choque! La bola cayó sobre Q*bert", choque: true }] : []),
      ...(vidas ? [moore("Vidas: ", vidas)] : []),
      ...(retiro_bola ? [moore("Bola:  ", retiro_bola)] : []),
      ...(retiro_coily ? [moore("Coily:", retiro_coily)] : []),
    ];
  }
  const { coily, choque, vidas, retiro_bola, retiro_coily } = ev.paso;
  return [
    moore("Coily:", coily),
    ...(choque ? [{ texto: "¡El huevo eclosionó sobre Q*bert!", choque: true }] : []),
    ...(ev.paso.bono_caida
      ? [{ texto: "¡Coily cayó al perseguir! +50 puntos y enemigos despejados", choque: true }]
      : []),
    ...(vidas ? [moore("Vidas: ", vidas)] : []),
    ...(retiro_bola ? [moore("Bola:  ", retiro_bola)] : []),
    ...(retiro_coily ? [moore("Coily:", retiro_coily)] : []),
  ];
}

export function Panel({ estado, ultimo }: { estado: EstadoPartida; ultimo: Evento | null }) {
  const total = estado.colores.length;
  return (
    <aside className="panel">
      <h2>Nivel {estado.nivel}</h2>

      <dl className="datos">
        <dt>Vidas</dt>
        <dd>{"♥".repeat(estado.vidas) || "—"} <span className="tenue">({estado.estado_vidas})</span></dd>
        <dt>Cubos en el objetivo</dt>
        <dd>{estado.cubos_en_objetivo} / {total}</dd>
        <dt>Q*bert en</dt>
        <dd>{estado.estado_movimiento}</dd>
        <dt>Bola en</dt>
        <dd>
          {estado.estado_bola}
          {estado.posicion_bola === null && <span className="tenue"> (fuera)</span>}
        </dd>
        <dt>Coily en</dt>
        <dd>
          {estado.estado_coily} <span className="tenue">({estado.fase_coily})</span>
          {estado.posicion_coily !== null && ` · cubo ${estado.posicion_coily}`}
        </dd>
      </dl>

      <h3>Colores de este nivel</h3>
      <ul className="colores">
        {estado.colores_nivel.map((c) => (
          <li key={c.estado}>
            <span className="muestra" style={{ background: COLORES[c.color] }} />
            {c.estado}/{c.color}
            {c.objetivo && <span className="tenue"> (objetivo)</span>}
          </li>
        ))}
      </ul>

      <h3>Último evento {ultimo && <span className="tenue">({ultimo.tipo})</span>}</h3>
      {ultimo
        ? (
          <pre className="traza">
            {lineasEvento(ultimo).map((l, i) => (
              <div key={i} className={l.choque ? "choque" : undefined}>{l.texto}</div>
            ))}
          </pre>
        )
        : <p className="tenue">(todavía ninguno)</p>}

      <h3>Controles</h3>
      <p className="tenue ayuda">
        W arriba-der · A arriba-izq<br />
        S abajo-izq · D abajo-der<br />
        Desde el cubo 10, A usa el plato izquierdo; desde el 14, W usa el derecho.<br />
        ENTER siguiente nivel · R reiniciar<br />
        La bola y el huevo aparecen con esperas aleatorias.<br />
        El huevo baja hasta la base; Coily decide su ruta hacia Q*bert.<br />
        Si cae persiguiéndote, despeja enemigos y suma 50 puntos.
      </p>
    </aside>
  );
}
