"""Ticket endpoints, filtering, pagination and CRUD operations."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.schemas import (
    TicketCreate,
    TicketPage,
    TicketPriority,
    TicketRead,
    TicketStatus,
    TicketUpdate,
)
from app.security import require_api_token

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(require_api_token)],
)


def get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    ticket = Ticket(**payload.model_dump(mode="json"))
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=TicketPage)
def list_tickets(
    db: Session = Depends(get_db),
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    priority: TicketPriority | None = None,
    assigned_to: str | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TicketPage:
    filters = []
    if status_filter is not None:
        filters.append(Ticket.status == status_filter.value)
    if priority is not None:
        filters.append(Ticket.priority == priority.value)
    if assigned_to is not None:
        filters.append(Ticket.assigned_to == assigned_to)

    total = db.scalar(select(func.count()).select_from(Ticket).where(*filters)) or 0
    order = Ticket.id.desc() if sort == "newest" else Ticket.id.asc()
    items = db.scalars(
        select(Ticket).where(*filters).order_by(order).limit(limit).offset(offset)
    ).all()
    return TicketPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/{ticket_id}", response_model=TicketRead)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Ticket:
    return get_ticket_or_404(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = get_ticket_or_404(db, ticket_id)
    changes = payload.model_dump(exclude_unset=True, mode="json")
    for name in ("title", "status", "priority"):
        if name in changes and changes[name] is None:
            raise HTTPException(status_code=422, detail=f"{name} cannot be null")
    for key, value in changes.items():
        setattr(ticket, key, value)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Response:
    ticket = get_ticket_or_404(db, ticket_id)
    db.delete(ticket)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
