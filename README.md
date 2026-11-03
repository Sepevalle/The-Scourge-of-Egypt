# The Scourge of Egypt

Juego de mesa digital para escritorio y navegador. La versión web funciona en
PC y móvil; en teléfonos se recomienda jugar en horizontal.

## Probarlo localmente

Con Python 3.12 y `pip`:

```bash
python -m pip install pygbag
python -m pygbag .
```

Abre <http://localhost:8000> y espera a que termine la carga.

## Publicarlo gratis en GitHub Pages

1. Sube el proyecto a un repositorio de GitHub, incluyendo
   `.github/workflows/deploy.yml`.
2. En el repositorio, ve a **Settings → Pages** y elige **GitHub Actions** como
   origen de publicación.
3. Sube los cambios a la rama `main` o `master`, o ejecuta manualmente el flujo
   **Deploy game to GitHub Pages** desde la pestaña **Actions**.
4. Cuando el flujo termine, GitHub Pages mostrará el enlace público del juego.

La compilación incluye Pygame CE y NumPy como dependencias del juego. En
navegadores, «Salir» vuelve al menú en vez de cerrar la página.
