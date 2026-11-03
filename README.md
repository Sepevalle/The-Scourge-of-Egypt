# The Scourge of Egypt

Juego de mesa digital hecho con Pygame. Se puede ejecutar como aplicación de
escritorio y jugar desde el navegador en PC o móvil. En teléfonos se recomienda
jugar en horizontal.

## Cómo funciona la versión web

El juego no se reescribe en JavaScript: [Pygbag](https://pypi.org/project/pygbag/)
empaqueta el proyecto Pygame para ejecutarlo en el navegador mediante Python y
WebAssembly. El archivo [main.py](./main.py) es tanto el punto de entrada de
escritorio como el de la compilación web.

El flujo de publicación está en
[.github/workflows/deploy.yml](./.github/workflows/deploy.yml):

1. Se ejecuta automáticamente al subir cambios a `main` o `master`. También se
   puede iniciar manualmente desde **GitHub → Actions → Deploy game to GitHub
   Pages → Run workflow**.
2. GitHub Actions prepara Python 3.12, instala Pygbag y construye el juego con
   `python -m pygbag --build --title "The Scourge of Egypt" main.py`.
3. Pygbag genera el sitio estático en `build/web`. El flujo toma el único
   archivo `.tar.gz` generado, le añade los primeros 12 caracteres del SHA del
   commit y actualiza la referencia en `index.html`. Por ejemplo:
   `the.scourge.of.egypt-bbc1093e9c4c.tar.gz`.
4. Se publica `build/web` como artefacto de GitHub Pages y `actions/deploy-pages`
   lo sirve en la URL del proyecto.

El nombre versionado del archivo es importante: los navegadores y la CDN pueden
conservar archivos estáticos en caché. Si se reemplazara el archivo con el mismo
nombre, el HTML nuevo podría cargar el juego antiguo durante varios minutos.
No elimines el paso **Version game archive to avoid stale browser caches** ni
hagas que `index.html` siga apuntando al nombre fijo del archivo.

## Requisitos para cambios de código

- Mantén `main.py` en la raíz y conserva sus dependencias PEP 723
  (`pygame-ce` y `numpy`). Las dependencias nuevas necesarias en navegador
  deben añadirse ahí y deben estar disponibles para Pygbag/WebAssembly.
- El bucle principal debe seguir siendo asíncrono (`async def main`) y ejecutar
  `await asyncio.sleep(0)` en cada iteración. Esto devuelve el control al
  navegador; sin ello la página puede bloquearse.
- Importa al principio de `main.py` los paquetes externos que necesite el
  juego. El cargador web los prepara a partir de las dependencias declaradas.
- Mantén los recursos necesarios dentro del proyecto y evita dependencias de
  rutas locales, ejecutables del sistema o APIs exclusivas de escritorio.
  Comprueba en particular audio, archivos, entrada táctil y cualquier
  funcionalidad que introduzcas.
- Conserva la salida del juego compatible con navegador: «Salir» vuelve al
  menú en vez de cerrar la pestaña.
- No subas `build/` como fuente de verdad. GitHub Actions lo genera de nuevo en
  cada despliegue; los artefactos compilados son temporales y están ignorados
  por Git.

## GitHub Pages: configuración inicial

En el repositorio, abre **Settings → Pages** y configura **Build and
deployment → Source: GitHub Actions**. El workflow ya declara los permisos
`pages: write` e `id-token: write`; no necesita una rama `gh-pages` ni un
despliegue manual de archivos. La dirección del proyecto es
<https://sepevalle.github.io/The-Scourge-of-Egypt/>.

Si un despliegue falla en **Configure GitHub Pages** con `Not Found`, verifica
que Pages esté habilitado y que su origen sea **GitHub Actions**. Si Actions
indica que terminó bien pero el navegador enseña la versión anterior, confirma
que el flujo incluye el paso de versionado del archivo `.tar.gz` y vuelve a
cargar la página.

## Probar localmente

Con Python 3.12 y `pip`:

```bash
python -m pip install pygbag
python -m pygbag .
```

Abre <http://localhost:8000> y espera a que termine la carga. Para verificar la
lógica y la interfaz desde Python de escritorio:

```bash
python -m unittest discover -s tests -v
```
