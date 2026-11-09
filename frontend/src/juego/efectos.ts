import catalogo from "virtual:catalogo-assets";

function elegir<T>(opciones: readonly T[]): T {
  if (opciones.length === 0) {
    throw new Error("No hay archivos disponibles para este efecto");
  }
  return opciones[Math.floor(Math.random() * opciones.length)];
}

export function gifColision(): string {
  return elegir(catalogo.gifsColision);
}

export function gifGameover(): { src: string; duracionMs: number } {
  return elegir(catalogo.gifsGameover);
}

export function reproducirEfecto(tipo: keyof typeof catalogo.audios): void {
  const audio = new Audio(elegir(catalogo.audios[tipo]));
  void audio.play().catch((error: unknown) => {
    console.warn(`No se pudo reproducir el audio de ${tipo}:`, error);
  });
}
