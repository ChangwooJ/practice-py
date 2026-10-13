import csv
from pathlib import Path


def load_campaigns(file_path: str | Path) -> list[dict[str, str]]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))
