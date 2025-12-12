from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.ticket import TicketStatus, TicketPriority

class TicketBase(BaseModel):
    """
    Atributos comunes de un ticket
    """
    title: str = Field(..., min_length = 5, max_length = 200)
    description: str = Field(..., min_length = 10)
    priority: TicketPriority = TicketPriority.MEDIUM

class TicketCreate(TicketBase):
    """
    Schema para crear un ticket nuevo.
    El creator_id se obtiene del token JWT, no del body.
    """
    pass # Hereda todo de TicketBase

class TicketUpdate(BaseModel):
    """
    Schema para actualizar un ticket.
    Todos los campos son opcionales.
    """
    title: Optional[str] = Field(None, min_length = 5, max_length = 200)
    description: Optional[str] = Field(None, min_length = 10)
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_agent_id: Optional[int] = None

class TicketAssign(BaseModel):
    """
    Schema específico para asignar un agente al ticket.
    """
    assigned_agent_id: int

class TicketResponse(TicketBase):
    """
    Schema para respuestas de la API.
    Incluye todos los datos del ticket.
    """
    id: int
    status: TicketStatus
    creator_id: int
    assigned_agent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Para leer desde modelos SQLAlchemy

class TicketListResponse(BaseModel):
    """
    Schema para listar múltiples tickets con información resumida
    """
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    creator_id: int
    assigned_agent_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True