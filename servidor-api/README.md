# servidor-api

Backend Flask del sistema. Administra la API, la base de datos PostgreSQL y, más adelante, trabajos de mejora. Delega la mejora de imágenes al paquete `motor-ia`.

Estado: Paso 3D — subida de imágenes y almacenamiento local intercambiable.

## Requisitos

- Python 3.10 o superior (comprobado con 3.14.4).
- Docker Desktop en ejecución.
- Variables en el `.env` de la raíz del proyecto.

## Base de datos

Desde la raíz del proyecto:

```text
docker compose up -d
docker compose ps
```

PostgreSQL escucha en `127.0.0.1:5433` (el puerto 5432 del host ya estaba ocupado).

## Instalar

Desde `servidor-api/`:

```text
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

## Migraciones

```text
.venv\Scripts\python -m flask --app wsgi db upgrade
.venv\Scripts\python -m flask --app wsgi db current
```

## Ejecutar el servidor

```text
.venv\Scripts\python wsgi.py
```

Salud: `http://127.0.0.1:5000/api/health`. Auth: ver `docs/API.md`.

## Crear administrador

Solo por consola (no hay ruta web):

```text
.venv\Scripts\python -m flask --app wsgi create-admin
```

Pide correo, nombre y contraseña (oculta, con confirmación). Falla si el correo ya existe.

## Tests

```text
.venv\Scripts\python -m pytest
```

Usan la base PostgreSQL `*_test` (no la de desarrollo). Docker debe estar levantado.
