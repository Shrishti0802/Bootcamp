from typing import Literal, Optional
from pydantic import BaseModel, Field


class Triage(BaseModel):
    equipment: str = Field(min_length=1)
    urgency: Literal["low", "medium", "high", "critical"]
    hospital: Optional[str] = None  # null when the complaint doesn't name one
    next_action: str = Field(min_length=1)