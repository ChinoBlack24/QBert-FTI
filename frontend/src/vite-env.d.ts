declare module "virtual:catalogo-assets" {
  interface CatalogoAssets {
    gifsColision: string[];
    gifsGameover: { src: string; duracionMs: number }[];
    audios: {
      arriba: string[];
      abajo: string[];
      caida: string[];
      colision: string[];
      gameover: string[];
    };
  }

  const catalogo: CatalogoAssets;
  export default catalogo;
}
