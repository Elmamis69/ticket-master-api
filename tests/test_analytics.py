"""
Pruebas para los endpoints de analytics
"""
import pytest

def crear_ticket_y_resolver(client, user_token, admin_token, agent_id):
    # Crear ticket con usuario normal
    response = client.post(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Ticket analytics", "description": "Descripción válida para analytics", "priority": "high"}
    )
    print('DEBUG status:', response.status_code)
    print('DEBUG body:', response.text)
    ticket_id = response.json()["id"]
    # Asignar agente (admin)
    resp_assign = client.post(
        f"/api/v1/tickets/{ticket_id}/assign",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"assigned_agent_id": agent_id}
    )
    print('ASSIGN status:', resp_assign.status_code)
    print('ASSIGN body:', resp_assign.text)
    # Cambiar a in_progress (admin)
    resp_in_progress = client.put(
        f"/api/v1/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "in_progress"}
    )
    print('IN_PROGRESS status:', resp_in_progress.status_code)
    print('IN_PROGRESS body:', resp_in_progress.text)
    # Cambiar a resolved (admin)
    resp_resolved = client.put(
        f"/api/v1/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "resolved"}
    )
    print('RESOLVED status:', resp_resolved.status_code)
    print('RESOLVED body:', resp_resolved.text)
    return ticket_id

def test_dashboard_analytics(client, user_token, admin_token, agent_id):
    """Debe devolver el dashboard de analytics"""
    crear_ticket_y_resolver(client, user_token, admin_token, agent_id)
    response = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "ticket_stats" in data
    assert "total_tickets" in data["ticket_stats"]
    assert "priority_stats" in data
    assert "top_agents" in data


def test_agent_stats(client, user_token, admin_token, agent_id):
    """Debe devolver estadísticas de un agente"""
    crear_ticket_y_resolver(client, user_token, admin_token, agent_id)
    response = client.get(
        f"/api/v1/analytics/agent/{agent_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "resolved_tickets" in data
