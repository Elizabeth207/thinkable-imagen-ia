# Decisiones

| Decisión | Estado | Fecha |
| --- | --- | --- |
| Estructura en 3 partes separadas (portal-web, servidor-api, motor-ia) | Aprobada | 2026-10-30 |
| motor-ia como paquete independiente fuera de servidor-api | Aprobada | 2026-10-30 |
| Primer proveedor de IA: Replicate (solo para prueba) | Aprobada | 2026-10-30 |
| Frontend: React o plantillas Flask | Pendiente | — |
| Almacenamiento: disco local primero, Dropbox después, detrás de una capa intercambiable | Aprobada | 2026-10-30 |
| Equipos e invitaciones (hasta terminar el flujo personal) | Pospuesto | — |
| Pertenencia a varios equipos | Pendiente | — |
| Límite de imágenes por usuario | Pendiente | — |
| Política de conservación | Pendiente | — |
| Proveedor de correo | Pendiente | — |
| Ficha de Replicate consultada (detalle abajo). Preset inicial del script: gfpgan | Verificada | 2026-10-30 |
| Backend: Flask + Flask-SQLAlchemy + Flask-Migrate | Aprobada | 2026-11-06 |
| Controlador PostgreSQL: psycopg 3.3.8 (psycopg[binary]) | Aprobada | 2026-11-06 |
| PostgreSQL en Docker: imagen `postgres:18` (estable reciente) | Aprobada | 2026-11-06 |
| Puerto host de PostgreSQL: `127.0.0.1:5433` (5432 ocupado por postgres nativo) | Aprobada | 2026-11-06 |
| Python del backend en esta máquina: 3.14.4 (paquetes comprobados) | Verificada | 2026-11-06 |
| Estados/roles: VARCHAR + CHECK (sin ENUM PostgreSQL) | Aprobada | 2026-11-06 |
| FK compuesta (espacio_id, tipo_espacio) para coherencia de tipo | Aprobada | 2026-11-06 |
| Un solo equipo grupal por usuario (índice único parcial) | Aprobada | 2026-11-06 |
| Un solo espacio individual por usuario (índice único parcial) | Aprobada | 2026-11-06 |
| Borrado: RESTRICT en usuarios/archivos/procesamientos; CASCADE solo membresías al borrar espacio | Aprobada | 2026-11-06 |
| Almacenamiento de archivos: `local` \| `dropbox` en columna | Aprobada | 2026-11-06 |
| Migraciones Alembic: excepción a la regla de 100 líneas si hace falta; preferir dividir | Aprobada | 2026-11-06 |
| rol_global incluye `admin_general`; procesamientos guardan modelo y proveedor_job_id | Aprobada | 2026-11-06 |
| Sesión por cookie firmada (Flask-Login), no JWT | Aprobada | 2026-11-06 |
| CSRF con Flask-WTF; token en `X-CSRFToken` | Aprobada | 2026-11-06 |
| Límite de intentos Flask-Limiter en memoria (por proceso; Redis si hace falta) | Aprobada | 2026-11-06 |
| Hash de contraseñas: werkzeug.security | Aprobada | 2026-11-06 |
| Política de contraseña: 10–128 caracteres, distinta del correo; sin complejidad forzada | Aprobada | 2026-11-06 |
| Sin CORS: el frontend usará proxy del servidor de desarrollo (mismo origen) | Aprobada | 2026-11-06 |
| Administradores solo con `flask create-admin` (sin ruta web) | Aprobada | 2026-11-06 |
| Sesiones firmadas en cookie: sin revocación centralizada; logout/clear solo afectan ese navegador | Aprobada | 2026-11-06 |
| Cookie copiada sigue válida hasta expirar (8 h), salvo cuenta inactiva | Aprobada | 2026-11-06 |
| Mejora futura: `session_version` en usuarios o sesiones en servidor (no implementado) | Pendiente | 2026-11-06 |
| CSRF obligatorio en register/login/logout/change-password; renovar tras login/logout | Aprobada | 2026-11-06 |
| Cambio de contraseña: código `same_password` si la nueva es idéntica a la actual | Aprobada | 2026-11-06 |
| Pendiente: recuperación de contraseña, login con Google, edición de perfil | Pendiente | 2026-11-06 |
| Subida: solo JPEG/PNG (WEBP y otros pospuestos) | Aprobada | 2026-11-06 |
| MAX_UPLOAD_MB=10 provisional, configurable; pendiente confirmar con la empresa | Aprobada | 2026-11-06 |
| Almacenamiento local detrás de interfaz `StorageBackend`; Dropbox pendiente | Aprobada | 2026-11-06 |
| Claves: `usuarios/<user_id>/originales/<archivo_id>.<ext>` (sin nombre de cliente) | Aprobada | 2026-11-06 |
| Acceso ajeno a imagen: 404 (no 403) para no filtrar ids | Aprobada | 2026-11-06 |
| EXIF del original se conserva; evaluar quitarlo al enviar al proveedor en 3E | Pendiente | 2026-11-06 |
| Validación reutiliza `ALLOWED_FORMATS`/`ImageInfo` de motor-ia; límites de producto en servidor-api | Aprobada | 2026-11-06 |
| Driver Dropbox | Pendiente | 2026-11-06 |

## Verificación de Replicate (2026-10-30)

Fuentes leídas: documentación HTTP de predicciones, guía Python del cliente 1.0.7, código de `replicate-python` 1.0.7 (`Client`, `predictions.create`, `predictions.get`), páginas de modelo, precios, límites, retención de datos de predicciones y la política de privacidad (actualizada el 1 de abril de 2026).

### Cliente y API

- Paquete estable en PyPI: `replicate` 1.0.7. Python requerido por ese paquete: 3.8 o superior.
- Autenticación: `Authorization: Bearer <token>`. El constructor documentado es `Client(api_token=..., base_url=...)`. La base por defecto en el cliente es `https://api.replicate.com`.
- Crear trabajo: `POST /v1/predictions`, en el cliente `predictions.create(version=..., input=..., wait=False)`. `wait=False` no envía la cabecera `Prefer: wait`. El identificador vuelve en `prediction.id`.
- Consultar: `GET /v1/predictions/{prediction_id}`, en el cliente `predictions.get(id)`.
- Estados documentados: `starting`, `processing`, `succeeded`, `failed`, `canceled`. Este paquete los traduce a `pending`, `processing`, `completed`, `failed` y `failed`.
- Un archivo local se pasa como objeto de archivo en `input`. La guía Python lo documenta. El documento de archivos de entrada dice que la subida local funciona hasta 100 MB.
- La salida de archivo, en la API, es una URI `https`. Para descargarla hay que enviar `Authorization`. El cliente también puede devolver un objeto con `read()`.
- El cliente reintenta GET ante 429, 503 y 504. No reintenta el POST de creación. Este paquete no vuelve a crear un trabajo fallido o vencido.
- Límites publicados: 600 creaciones de predicción por minuto y 3000 peticiones por minuto al resto. Un exceso responde 429. Con crédito bajo los límites se endurecen.
- Intervalo de sondeo recomendado por la API: no confirmado. El cliente usa 0.5 s (`REPLICATE_POLL_INTERVAL`) dentro de `prediction.wait()`. El paquete usa 0.5 s por defecto y no usa `wait()`, para poder cortar a los 180 s. Tiempo máximo de una predicción: no confirmado.

### Modelos comprobados

`tencentarc/gfpgan`, versión latest `0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c`. Entradas: `img` (obligatoria), `version` (opcional, por defecto `v1.4`; `v1.3` es mejor calidad y `v1.4` más detalle e identidad), `scale` (opcional, por defecto 2). Salida: URI. Ejemplos oficiales en JPG y PNG; la salida de ejemplo es PNG. Costo aproximado publicado en la ficha: 0,0035 USD por ejecución, en Nvidia L40S, suele terminar en unos 4 s. Varía según la entrada. Formatos admitidos y tamaño máximo del modelo: no confirmado. El script solo deja pasar JPEG y PNG, que son los de los ejemplos.

`xinntao/realesrgan`, versión latest `1b976a4d456ed9e4d1a846597b7614e79eadad3032e9124fa63859db0fd59b56`. Entradas: `img` (obligatoria), `version` (por defecto `General - v3`), `scale` (por defecto 2), `face_enhance` (por defecto false; si es true usa GFPGAN y no sirve para anime), `tile` (por defecto 0). Salida: URI. Costo aproximado publicado: 0,0023 USD por ejecución, en Nvidia T4, suele tardar unos 11 s. Varía según la entrada. Resolución máxima: no confirmado.

`nightmareai/real-esrgan` existe. El readme recomienda como máximo 1440p de entrada. La lista de versiones marca el prefijo `f121d640` como latest. Entradas vistas en una ficha de versión: `image`, `scale` (por defecto 4, máximo 10) y `face_enhance` (por defecto false). Salida: URI. El costo de esa ficha no quedó en el texto leído: no confirmado. No está conectado en el código.

Precios de hardware en la página de pricing, como referencia y no como cotización de una corrida: L40S 0,000975 USD/s; T4 0,000225 USD/s.

### Privacidad

Para predicciones creadas por API, entradas, salidas, archivos de salida y logs se borran a la hora, por defecto. Hay que guardar una copia. Los archivos de salida se sirven desde `replicate.delivery`. Si esas imágenes se usan para entrenar modelos de Replicate: no confirmado. La política de privacidad dice que Replicate actúa como encargado del tratamiento y conserva datos de clientes el tiempo necesario para el servicio, obligaciones legales y prevención de abuso.

### Elección del script

La primera prueba usa el preset `gfpgan`, porque la ficha lo describe como restauración facial de fotos antiguas o caras generadas por IA, y pasa los valores por defecto documentados (`v1.4`, `scale` 2). `realesrgan` queda disponible con `--preset realesrgan` y sus valores por defecto, incluido `face_enhance` en false. Cambiar el preset antes de la prueba de pago no requiere tocar el código.
