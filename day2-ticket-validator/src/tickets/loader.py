from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from .models import Ticket

logger = logging.getLogger(__name__)


@dataclass
class BadRow:
    line: int
    row: dict[str, str]
    errors: list[str]


@dataclass
class LoadResult:
    valid: list[Ticket] = field(default_factory=list)
    invalid: list[BadRow] = field(default_factory=list)


def _format_errors(exc: ValidationError) -> list[str]:
    messages = []
    for err in exc.errors():
        where = ".".join(str(p) for p in err["loc"]) or "row"
        messages.append(f"{where}: {err['msg']}")
    return messages


def load_tickets(path: str | Path) -> LoadResult:
    result = LoadResult()
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line = reader.line_num
            try:
                ticket = Ticket(**row)
            except ValidationError as exc:
                errors = _format_errors(exc)
                result.invalid.append(BadRow(line, row, errors))
                logger.warning("Line %d rejected: %s", line, "; ".join(errors))
            else:
                result.valid.append(ticket)
                logger.info("Line %d OK: %s", line, ticket.ticket_id)
    logger.info("Done: %d valid, %d invalid", len(result.valid), len(result.invalid))
    return result