from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    """
    Atributos comunes de un comentario
    """
    content: str = Field(..., min_length=1,max_length=2000)

class CommentCreate(CommentBase):
    """
    Schema para crear un comentario.
    El ticket_id viene de la URL, el author_id del token JWT
    """
    pass

class CommentUpdate(BaseModel):
    """
    Schema para actualizar un comentario.
    Solo se puede actualizar el contenido.
    """
    content: str = Field(None, min_length=1, max_length=2000)

class CommentResponse(CommentBase):
    """
    Schema para respuestas de la API.
    """
    id: int
    ticket_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CommentWithAuthor(CommentResponse):
    """
    Schema para extendido que incluye información del autor.
    Útil para mostrar comentarios con nombre del usuario
    """
    author_full_name: Optional[str] = None

    class Config:
        from_attributes = True