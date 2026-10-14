# SoftMarket - Módulo de Facturación

Repositorio de referencia con la propuesta de buenas prácticas de ingeniería de software.

- `legacy/`  : código original (God class), solo como referencia del "antes".
- `src/facturacion/` : módulo refactorizado aplicando SOLID.
- `tests/`   : pruebas unitarias (pytest).
- `docs/adr/`: decisiones de arquitectura.

## Cómo ejecutar
    python -m venv .venv && source .venv/bin/activate
    pip install pytest pytest-cov ruff black mypy
    pytest --cov=facturacion

## Flujo de trabajo
Ver `CONTRIBUTING.md` (modelo de ramas, commits, revisión de código).
