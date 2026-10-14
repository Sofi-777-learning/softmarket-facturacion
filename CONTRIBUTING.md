# Guía de contribución

## 1. Modelo de ramas (Git Flow simplificado)
| Rama | Origen | Destino | Descripción |
|------|--------|---------|-------------|
| `main` | - | - | Código en producción. Cada merge lleva un tag `vX.Y.Z`. Protegida. |
| `develop` | `main` | - | Integración continua del trabajo. Protegida. |
| `feature/SM-<id>-<descripcion>` | `develop` | `develop` | Nueva funcionalidad o refactor. |
| `release/X.Y.Z` | `develop` | `main` y `develop` | Estabilización de una versión. Solo correcciones. |
| `hotfix/X.Y.Z-<descripcion>` | `main` | `main` y `develop` | Corrección urgente en producción. |

Nadie hace `push` directo a `main` ni a `develop`: todo entra por Pull Request.

## 2. Convención de commits (Conventional Commits 1.0.0)
    <tipo>(<alcance>): <descripción en imperativo, máx. 72 caracteres>

    [cuerpo opcional: qué y por qué]

    [Refs: SM-123]  /  [BREAKING CHANGE: ...]

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

## 3. Pull Requests y revisión
- PR pequeño (idealmente < 400 líneas), con la plantilla completa.
- CI en verde (lint, formato, tipos, pruebas, cobertura >= 80 %).
- Mínimo 1 aprobación (2 para `release/*` y `hotfix/*` hacia `main`). Prohibido aprobar el propio PR.
- Plazo de primera respuesta del revisor: 24 horas hábiles.
- Comentarios clasificados: `[bloqueante]`, `[sugerencia]`, `[nit]`, `[pregunta]`.

## 4. Conflictos
- Sincronizar la rama con `develop` al menos una vez al día: `git fetch && git rebase origin/develop`.
- Rebase solo en ramas propias; nunca reescribir historia de `main` o `develop`.
- Subir con `git push --force-with-lease` (nunca `--force`).
- Tras resolver, volver a ejecutar las pruebas antes de continuar el rebase.
