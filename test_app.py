import pytest
from app import app

@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as cliente:
        yield cliente


def test_pagina_principal(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200


def test_pagina_registro(cliente):
    respuesta = cliente.get("/registro")
    assert respuesta.status_code == 200


def test_pagina_login(cliente):
    respuesta = cliente.get("/login")
    assert respuesta.status_code == 200


def test_admin_requiere_sesion(cliente):
    respuesta = cliente.get("/admin")
    assert respuesta.status_code in (302, 401, 403)


def test_visitante_no_accede_admin(cliente):
    with cliente.session_transaction() as sesion:
        sesion["usuario_id"] = 999
        sesion["rol"] = "visitante"

    respuesta = cliente.get("/admin")
    assert respuesta.status_code == 403