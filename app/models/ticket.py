from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class TicketStatus(str, enum.Enum):
    """
    Estados del ciclo de vida de un ticket
    """
    OPEN = "open" # Recien creado
    IN_PROGRESS = "in_progress" # Asignado y en trabajo
    PENDING = "pending" # Esperando respuesta del usuario
    RESOLVED = "resolved" # Solucionado
    CLOSED = "closed" # Cerrado definitivamente

class TicketPriority(str, enum.Enum):
    """
    Niveles de prioridad del ticket
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Ticket(Base):
    """
    Modelo principal de tickets del sistema

    Relaciones:
    - creator: Usuario que creó el ticket (FK a users)
    - assigned_agent: Agente asignado al ticket (FK a users, opcional)
    """
    __tablename__ = "tickets"

    # Campos principales
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(200), nullable = False)
    description = Column(Text, nullable = False)

    # Estado y prioridad
    status = Column(Enum(TicketStatus), default = TicketStatus.OPEN, nullable = False)
    priority = Column(Enum(TicketPriority), default = TicketPriority.MEDIUM, nullable = False)

    # Relaciones (Foreign Keys)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable = True)

    # Timestamps
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone = True), nullable = True)

    # Relaciones ORM (para acceder a los objetos User relacionados)
    # Esto te permite hacer: ticket.creator o ticket.assigned_agent.full_name
    creator = relationship("User", foreign_keys=[creator_id], backref = "created_tickets")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id], backref = "assigned_tickets")

    def __repr__(self):
        return f"<Ticket #{self.id}: {self.title[:30]}>"