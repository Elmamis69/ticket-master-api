from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship 
from app.db.session import Base

class Comment(Base):
    """
    Modelo de comentarios en tickets

    Relaciones:
    - ticket: Ticket al que pertenece el comentario
    - author: Usuario que escribió el comentario
    """
    __tablename__ = "comments"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    # Relaciones (Foreign Keys)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones ORM
    ticket = relationship("Ticket", backref="comments")
    author = relationship("User", backref="comments")

    def __repr__(self):
        return f"<Comment #{self.id} on Ticket #{self.ticket_id}>"
