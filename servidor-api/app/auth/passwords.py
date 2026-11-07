"""Hash, verificación y política de contraseña."""

from werkzeug.security import check_password_hash, generate_password_hash

_MIN_LEN = 10
_MAX_LEN = 128
_DUMMY_HASH = generate_password_hash("timing-dummy-not-a-real-password")


def hash_password(password: str) -> str:
    """Genera el hash de una contraseña en texto."""
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Compara la contraseña con el hash guardado."""
    return check_password_hash(password_hash, password)


def verify_or_dummy(password_hash: str | None, password: str) -> bool:
    """Verifica el hash o ejecuta una comparación ficticia (timing)."""
    if password_hash is None:
        check_password_hash(_DUMMY_HASH, password)
        return False
    return check_password_hash(password_hash, password)


def password_policy_error(password: str, email: str) -> str | None:
    """Devuelve el mensaje de error de política, o None si es válida."""
    if len(password) < _MIN_LEN:
        return f"La contraseña debe tener al menos {_MIN_LEN} caracteres."
    if len(password) > _MAX_LEN:
        return f"La contraseña no puede superar {_MAX_LEN} caracteres."
    if password.lower() == email.lower():
        return "La contraseña no puede ser igual al correo."
    return None
