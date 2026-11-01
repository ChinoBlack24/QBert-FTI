/**
 * Panel lateral: nivel, vidas, avance, colores del nivel y qué hizo cada
 * máquina en el último salto.
 */

import type { EstadoPartida, Paso } from "../api/cliente";
import { COLORES } from "./colores";

function lineasPaso(p: Paso): string[] {
  const m = p.movimiento;
  const v = p.vidas;
  const lineas = [`Mealy:  f(${m.q}, ${m.e}) = ${m.q_nuevo}    g(${m.q}, ${m.e}) = ${m.s}`];
  if (p.cubo) {
    const c = p.cubo;
    lineas.push(`Cubo ${c.cubo}: ${c.q} --p--> ${c.q_nuevo}/${c.color}`);
  }
  lineas.push(`Vidas:  ${v.q} --${v.e}--> ${v.q_nuevo}/${v.s}`);
  return lineas;
}

export function Panel({ estado, ultimoPaso }: { estado: EstadoPartida; ultimoPaso: Paso | null }) {
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

      <h3>Último salto</h3>
      {ultimoPaso
        ? <pre className="traza">{lineasPaso(ultimoPaso).join("\n")}</pre>
        : <p className="tenue">(todavía ninguno)</p>}

      <h3>Controles</h3>
      <p className="tenue ayuda">
        W arriba-der · A arriba-izq<br />
        S abajo-izq · D abajo-der<br />
        ENTER siguiente nivel · R reiniciar
      </p>
    </aside>
  );
}
