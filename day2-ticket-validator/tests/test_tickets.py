from pathlib import Path

from tickets.loader import load_tickets

HEADER = "ticket_id,customer_name,service_type,status,opened_on,closed_on\n"


def write_csv(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "tickets.csv"
    p.write_text(text, encoding="utf-8")
    return p


def test_valid_row(tmp_path):
    p = write_csv(tmp_path, HEADER + "T1,Asha,AMC,OPEN,2025-01-15,\n")
    result = load_tickets(p)
    assert len(result.valid) == 1
    assert result.invalid == []
    assert result.valid[0].customer_name == "Asha"


def test_missing_field(tmp_path):
    # Header has no customer_name column at all.
    text = "ticket_id,service_type,status,opened_on,closed_on\nT1,AMC,OPEN,2025-01-15,\n"
    result = load_tickets(write_csv(tmp_path, text))
    assert result.valid == []
    assert len(result.invalid) == 1
    assert any("customer_name" in e for e in result.invalid[0].errors)


def test_bad_date(tmp_path):
    p = write_csv(tmp_path, HEADER + "T1,Asha,AMC,OPEN,31-02-2025,\n")
    result = load_tickets(p)
    assert result.valid == []
    assert any("opened_on" in e for e in result.invalid[0].errors)


def test_bad_enum(tmp_path):
    p = write_csv(tmp_path, HEADER + "T1,Asha,WARRANTY,OPEN,2025-01-15,\n")
    result = load_tickets(p)
    assert result.valid == []
    assert any("service_type" in e for e in result.invalid[0].errors)


def test_empty_file(tmp_path):
    result = load_tickets(write_csv(tmp_path, ""))
    assert result.valid == []
    assert result.invalid == []