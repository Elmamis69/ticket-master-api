"""
Pruebas para el sistema de comentarios en tickets
"""
import pytest


def test_crear_comentario(client, user_token, ticket_id):
    """Debe permitir crear un comentario en un ticket"""
    response = client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"content": "Comentario de prueba"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Comentario de prueba"


def test_listar_comentarios(client, user_token, ticket_id):
    """Debe listar los comentarios de un ticket"""
    response = client.get(
        f"/api/v1/tickets/{ticket_id}/comments",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_eliminar_comentario(client, user_token, ticket_id, comment_id):
    """Debe permitir eliminar un comentario propio"""
    response = client.delete(
        f"/api/v1/tickets/{ticket_id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 204
