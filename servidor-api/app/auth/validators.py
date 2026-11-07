"""Validación de entradas de autenticación."""

from email_validator import EmailNotValidError, validate_email

from app.auth.passwords import password_policy_error

_REGISTER_FIELDS = frozenset({"nombre", "correo", "contraseña"})
_LOGIN_FIELDS = frozenset({"correo", "contraseña"})
_PASSWORD_FIELDS = frozenset({"contraseña_actual", "contraseña_nueva"})


def validate_register(data: dict) -> tuple[dict | None, dict[str, str] | None]:
    """Valida el registro. Rechaza campos no permitidos."""
    extra = _extra_fields(data, _REGISTER_FIELDS)
    if extra:
        return None, extra
    fields: dict[str, str] = {}
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        fields["nombre"] = "El nombre es obligatorio."
    elif len(nombre) > 120:
        fields["nombre"] = "El nombre no puede superar 120 caracteres."
    correo, correo_err = _normalize_email(data.get("correo"))
    if correo_err:
        fields["correo"] = correo_err
    password = data.get("contraseña") or ""
    policy = password_policy_error(password, correo or "")
    if policy:
        fields["contraseña"] = policy
    if fields:
        return None, fields
    return {"nombre": nombre, "correo": correo, "contraseña": password}, None


def validate_login(data: dict) -> tuple[dict | None, dict[str, str] | None]:
    """Valida correo y contraseña de inicio de sesión."""
    extra = _extra_fields(data, _LOGIN_FIELDS)
    if extra:
        return None, extra
    fields: dict[str, str] = {}
    correo, correo_err = _normalize_email(data.get("correo"))
    if correo_err:
        fields["correo"] = correo_err
    password = data.get("contraseña") or ""
    if not password:
        fields["contraseña"] = "La contraseña es obligatoria."
    if fields:
        return None, fields
    return {"correo": correo, "contraseña": password}, None


def validate_change_password(
    data: dict, email: str
) -> tuple[dict | None, dict[str, str] | None]:
    """Valida el cambio de contraseña."""
    extra = _extra_fields(data, _PASSWORD_FIELDS)
    if extra:
        return None, extra
    fields: dict[str, str] = {}
    current = data.get("contraseña_actual") or ""
    new = data.get("contraseña_nueva") or ""
    if not current:
        fields["contraseña_actual"] = "La contraseña actual es obligatoria."
    policy = password_policy_error(new, email)
    if policy:
        fields["contraseña_nueva"] = policy
    if fields:
        return None, fields
    return {"contraseña_actual": current, "contraseña_nueva": new}, None


def _extra_fields(data: dict, allowed: frozenset[str]) -> dict[str, str] | None:
    if not isinstance(data, dict):
        return {"_": "El cuerpo debe ser un objeto JSON."}
    unexpected = sorted(set(data) - allowed)
    if not unexpected:
        return None
    return {name: "Campo no permitido." for name in unexpected}


def _normalize_email(raw: object) -> tuple[str | None, str | None]:
    text = (str(raw) if raw is not None else "").strip().lower()
    if not text:
        return None, "El correo es obligatorio."
    try:
        result = validate_email(text, check_deliverability=False)
    except EmailNotValidError:
        return None, "El formato del correo no es válido."
    return result.normalized, None
