from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class TicketStats(BaseModel):
    """
    Estadísticas generales de tickets.
    """
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int

class PriorityStats(BaseModel):
    """
    Estadísticas por prioridad.
    """
    low: int
    medium: int
    high: int
    critical: int

class AgentStats(BaseModel):
    """
    Estadísticas de un agente.
    """
    agent_id: int
    agent_name: str
    assigned_tickets: int
    resolved_tickets: int
    avg_resolution_time_hours: Optional[float] = None

class TimeSeriesData(BaseModel):
    """
    Datos de series temporales.
    """
    timestamp: str
    value: float

class AnalyticsResponse(BaseModel):
    """
    Respuesta completa de analytics.
    """
    ticket_stats: TicketStats
    priority_stats: PriorityStats
    top_agents: List[AgentStats]
    tickets_over_time: List[TimeSeriesData]
    avg_resolution_time_hours: Optional[float] = None