import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    campaign_name: str
    cost: int
    conversions: int


def load_campaigns(file_path: str | Path) -> list[dict[str, str]]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required_columns = {"campaign_id", "campaign_name", "cost", "conversions"}
        missing_columns = required_columns - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"CSV 필수 열 누락: {', '.join(sorted(missing_columns))}")
        return list(reader)


def _required_text(row: dict[str, str], field: str, row_number: int) -> str:
    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"{row_number}행 {field}: 값이 필요합니다")
    return value.strip()


def _nonnegative_int(row: dict[str, str], field: str, row_number: int) -> int:
    value = _required_text(row, field, row_number)
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{row_number}행 {field}: 0 이상의 정수가 필요합니다") from exc
    if number < 0:
        raise ValueError(f"{row_number}행 {field}: 0 이상의 정수가 필요합니다")
    return number


def parse_campaigns(rows: list[dict[str, str]]) -> list[Campaign]:
    campaigns = []
    for row_number, row in enumerate(rows, start=2):
        campaigns.append(
            Campaign(
                campaign_id=_required_text(row, "campaign_id", row_number),
                campaign_name=_required_text(row, "campaign_name", row_number),
                cost=_nonnegative_int(row, "cost", row_number),
                conversions=_nonnegative_int(row, "conversions", row_number),
            )
        )
    return campaigns


def find_spend_without_conversions(campaigns: list[Campaign]) -> list[Campaign]:
    flagged = []
    for campaign in campaigns:
        if campaign.cost > 0 and campaign.conversions == 0:
            flagged.append(campaign)
    return flagged
