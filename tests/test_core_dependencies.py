import importlib
import sys
import types


def test_dependencies_imports_verify_token_from_app_core_security(monkeypatch):
    module_name = "app.core.dependencies"
    sys.modules.pop(module_name, None)

    fastapi_module = types.ModuleType("fastapi")

    def depends(value):
        return value

    class HTTPException(Exception):
        def __init__(self, status_code=None, detail=None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    fastapi_module.Depends = depends
    fastapi_module.HTTPException = HTTPException
    fastapi_module.status = types.SimpleNamespace(HTTP_401_UNAUTHORIZED=401)

    fastapi_security_module = types.ModuleType("fastapi.security")

    class HTTPBearer:
        def __init__(self, *args, **kwargs):
            pass

    class OAuth2PasswordBearer:
        def __init__(self, *args, **kwargs):
            pass

    fastapi_security_module.HTTPBearer = HTTPBearer
    fastapi_security_module.OAuth2PasswordBearer = OAuth2PasswordBearer

    jose_module = types.ModuleType("jose")

    class JWTError(Exception):
        pass

    class JWT:
        @staticmethod
        def decode(*args, **kwargs):
            return {"user_id": 1, "tenant_id": "t1", "role": "user"}

    jose_module.JWTError = JWTError
    jose_module.jwt = JWT()

    config_module = types.ModuleType("app.core.config")
    config_module.settings = types.SimpleNamespace(
        SECRET_KEY="test-secret",
        ALGORITHM="HS256",
    )

    security_module = types.ModuleType("app.core.security")

    def verify_token(token):
        return {"token": token}

    security_module.verify_token = verify_token

    monkeypatch.setitem(sys.modules, "fastapi", fastapi_module)
    monkeypatch.setitem(sys.modules, "fastapi.security", fastapi_security_module)
    monkeypatch.setitem(sys.modules, "jose", jose_module)
    monkeypatch.setitem(sys.modules, "app.core.config", config_module)
    monkeypatch.setitem(sys.modules, "app.core.security", security_module)
    monkeypatch.delitem(sys.modules, "core.security", raising=False)

    module = importlib.import_module(module_name)

    assert module.verify_token is verify_token