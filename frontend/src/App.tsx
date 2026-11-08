/**
 * Mínimo jugable: la pirámide, Q*bert, la bola, el teclado y un panel con el estado.
 * Toda la lógica la resuelve el backend; acá solo se dibuja lo que devuelve.
 */

import { useEffect } from "react";
import type { Tecla } from "./api/cliente";
import { Panel } from "./juego/Panel";
import { Piramide } from "./juego/Piramide";
import { useJuego } from "./juego/useJuego";

const TECLAS: Record<string, Tecla> = { w: "w", a: "a", s: "s", d: "d" };

export default function App() {
  const {
    piramide, estado, ultimo, ultimoSalto, coloresCongelados, vistaQbert, error,
    puntaje, mejorPuntaje, errorPuntaje, saltar, siguienteNivel, nuevaPartida,
  } = useJuego();

  useEffect(() => {
    function alApretar(ev: KeyboardEvent) {
      if (ev.repeat) return;
      const tecla = ev.key.toLowerCase();
      if (tecla in TECLAS) saltar(TECLAS[tecla]);
      else if (tecla === "enter") siguienteNivel();
      else if (tecla === "r") nuevaPartida();
    }
    window.addEventListener("keydown", alApretar);
    return () => window.removeEventListener("keydown", alApretar);
  }, [saltar, siguienteNivel, nuevaPartida]);

  if (error) {
    return (
      <main className="centrado">
        <p>No se pudo conectar con el backend: {error}</p>
        <p className="tenue">¿Está corriendo <code>uvicorn api.main:app --reload</code> en backend/?</p>
      </main>
    );
  }
  if (!piramide || !estado) {
    return <main className="centrado"><p className="tenue">Conectando…</p></main>;
  }

  let mensaje: string | null = null;
  if (estado.game_over) mensaje = "GAME OVER · R para reiniciar";
  else if (estado.nivel_completo) {
    mensaje = estado.ultimo_nivel
      ? "¡Ganaste todos los niveles! · R para reiniciar"
      : "¡Nivel completo! · ENTER para seguir";
  }

  return (
    <main className="juego">
      <div className="marcador" aria-label="Puntajes">
        <p aria-live="polite">Puntaje actual: <strong>{puntaje}</strong> pts</p>
        <p>Récord: <strong>{mejorPuntaje}</strong> pts</p>
        {errorPuntaje && <p className="error-puntaje" role="alert">{errorPuntaje}</p>}
      </div>
      <section className="tablero">
        <h1>Q*bert con autómatas</h1>
        <Piramide datos={piramide} estado={estado} ultimo={ultimo} ultimoSalto={ultimoSalto}
          coloresCongelados={coloresCongelados} vistaQbert={vistaQbert} />
        {mensaje && <p className="mensaje">{mensaje}</p>}
      </section>
      <Panel estado={estado} ultimo={ultimo} />
    </main>
  );
}
