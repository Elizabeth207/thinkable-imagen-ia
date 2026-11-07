# motor-ia

Paquete Python que usa `servidor-api` para mejorar imágenes con un proveedor externo. No es un microservicio ni un servidor.

Estado: el paquete y las pruebas automáticas están escritos. La prueba con imágenes reales no se ha ejecutado.

## Requisitos

Python 3.10 o superior. En esta máquina hay Python 3.14.4. El cliente oficial `replicate` 1.0.7 pide Python 3.8 o superior y se instaló bien en 3.14.4, igual que Pillow 13.0.0, python-dotenv 1.2.4 y pytest 9.2.0.

## Instalar

Desde `motor-ia/`:

```text
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

El entorno queda en `motor-ia/.venv` y no se sube a Git.

## Configurar

Crea un archivo `.env` en la raíz del proyecto, no dentro de `motor-ia/`. No lo subas a Git.

```text
IMAGE_PROVIDER_API_KEY=
```

Ahí va el token de Replicate. El paquete lo lee y se lo pasa al cliente oficial. No lo escribas en el código.

Opcionales:

- `IMAGE_PROVIDER_BASE_URL`: solo si quieres otro host. Si está vacía, el cliente usa `https://api.replicate.com`.
- `IMAGE_PROVIDER_PRESET`: `gfpgan` (valor por defecto) o `realesrgan`.
- `IMAGE_PROVIDER_POLL_INTERVAL_SECONDS`: por defecto `0.5`, el mismo valor que usa el cliente oficial al esperar.
- `IMAGE_PROVIDER_MAX_WAIT_SECONDS`: por defecto `180`. Si se agota, el trabajo no se vuelve a enviar.

Las imágenes de prueba van en `motor-ia/samples/`. El script no las genera ni las descarga. Esa carpeta no se sube a Git.

## Tests

Desde `motor-ia/`:

```text
.venv\Scripts\python -m pytest
```

No llaman a Replicate y no cobran.

## Prueba real

Desde `motor-ia/`, y solo cuando la clave y las imágenes ya estén:

```text
.venv\Scripts\python scripts\run_quality_test.py --max-images 1
```

Por defecto procesa como máximo 3 imágenes. Si pides más de 3, el script avisa que Replicate cobra por ejecución y espera que escribas `SI`. El resultado queda en `out/resultados.csv`. Si `samples/` está vacío, termina sin llamar al proveedor.

El preset inicial es `gfpgan` (restauración facial). Para superresolución:

```text
.venv\Scripts\python scripts\run_quality_test.py --max-images 1 --preset realesrgan
```
