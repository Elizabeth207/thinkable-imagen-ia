# Plan de desarrollo

No se marca un paso como hecho sin una comprobación.

## Paso 1 — Estructura

- [x] Carpetas, documentación inicial, `.gitignore` y `git init`. Comprobado el 2026-10-30 con `tree /F` y `git status`.

## Paso 2 — motor-ia

- [x] Documentación oficial de Replicate leída y resumida en `docs/DECISIONS.md` (2026-10-30).
- [x] Paquete `motor_ia`, script y pruebas creados dentro de `motor-ia/`.
- [x] `pytest`: 17 pruebas pasaron. Los tests del proveedor usan mocks y no llaman a la red.
- [x] Ningún archivo `.py` de `motor-ia/` supera 100 líneas. Comprobado contando líneas.
- [ ] Prueba real con una imagen. No ejecutada: faltan la clave en `.env` y las imágenes en `samples/`, y no hay autorización para el cobro.
- [ ] Resto de imágenes de `samples/`. Espera autorización aparte.

## Paso 3 — servidor-api

### 3A — Base Flask, PostgreSQL en Docker, migraciones y salud

- [x] Docker disponible; PostgreSQL 18 en Compose con puerto host `5433` (5432 ocupado). Comprobado healthy con `docker compose ps`.
- [x] App Flask mínima, `GET /api/health`, errores JSON uniformes.
- [x] Flask-Migrate inicializado sin revisiones (aún no hay modelos).
- [x] Tests de salud pasan; verificación manual 200/503 con Docker up/stop.
- [x] Ningún `.py` de `servidor-api/` supera 100 líneas.

### 3B — Modelos de datos y primeras migraciones

- [x] Modelos: usuarios, espacios, membresías, archivos, proveedores, procesamientos, auditoría.
- [x] Tres migraciones (usuarios/espacios; archivos; proveedores/procesamientos/auditoría). `flask db upgrade` / `downgrade base` comprobados.
- [x] Pruebas de restricciones en PostgreSQL (`*_test`): 18 passed.
- [x] Persistencia tras `docker compose down` (sin `-v`) y `up -d`.
- [x] `docs/DATABASE.md` creado.

### 3C — Registro, login, sesión segura y roles

- [x] Endpoints `/api/auth/*`: csrf, register, login, logout, me, change-password.
- [x] Flask-Login, CSRF, Limiter, cabeceras de seguridad, `flask create-admin`.
- [x] Ajustes: lista blanca, `same_password`, CSRF por acción + ciclo de tokens, estado activo en cada request, errores JSON (401–500/429), sin secretos en logs/auditoría, limitación de sesiones documentada.
- [x] Pruebas PostgreSQL: 49 passed.
- [x] Demo HTTP contra `*_test` (crear/limpiar por id); `docs/API.md` actualizado.

### 3D — Almacenamiento (disco local) y subida de imágenes

- [x] Capa `StorageBackend` + `LocalStorage`; factory; Dropbox → no implementado.
- [x] Endpoints `/api/images` (POST/GET lista/GET meta/GET file) con CSRF, dueño y validación Pillow.
- [x] Migración `nombre_original`; tests PostgreSQL + storage temporal.
- [ ] Driver de Dropbox (pendiente).

### 3E — Trabajos de mejora con motor-ia (segundo plano, estados, cuota)

- [ ] Pendiente.

### 3F — Historial y descarga con permisos

- [ ] Pendiente.

## Paso 4 — portal-web

- [ ] Sin empezar.

## Después

- [ ] Equipos, invitaciones y trabajos compartidos.
