from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.db.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.schemas.analytics import (
    AnalyticsResponse,
    TicketStats,
    PriorityStats,
    AgentStats,
    TimeSeriesData
)

router = APIRouter(prefix = "/analytics", tags=["Analytics"])

# ============================================
# DASHBOARD GENERAL DE ANALYTICS
# ============================================
@router.get("/dashboard", response_model = AnalyticsResponse)
def get_analytics_dashboard(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener dashboard completo de analytics.

    Solo accesible para ADMIN y AGENT.
    """
    # Solo ADMIN y AGENT pueden ver analytics
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Solo ADMIN y AGENT pueden acceder a analytics"
        )
    
    # Calcular fecha de inicio
    start_date = datetime.utcnow() - timedelta(days=days)

    # 1. Estadísticas generales de tickets
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
    in_progress = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()
    closed = db.query(Ticket).filter(Ticket.status == TicketStatus.CLOSED).count()

    ticket_stats = TicketStats(
        total_tickets = total_tickets,
        open_tickets = open_tickets,
        in_progress_tickets = in_progress,
        resolved_tickets = resolved,
        closed_tickets = closed
    )

    # 2. Estadísticas por prioridad
    low = db.query(Ticket).filter(Ticket.priority == TicketPriority.LOW).count()
    medium = db.query(Ticket).filter(Ticket.priority == TicketPriority.MEDIUM).count()
    high = db.query(Ticket).filter(Ticket.priority == TicketPriority.HIGH).count()
    critical = db.query(Ticket).filter(Ticket.priority == TicketPriority.CRITICAL).count()

    priority_stats = PriorityStats(
        low = low,
        medium = medium,
        high = high,
        critical = critical
    )

    # 3. Top agentes
    agents_data = db.query(
        User.id,
        User.full_name,
        func.count(Ticket.id).label("assigned_tickets"),
    ).join(
        Ticket, Ticket.assigned_agent_id == User.id, isouter=True
    ).filter(
        User.role.in_([UserRole.AGENT, UserRole.ADMIN])
    ).group_by(User.id, User.full_name).all()

    top_agents = []
    for agent_id, agent_name, assigned_count in agents_data:
        resolved_count = db.query(Ticket).filter(
            Ticket.assigned_agent_id == agent_id,
            Ticket.status == TicketStatus.RESOLVED
        ).count()

        # Calcular tiempo promedio de resolución
        resolution_tickets = db.query(Ticket).filter(
            Ticket.assigned_agent_id == agent_id,
            Ticket.status == TicketStatus.RESOLVED,
            Ticket.resolved_at.isnot(None)
        ).all()

        avg_time = None
        if resolution_tickets:
            total_seconds = sum(
                (ticket.resolved_at - ticket.created_at).total_seconds()
                for ticket in resolution_tickets
            )
            avg_time = total_seconds / len(resolution_tickets) / 3600  # Convertir a horas

        top_agents.append(AgentStats(
            agent_id = agent_id,
            agent_name = agent_name,
            assigned_tickets = assigned_count or 0,
            resolved_tickets = resolved_count,
            avg_resolution_time_hours = round(avg_time, 2) if avg_time else None
        ))

    # Ordenar por tickets resueltos
    top_agents.sort(key=lambda x: x.resolved_tickets, reverse=True)

    # 4. Tickets creados en los últimos N días (series temporales)
    tickets_over_time = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)

        count = db.query(Ticket).filter(
            Ticket.created_at >= date,
            Ticket.created_at < next_date
        ).count()

        tickets_over_time.append(TimeSeriesData(
            timestamp = date.strftime("%Y-%m-%d"),
            value = float(count)
        ))

    # 5. Tiempo promedio de resolución global
    all_resolved = db.query(Ticket).filter(
        Ticket.status == TicketStatus.RESOLVED,
        Ticket.resolved_at.isnot(None)
    ).all()

    avg_resolution_time = None
    if all_resolved:
        total_seconds = sum(
            (ticket.resolved_at - ticket.created_at).total_seconds()
            for ticket in all_resolved
        )
        avg_resolution_time = round((total_seconds / len(all_resolved)) / 3600, 2)  # Convertir a horas

    return AnalyticsResponse(
        ticket_stats = ticket_stats,
        priority_stats = priority_stats,
        top_agents = top_agents[:10], # Top 10 agentes
        tickets_over_time = tickets_over_time,
        avg_resolution_time_hours = avg_resolution_time
    )

# ============================================
# ESTADÍSTICAS DE AGENTE INDIVIDUAL
# ============================================
@router.get("/agent/{agent_id}", response_model = AgentStats)
def get_agent_stats(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener estadísticas de un agente específico.

    AGENT puede ver solo sus propias estadísticas.
    ADMIN puede ver cualquier agente
    """
    # Verificar permisos
    if current_user.role == UserRole.AGENT and current_user.id != agent_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Agentes solo pueden ver sus propias estadísticas"
        )
    
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Usuarios no pueden acceder a estadísticas de agentes"
        )
    
    # Verificar que el agente existe
    agent = db.query(User).filter(User.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Agente no encontrado"
        )
    
    # Calcular estadísticas
    assigned_count = db.query(Ticket).filter(
        Ticket.assigned_agent_id == agent_id
    ).count()

    resolved_count = db.query(Ticket).filter(
        Ticket.assigned_agent_id == agent_id,
        Ticket.status == TicketStatus.RESOLVED
    ).count()

    # Tiempo promedio de resolución
    resolution_tickets = db.query(Ticket).filter(
        Ticket.assigned_agent_id == agent_id,
        Ticket.status == TicketStatus.RESOLVED,
        Ticket.resolved_at.isnot(None)
    ).all()

    avg_time = None
    if resolution_tickets:
        total_seconds = sum(
            (ticket.resolved_at - ticket.created_at).total_seconds()
            for ticket in resolution_tickets
        )
        avg_time = round((total_seconds / len(resolution_tickets)) / 3600, 2)  # Convertir a horas

    return AgentStats(
        agent_id = agent.id,
        agent_name = agent.full_name,
        assigned_tickets = assigned_count,
        resolved_tickets = resolved_count,
        avg_resolution_time_hours = avg_time
    )