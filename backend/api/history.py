"""Detection Event History API.
Maintains local SQLite detection logs and human verification updates.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.database.database import get_db
from backend.database.models import DetectionEvent

router = APIRouter(prefix="/api/history", tags=["history"])

class VerificationUpdateRequest(BaseModel):
    human_verification: str # "CONFIRMED", "FALSE_ALARM", "DISMISSED"

@router.get("")
def get_detection_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve chronologically ordered detection events from SQLite."""
    events = (
        db.query(DetectionEvent)
        .order_by(DetectionEvent.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [e.to_dict() for e in events]

@router.post("/{event_id}/verify")
def update_human_verification(
    event_id: int,
    req: VerificationUpdateRequest,
    db: Session = Depends(get_db)
):
    """Enforces human-in-the-loop verification on AI potential threats."""
    event = db.query(DetectionEvent).filter(DetectionEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Detection event not found.")

    event.human_verification = req.human_verification.upper()
    db.commit()
    db.refresh(event)
    return event.to_dict()

@router.delete("")
def clear_detection_history(db: Session = Depends(get_db)):
    """Deletes past detection events from the local SQLite database."""
    deleted_count = db.query(DetectionEvent).delete()
    db.commit()
    return {"status": "SUCCESS", "deleted_records": deleted_count}
