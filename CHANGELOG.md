# Changelog
Formato basado en [Keep a Changelog](https://keepachangelog.com) y [SemVer](https://semver.org).

## [Sin publicar]
### Agregado
- Documentación del flujo de contribución validada por el equipo (SM-40).
- Aplicación web de facturación desplegable en Cloud Run (SM-42).
- Adaptadores de Google Cloud: RepositorioFirestore y NotificadorPubSub (SM-42).
- Clave de acceso leída desde Secret Manager, sin credenciales en el código (SM-42).

## [1.0.1]
### Corregido
- IVA redondeado a 2 decimales (hotfix SM-31).

## [1.0.0]
### Agregado
- Módulo de facturación refactorizado aplicando SOLID (Strategy, Repository, DI).
- Descuento por volumen.
- Pipeline de CI y guía de contribución.
