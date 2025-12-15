"""
Pruebas para el sistema de tickets (CRUD, asignación, cambio de estado)
"""
import pytest


def test_crear_ticket(client, user_token):
    """Debe permitir crear un ticket nuevo"""
    response = client.post(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "title": "Prueba de ticket",
            "description": "Descripción de prueba",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Prueba de ticket"
    assert data["priority"] == "high"
    assert data["status"] == "open"


def test_listar_tickets(client, user_token):
    """Debe listar los tickets del usuario autenticado"""
    response = client.get(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_actualizar_ticket(client, user_token):
    """Debe permitir actualizar título y descripción"""
    # Crear ticket
    response = client.post(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Actualizar", "description": "desc", "priority": "medium"}
    )
    ticket_id = response.json()["id"]
    # Actualizar
    response = client.put(
        f"/api/v1/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Nuevo título", "description": "Nueva desc"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Nuevo título"


def test_eliminar_ticket(client, user_token):
    """Debe permitir eliminar un ticket propio"""
    response = client.post(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Eliminar", "description": "desc", "priority": "low"}
    )
    ticket_id = response.json()["id"]
    response = client.delete(
        f"/api/v1/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 204
