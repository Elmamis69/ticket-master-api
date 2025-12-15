from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.services.metrics_service import metrics_service

from app.db.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketAssign,
    TicketResponse,
    TicketListResponse,
)

router = APIRouter(prefix = "/tickets", tags = ["Tickets"])

# ============================================
# CREAR TICKET
# ============================================
@router.post("/", response_model = TicketResponse, status_code = status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crear un nuevo ticket.
    Cualquier usuario autenticado puede crear tickets.
    """
    new_ticket = Ticket(
        title = ticket_data.title,
        description = ticket_data.description,
        priority = ticket_data.priority,
        creator_id = current_user.id,
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
        # Registrar métrica
    metrics_service.record_ticket_created(
        ticket_id=new_ticket.id,
        creator_id=current_user.id,
        priority=new_ticket.priority.value
    )
    return new_ticket

# ============================================
# LISTAR TICKETS (con permisos por rol)
# ============================================
@router.get("/", response_model = List[TicketListResponse])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Listar tickets según el rol del usuario:
    - USER: solo sus propios tickets
    - AGENT: tickets asignados a él + sin asignar
    - ADMIN: todos los tickets
    """
    if current_user.role == UserRole.ADMIN:
        tickets = db.query(Ticket).all()
    
    elif current_user.role == UserRole.AGENT:
        # Agent ve: tickets asignados a él + sin asignar
        tickets = db.query(Ticket).filter(
            (Ticket.assigned_agent_id == current_user.id) |
            (Ticket.assigned_agent_id == None)
        ).all()

    else: # USER
        # User solo ve sus propios tickets
        tickets = db.query(Ticket).filter(
            Ticket.creator_id == current_user.id
            ).all()
    
    return tickets

# ============================================
# VER DETALLE DE UN TICKET
# ============================================
@router.get("/{ticket_id}", response_model = TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtener los detalles de un ticket específico.
    Verifica permisos según rol.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()                        

    if not ticket:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket no encontrado"
        )

    # Verificar permisos
    if current_user.role == UserRole.USER and ticket.creator_id != current_user.id:
        # Un USER solo puede ver sus propios tickets
        if ticket.creator_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN, 
                detail = "No tienes permiso para ver este ticket")

    elif current_user.role == UserRole.AGENT:
        # Un AGENT solo puede ver tickets asignados a él o sin asignar
        if ticket.assigned_agent_id and ticket.assigned_agent_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN, 
                detail = "No tienes permiso para ver este ticket")
        
    # ADMIN puede ver cualquier ticket (no hay restricción)
    return ticket

# ============================================
# ACTUALIZAR TICKET
# ============================================
@router.put("/{ticket_id}", response_model = TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualizar un ticket.
    - USER: solo puede actualizar título y descripción de sus propios tickets
    - AGENT: puede actualizar cualquier campo
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket no encontrado"
        )

    # Verificar permisos
    if current_user.role == UserRole.USER:
        # USER solo puede editar sus propios tickets
        if ticket.creator_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN, 
                detail = "No tienes permiso para actualizar este ticket"
                )
        # USER solo puede cambiar título y descripción
        if ticket_data.status or ticket_data.assigned_agent_id or not None:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN, 
                detail = "No tienes permiso para actualizar ese campo"
                )
        
    # Actualizar campos (solo los que se enviaron)
    if ticket_data.title is not None:
        ticket.title = ticket_data.title
    if ticket_data.description is not None:
        ticket.description = ticket_data.description
    if ticket_data.priority is not None:
        ticket.priority = ticket_data.priority
    if ticket_data.status is not None:
        # Registrar cambio de estado
        old_status = ticket.status.value
        ticket.status = ticket_data.status
        metrics_service.record_ticket_status_change(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=ticket_data.status.value,
            user_id=current_user.id
        )
        
        # Si se marca como resuelto, calcular tiempo y registrar métrica
        if ticket_data.status == TicketStatus.RESOLVED and not ticket.resolved_at:
            ticket.resolved_at = datetime.now(timezone.utc)
            # Asegurar que ambos datetimes sean aware (UTC)
            created = ticket.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            resolved = ticket.resolved_at
            if resolved.tzinfo is None:
                resolved = resolved.replace(tzinfo=timezone.utc)
            resolution_time = int((resolved - created).total_seconds())
            metrics_service.record_ticket_resolved(
                ticket_id=ticket.id,
                agent_id=ticket.assigned_agent_id,
                resolution_time_seconds=resolution_time
            )
    if ticket_data.assigned_agent_id is not None:
        ticket.assigned_agent_id = ticket_data.assigned_agent_id

    db.commit()
    db.refresh(ticket)

    return ticket

# ============================================
# ASIGNAR AGENTE (endpoint específico)
# ============================================
@router.patch("/{ticket_id}/assign", response_model = TicketResponse)
def assign_ticket(
    ticket_id: int,
    assignment: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Asignar un agente a un ticket.
    Solo ADMIN y AGENT pueden asignar tickets.
    """
    # Solo admin y agent pueden asignar
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Solo admins y agents pueden asignar tickets"
        )

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket no encontrado"
        )
    
    # Verificar que el usuario a asignar existe y es AGENT
    agent = db.query(User).filter(User.id == assignment.assigned_agent_id).first()
    if not agent:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Agente no encontrado"
        )
    
    if agent.role != UserRole.AGENT and agent.role != UserRole.ADMIN:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "El usuario asignado debe ser un agente o admin"
        )

    ticket.assigned_agent_id = assignment.assigned_agent_id

    # Registrar métrica de asignación
    metrics_service.record_ticket_assigned(
        ticket_id=ticket.id,
        agent_id=assignment.assigned_agent_id,
        assigned_by_id=current_user.id
    )

    # Cambiar estado a IN_PROGRESS si está OPEN
    if ticket.status == TicketStatus.OPEN:
        ticket.status = TicketStatus.IN_PROGRESS

    db.commit()
    db.refresh(ticket)

    return ticket

# ============================================
# ELIMINAR TICKET (soft delete o real)
# ============================================
@router.delete("/{ticket_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Eliminar un ticket.
    Solo ADMIN puede eliminar tickets.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Solo admins pueden eliminar tickets"
        )

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket no encontrado"
        )

    db.delete(ticket)
    db.commit()

    return None