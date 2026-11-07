"""Fábrica de la aplicación Flask."""

from flask import Flask

from app.auth.cli import register_cli
from app.auth.routes import auth_bp
from app.common.errors import register_error_handlers
from app.common.responses import error_response
from app.common.security_headers import register_security_headers
from app.config import get_config, load_env_file
from app.extensions import csrf, db, limiter, login_manager, migrate
from app.health.routes import health_bp
from app.media.routes import media_bp
from app.users.repository import find_by_id


def create_app(config_name: str | None = None) -> Flask:
    """Crea la app, carga config, extensiones y blueprints."""
    load_env_file()
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    _init_extensions(app)
    _register_login_handlers()
    register_error_handlers(app)
    register_security_headers(app)
    register_cli(app)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(media_bp)
    if app.testing:
        _register_testing_routes(app)
    return app


def _register_testing_routes(app: Flask) -> None:
    """Rutas solo para pruebas de roles (no existen en desarrollo)."""
    from app.auth.permissions import role_required
    from app.common.responses import success_response

    @app.get("/api/_test/admin-only")
    @role_required("admin_general")
    def admin_only():
        return success_response({"ok": True})

    @app.get("/api/_test/boom")
    def boom():
        raise RuntimeError("error intencional de prueba")



def _init_extensions(app: Flask) -> None:
    """Enlaza SQLAlchemy, sesión, CSRF, límite y modelos."""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.session_protection = "basic"
    import app.db_models  # noqa: F401


def _register_login_handlers() -> None:
    """Cargador de usuario activo y respuesta 401 JSON."""

    @login_manager.user_loader
    def load_user(user_id: str):
        user = find_by_id(user_id)
        if user is None:
            return None
        db.session.refresh(user)
        if user.estado != "activo":
            return None
        return user

    @login_manager.unauthorized_handler
    def unauthorized():
        return error_response("unauthorized", "Autenticación requerida.", 401)
