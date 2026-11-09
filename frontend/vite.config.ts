import { readFileSync, readdirSync } from 'node:fs'
import { dirname, relative, resolve, sep } from 'node:path'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin, type ViteDevServer } from 'vite'

const ID_CATALOGO = 'virtual:catalogo-assets'
const ID_CATALOGO_RESUELTO = `\0${ID_CATALOGO}`

function duracionGifMs(archivo: string): number {
  const datos = readFileSync(archivo)
  if (datos.toString('ascii', 0, 3) !== 'GIF' || datos.length < 13) {
    throw new Error(`El archivo no es un GIF válido: ${archivo}`)
  }

  const saltarSubbloques = (desde: number) => {
    let posicion = desde
    while (posicion < datos.length) {
      const tamano = datos[posicion++]
      if (tamano === 0) return posicion
      posicion += tamano
    }
    throw new Error(`GIF truncado en ${archivo}`)
  }

  let posicion = 13
  const packed = datos[10]
  if (packed & 0x80) posicion += 3 * (1 << ((packed & 0x07) + 1))

  let demoraSiguienteCuadro = 0
  let duracionTotal = 0
  while (posicion < datos.length) {
    const bloque = datos[posicion++]
    if (bloque === 0x3b) break

    if (bloque === 0x21) {
      const etiqueta = datos[posicion++]
      if (etiqueta === 0xf9) {
        const tamano = datos[posicion++]
        if (tamano !== 4 || posicion + tamano >= datos.length) {
          throw new Error(`Bloque de control GIF inválido en ${archivo}`)
        }
        demoraSiguienteCuadro = datos.readUInt16LE(posicion + 1) * 10
        posicion += tamano
        if (datos[posicion++] !== 0) {
          throw new Error(`Bloque de control GIF sin terminador en ${archivo}`)
        }
      } else {
        posicion = saltarSubbloques(posicion)
      }
      continue
    }

    if (bloque === 0x2c) {
      if (posicion + 9 > datos.length) throw new Error(`GIF truncado en ${archivo}`)
      const imagenPacked = datos[posicion + 8]
      posicion += 9
      if (imagenPacked & 0x80) posicion += 3 * (1 << ((imagenPacked & 0x07) + 1))
      posicion += 1
      posicion = saltarSubbloques(posicion)
      duracionTotal += Math.max(demoraSiguienteCuadro, 10)
      demoraSiguienteCuadro = 0
      continue
    }

    throw new Error(`Bloque GIF desconocido en ${archivo}`)
  }

  if (duracionTotal === 0) throw new Error(`El GIF no contiene cuadros: ${archivo}`)
  return duracionTotal
}

function catalogoAssets(): Plugin {
  const raizPublica = resolve(import.meta.dirname, 'public')
  const directorios = {
    gifs: resolve(raizPublica, 'assets'),
    audios: resolve(raizPublica, 'audios'),
  }
  let servidor: ViteDevServer | undefined

  const listar = (directorio: string, prefijo: string, extension: string) => {
    try {
      return readdirSync(directorio)
        .filter((nombre) => nombre.startsWith(prefijo) && nombre.endsWith(extension))
        .sort()
        .map((nombre) => `/${relative(raizPublica, resolve(directorio, nombre)).split(sep).join('/')}`)
    } catch (error) {
      throw new Error(`No se pudieron leer los assets de ${directorio}`, { cause: error })
    }
  }

  const listarGifsGameover = () => {
    try {
      return readdirSync(directorios.gifs)
        .filter((nombre) => nombre.startsWith('gameover') && nombre.endsWith('.gif'))
        .sort()
        .map((nombre) => {
          const archivo = resolve(directorios.gifs, nombre)
          return {
            src: `/${relative(raizPublica, archivo).split(sep).join('/')}`,
            duracionMs: duracionGifMs(archivo),
          }
        })
    } catch (error) {
      throw new Error(`No se pudieron leer los GIF de ${directorios.gifs}`, { cause: error })
    }
  }

  const actualizarCatalogo = (archivo: string) => {
    if (!servidor || !Object.values(directorios).includes(dirname(archivo))) return
    const modulo = servidor.moduleGraph.getModuleById(ID_CATALOGO_RESUELTO)
    if (modulo) servidor.moduleGraph.invalidateModule(modulo)
    servidor.ws.send({ type: 'full-reload' })
  }

  return {
    name: 'catalogo-assets-juego',
    resolveId(id) {
      return id === ID_CATALOGO ? ID_CATALOGO_RESUELTO : undefined
    },
    load(id) {
      if (id !== ID_CATALOGO_RESUELTO) return undefined
      const catalogo = {
        gifsColision: listar(directorios.gifs, 'colision', '.gif'),
        gifsGameover: listarGifsGameover(),
        audios: {
          arriba: listar(directorios.audios, 'arriba', '.mp3'),
          abajo: listar(directorios.audios, 'abajo', '.mp3'),
          caida: listar(directorios.audios, 'caida', '.mp3'),
          colision: listar(directorios.audios, 'colision', '.mp3'),
          gameover: listar(directorios.audios, 'gameover', '.mp3'),
        },
      }
      return `export default ${JSON.stringify(catalogo)}`
    },
    configureServer(devServer) {
      servidor = devServer
      devServer.watcher.add(Object.values(directorios))
      devServer.watcher.on('add', actualizarCatalogo)
      devServer.watcher.on('unlink', actualizarCatalogo)
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), catalogoAssets()],
  server: {
    // En desarrollo, /api/... va al backend (uvicorn en el puerto 8000).
    // Así el frontend usa rutas relativas y no hace falta configurar CORS.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
