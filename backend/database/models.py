from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DetectionEvent(Base):
    """Stores local detection audit records.
    Stores metadata only to respect privacy.
    """
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    object_type = Column(String, nullable=False, index=True) # firearm, knife
    confidence = Column(Float, nullable=False)                # e.g., 0.94
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source = Column(String, default="camera_0")              # camera source ID
    alert_status = Column(String, default="TRIGGERED")       # TRIGGERED, SUPPRESSED_COOLDOWN, DISMISSED
    bounding_box = Column(String, nullable=True)             # "[x1, y1, x2, y2]" JSON string
    human_verification = Column(String, default="PENDING")   # PENDING, CONFIRMED, FALSE_ALARM

    def to_dict(self):
        return {
            "id": self.id,
            "object_type": self.object_type,
            "confidence": round(self.confidence, 4),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "alert_status": self.alert_status,
            "bounding_box": self.bounding_box,
            "human_verification": self.human_verification
        }
