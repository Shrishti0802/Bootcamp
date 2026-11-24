from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, field_validator, model_validator


class ServiceType(str, Enum):
    AMC = "AMC"
    REPAIR = "REPAIR"
    INSTALLATION = "INSTALLATION"


class Status(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class Ticket(BaseModel):
    ticket_id: str
    customer_name: str
    service_type: ServiceType
    status: Status
    opened_on: date
    closed_on: date | None = None

    @field_validator("ticket_id", "customer_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("closed_on", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        # In a CSV, an empty cell arrives as "" (not None).
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @model_validator(mode="after")
    def check_dates(self) -> Ticket:
        if self.closed_on and self.closed_on < self.opened_on:
            raise ValueError("closed_on cannot be before opened_on")
        if self.status is Status.CLOSED and self.closed_on is None:
            raise ValueError("closed tickets need a closed_on date")
        return self