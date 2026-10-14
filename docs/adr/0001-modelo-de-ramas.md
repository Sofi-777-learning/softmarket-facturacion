# ADR 0001: Adoptar Git Flow simplificado

- Estado: Aceptado
- Contexto: SoftMarket entrega software a medida con versiones distintas por cliente,
  necesita trazabilidad de releases y correcciones urgentes sin detener el desarrollo.
- Decisión: usar `main`, `develop`, `feature/*`, `release/*` y `hotfix/*`, con Pull Requests
  obligatorios, Conventional Commits y versionado semántico.
- Alternativas consideradas: GitHub Flow (más simple, pero sin rama de estabilización) y
  trunk-based (exige madurez alta en pruebas y feature flags que hoy no existe).
- Consecuencias: más ramas que gestionar; se mitiga con ramas de vida corta y automatización en CI.
