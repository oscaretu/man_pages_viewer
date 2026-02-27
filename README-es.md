# manls

Un visor de páginas de manual estilo Dash para terminal con navegación por secciones.

<img src="manls/images/man_pages_viewer_01.png" width="800" align="center" />

## Características

- **Navegación por Secciones**: Saltar rápidamente a cualquier sección desde la barra lateral
- **Diseño de Dos Paneles**: Secciones a la izquierda, contenido a la derecha
- **Soporte de Scroll**: Desplazamiento fluido en ambos paneles
- **Búsqueda**: Encontrar páginas de manual con la opción `-k`
- **Navegación con Teclado**: Control total mediante teclado


## Instalación

```bash
cd manls
pip install -e .
```

O ejecutar directamente:

```bash
./manls <comando>
```

## Uso

```bash
# Ver una página de manual
manls ls
manls bash

# Ejecutar el comando sin una sección específica
manls passwd

# Ver passwd sección 5 (ficheros) - observa la diferencia sin número de sección
manls 5 passwd

# Buscar páginas de manual
manls -k ssh
```

## Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| `Tab` | Cambiar entre paneles |
| `↑` / `↓` | Navegar secciones (panel lateral) |
| `j` / `k` | Navegar secciones (panel lateral) / Desplazar contenido (panel de contenido) |
| `q` | Salir |

## Requisitos

- Python 3.8+
- [Textual](https://textual.textualize.io/) (framework TUI)
- Páginas de manual de Linux (`man-db`)

## Ver También

Este proyecto está inspirado en el artículo de Julia Evans [Notes on clarifying man pages](https://jvns.ca/blog/2026/02/18/man-pages/).

- [English](./README.md)

## Licencia

MIT
