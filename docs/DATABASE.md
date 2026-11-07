# Esquema de base de datos

PostgreSQL 18. Claves primarias UUID (`uuid4` en la aplicación). Fechas en `timestamptz` (UTC). Estados y roles como `VARCHAR` con `CHECK` (sin ENUM de PostgreSQL).

## Política de borrado

- Usuarios, archivos y procesamientos: `ON DELETE RESTRICT` (no se borran en cascada).
- Los usuarios se desactivan con `estado = 'inactivo'`.
- Única cascada permitida: al eliminar un `espacios_trabajo`, se eliminan sus `membresias_espacio`.
- `auditoria.usuario_id`: `ON DELETE SET NULL`.

## Tablas

### usuarios

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | |
| nombre | VARCHAR(120) | |
| correo | VARCHAR(180) | Índice único sobre `lower(correo)` |
| password_hash | TEXT | |
| estado | VARCHAR | `activo` \| `inactivo` |
| rol_global | VARCHAR | `usuario` \| `admin_general` (default `usuario`) |
| creado_en, actualizado_en | timestamptz | |

### espacios_trabajo

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | UNIQUE `(id, tipo)` para FK compuesta |
| propietario_id | UUID FK → usuarios | RESTRICT |
| nombre | VARCHAR(120) | |
| tipo | VARCHAR | `individual` \| `grupal` |
| estado | VARCHAR | `activo` \| `inactivo` |
| creado_en | timestamptz | |

Índice único parcial: un solo espacio `individual` por `propietario_id`.

### membresias_espacio

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | |
| usuario_id | UUID FK → usuarios | RESTRICT |
| espacio_id, tipo_espacio | FK compuesta → espacios_trabajo(id, tipo) | CASCADE |
| rol | VARCHAR | `propietario` \| `admin` \| `participante` |
| unido_en | timestamptz | |

UNIQUE `(usuario_id, espacio_id)`. Índice único parcial: un solo equipo `grupal` por usuario.

### archivos_multimedia

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | |
| propietario_id | UUID FK → usuarios | RESTRICT |
| espacio_id | UUID FK → espacios_trabajo | RESTRICT |
| tipo | VARCHAR | `original` \| `resultado` |
| almacenamiento | VARCHAR | `local` \| `dropbox` |
| referencia_externa | VARCHAR(255) | nullable (id Dropbox) |
| ruta_logica | TEXT | |
| mime_type | VARCHAR(100) | |
| tamano_bytes | BIGINT | `> 0` |
| ancho, alto | INTEGER | nullable |
| checksum_sha256 | VARCHAR(64) | |
| nombre_original | VARCHAR(255) | nullable; solo para mostrar (sanitizado; nunca en rutas) |
| creado_en | timestamptz | |

### proveedores_ia

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | |
| nombre | VARCHAR(120) | único |
| estado | VARCHAR | `activo` \| `inactivo` |
| creado_en | timestamptz | |

### procesamientos_ia

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | |
| usuario_id | UUID FK → usuarios | RESTRICT |
| espacio_id | UUID FK → espacios_trabajo | RESTRICT |
| proveedor_id | UUID FK → proveedores_ia | nullable, RESTRICT |
| archivo_original_id | UUID FK → archivos_multimedia | RESTRICT |
| archivo_resultado_id | UUID FK → archivos_multimedia | nullable, RESTRICT |
| estado | VARCHAR | `pendiente` \| `en_proceso` \| `completado` \| `fallido` |
| modelo, version_modelo | VARCHAR | nullable |
| parametros | JSONB | nullable |
| proveedor_job_id | VARCHAR(120) | nullable |
| solicitado_en | timestamptz | |
| finalizado_en | timestamptz | nullable |
| mensaje_error | TEXT | nullable |

CHECK: si `estado = 'completado'`, `archivo_resultado_id` no nulo. UNIQUE `(proveedor_id, proveedor_job_id)`. Índices `(usuario_id, solicitado_en)` y `(espacio_id, estado)`.

### auditoria

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | UUID PK | |
| usuario_id | UUID FK → usuarios | nullable, SET NULL |
| accion | VARCHAR(80) | |
| tipo_objetivo | VARCHAR(60) | |
| objetivo_id | UUID | nullable |
| fecha | timestamptz | índice |

## Aún no creadas

`invitaciones_equipo`, `trabajos_compartidos` y tablas de cuotas (pasos posteriores).
