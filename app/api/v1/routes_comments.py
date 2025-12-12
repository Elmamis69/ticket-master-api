from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate, 
    CommentResponse
)

router = APIRouter(prefix = "/tickets", tags = ["Comments"])

# ============================================
# CREAR COMENTARIO EN UN TICKET
# ============================================
@router.post("/{ticket_id}/comments", response_model = CommentResponse, status_code = status.HTTP_201_CREATED)
def create_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear un comentario en un ticket.

    Permisos:
    - USER: puede comentar solo en sus propios tickets.
    - AGENT: puede comentar en tickets asignados a él o sin asignar
    - ADMIN: puede comentar en cualquier ticket.
    """
    # Verificar que el ticket exista    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Ticket no encontrado"
        )

    # Verificar permisos según rol
    if current_user.role == UserRole.USER:
        # USER solo puede comentar en sus propios tickets
        if ticket.creator_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "No tienes permiso para comentar en este ticket"
            )
    
    elif current_user.role == UserRole.AGENT:
        # AGENT puede comentar en tickets asignados a él o sin asignar
        if ticket.assigned_agent_id and ticket.assigned_agent_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "No tienes permiso para comentar en este ticket"
            )
        
    # ADMIN puede comentar en cualquier ticket (no hay restricción)

    # Crear el comentario
    new_comment = Comment(
        content = comment_data.content,
        ticket_id = ticket_id,
        author_id = current_user.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

# ============================================
# LISTAR COMENTARIOS DE UN TICKET
# ============================================
@router.get("/{ticket_id}/comments", response_model = List[CommentResponse])
def list_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener todos los comentarios de un ticket.

    Se verifica que el usuario tenga acceso al ticket.
    """
    # Verificar que el ticket existe    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Ticket no encontrado"
        )

    # Verificar permisos (mismo que get_ticket)
    if current_user.role == UserRole.USER:
        if ticket.creator_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "No tienes permiso para ver comentarios en este ticket"
            )
    
    elif current_user.role == UserRole.AGENT:
        if ticket.assigned_agent_id and ticket.assigned_agent_id != current_user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "No tienes permiso para ver comentarios en este ticket"
            )
        
    # Obtener comentarios ordenados por fecha
    comments = db.query(Comment).filter(
        Comment.ticket_id == ticket_id
        ).order_by(Comment.created_at.asc()).all()
    
    return comments

# ============================================
# ACTUALIZAR COMENTARIO
# ============================================
@router.put("/{ticket_id}/comments/{comment_id}", response_model = CommentResponse)
def update_comment(
    ticket_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar un comentario existente.

    Solo el autor del comentario o un ADMIN pueden actualizarlo.
    """
    # Verificar que el comentario exista
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.ticket_id == ticket_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Comentario no encontrado"
        )
    
    # Verificar permisos: solo el autor o ADMIN pueden editar
    if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permiso para actualizar este comentario"
        )
    
    # Actualizar contenido
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return comment

# ============================================
# ELIMINAR COMENTARIO
# ============================================
@router.delete("/{ticket_id}/comments/{comment_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_comment(
    ticket_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un comentario existente.

    Solo el autor del comentario o un ADMIN pueden eliminarlo.
    """
    # Verificar que el comentario existe y pertenece al ticket.
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.ticket_id == ticket_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Comentario no encontrado"
        )
    
    # Verificar permisos: solo el autor o ADMIN pueden eliminar
    if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No tienes permiso para eliminar este comentario"
        )
    
    # Eliminar comentario
    db.delete(comment)
    db.commit()

    return None