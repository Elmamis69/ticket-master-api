from datetime import datetime
from typing import Optional
from app.db.influxdb import influx_db
from app.core.logging import get_logger

logger = get_logger("metrics")

class MetricsService:
    """
    Servicio para registrar métricas en InfluxDB.
    """

    @staticmethod
    def record_ticket_created(ticket_id: int, creator_id: int, priority: str):
        """
        Registrar la creación de un ticket.
        """
        try:
            influx_db.write_point(
                measurement="ticket_created",
                tags={
                    "priority": priority,
                    "creator_id": str(creator_id)
                },
                fields={
                    "ticket_id": ticket_id,
                    "count": 1
                }
            )
            logger.info(f"Metric recorded: ticket_created - ID {ticket_id}")
        except Exception as e:
            logger.error(f"Failed to record ticket_created metric: {e}")

    @staticmethod
    def record_ticket_status_change(ticket_id: int, old_status: str, new_status: str, user_id: int):
        """
        Registrar el cambio de estado de un ticket.
        """
        try:
            influx_db.write_point(
                measurement="ticket_status_change",
                tags={
                    "old_status": old_status,
                    "new_status": new_status,
                    "user_id": str(user_id)
                },
                fields={
                    "ticket_id": ticket_id,
                    "count": 1
                }
            )
            logger.info(f"Metric recorded: status change {old_status} -> {new_status}")
        except Exception as e:
            logger.error(f"Failed to record status change metric: {e}")

    @staticmethod
    def record_ticket_assigned(ticket_id: int, agent_id: int, assigned_by_id: int):
        """
        Registrar la asignación de un ticket a un agente.
        """
        try:
            influx_db.write_point(
                measurement="ticket_assigned",
                tags={
                    "assigned_agent_id": str(agent_id),
                    "assigned_by_id": str(assigned_by_id)
                },
                fields={
                    "ticket_id": ticket_id,
                    "count": 1
                }
            )
            logger.info(f"Metric recorded: ticket assigned to agent {agent_id}")
        except Exception as e:
            logger.error(f"Failed to record ticket assigned metric: {e}")

    @staticmethod
    def record_ticket_resolved(ticket_id: int, agent_id: Optional[int], resolution_time_seconds: int):
        """
        Registrar la resolución de un ticket.
        """
        try:
            tags = {"ticket_id": str(ticket_id)}
            if agent_id:
                tags["agent_id"] = str(agent_id)

            influx_db.write_point(
                measurement="ticket_resolved",
                tags=tags,
                fields={
                    "resolution_time_seconds": resolution_time_seconds,
                    "count": 1
                }
            )
            logger.info(f"Metric recorded: ticket resolved - ID {ticket_id}")
        except Exception as e:
            logger.error(f"Failed to record ticket resolved metric: {e}")

    @staticmethod
    def record_comment_created(ticket_id: int, author_id: int):
        """
        Registrar la creación de un comentario.
        """
        try:
            influx_db.write_point(
                measurement="comment_created",
                tags={
                    "ticket_id": str(ticket_id),
                    "author_id": str(author_id)
                },
                fields={
                    "count": 1
                }
            )
            logger.info(f"Metric recorded: comment created on ticket {ticket_id}")
        except Exception as e:
            logger.error(f"Failed to record comment created metric: {e}")

# Instancia global del servicio
metrics_service = MetricsService()