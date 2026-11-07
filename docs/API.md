# API — Autenticación

Base: `http://127.0.0.1:5000`. Errores siempre JSON: `{"error": {"code": "...", "message": "..."}}` (opcional `fields` en validación). Nunca HTML.

## Sesiones (limitación)

La sesión va en cookie firmada (Flask-Login), duración 8 horas, sin "recordarme". **No hay revocación centralizada:** `logout` y `session.clear()` solo afectan al navegador que ejecuta la acción. Una cookie copiada antes sigue válida hasta que expire, salvo que la cuenta pase a `inactiva` (el cargador consulta el estado en cada solicitud y responde 401). Mejora futura (no implementada): `session_version` en usuarios o sesiones en servidor.

## CSRF

1. `GET /api/auth/csrf` → `{"csrf_token": "..."}`.
2. Enviar `X-CSRFToken` en `register`, `login`, `logout` y `change-password`.
3. El token vive en la sesión: tras **login** o **logout** (limpieza de sesión) el anterior deja de valer. El frontend **debe** volver a pedir `GET /api/auth/csrf` después de login y de logout.

Sin token válido: `400` / `csrf_failed`.

## Endpoints

### GET /api/auth/csrf

`200`: `{"csrf_token": "..."}`.

### POST /api/auth/register

Solo: `nombre`, `correo`, `contraseña`. Cualquier otro campo → `400` / `validation_error`.

| Código | code |
| --- | --- |
| 201 | usuario creado y sesión iniciada (`user` sin `password_hash`) |
| 400 | `validation_error` o `csrf_failed` |
| 409 | `email_taken` |
| 429 | `rate_limited` (+ `Retry-After` si aplica) |

### POST /api/auth/login

Solo: `correo`, `contraseña`.

| Código | code |
| --- | --- |
| 200 | sesión iniciada |
| 401 | `invalid_credentials` (`credenciales inválidas`) |
| 403 | `account_inactive` |
| 429 | `rate_limited` |

### POST /api/auth/logout

Requiere sesión. `200`: `{"ok": true}`. Sin sesión: `401` / `unauthorized`.

### GET /api/auth/me

`200`: `{"user": {...}}` sin `password_hash`. Sin sesión o cuenta inactiva: `401`.

### POST /api/auth/change-password

Solo: `contraseña_actual`, `contraseña_nueva`.

| Código | code |
| --- | --- |
| 200 | `{"ok": true}` |
| 400 | `validation_error`, `same_password` o `csrf_failed` |
| 401 | `unauthorized` |

## Imágenes (`/api/images`)

Exigen sesión. `POST /` exige CSRF (`X-CSRFToken`). Solo JPEG/PNG. Máximo `MAX_UPLOAD_MB` (por defecto **10 MB, provisional**). Límite de subidas: `UPLOAD_RATE_LIMIT` (20/min por usuario). El propietario y el espacio individual los fija el servidor.

### POST /api/images/

Multipart, único campo `file`. Campos extra → `400 validation_error`.

| Código | code |
| --- | --- |
| 201 | `{"image": {...}}` (metadatos; incluye `checksum_sha256`, `nombre_original`) |
| 400 | `validation_error` / `csrf_failed` |
| 401 | `unauthorized` |
| 413 | `payload_too_large` |
| 429 | `rate_limited` |
| 501 | `not_implemented` (p. ej. Dropbox) |

### GET /api/images/?page=1&per_page=20

Lista solo del usuario. `per_page` máximo 50. `200`: `{items, page, per_page, total}`.

### GET /api/images/<id>

Metadatos propios. Otro usuario o id inexistente → `404` (nunca 403).

### GET /api/images/<id>/file?download=1

Archivo propio. `Content-Type` del mime guardado; `X-Content-Type-Options: nosniff`. Sin `download`: `inline`; con `download=1`: `attachment`. Ajeno/inexistente → `404`.
