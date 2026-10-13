import os
from pathlib import Path

from campaigns import load_campaigns, parse_campaigns
from storage import create_campaign_table, save_campaigns


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL 환경 변수를 설정하세요")

    csv_path = Path(__file__).parent / "data" / "campaigns.csv"
    campaigns = parse_campaigns(load_campaigns(csv_path))
    create_campaign_table(database_url)
    save_campaigns(database_url, campaigns)
    print(f"PostgreSQL에 광고 {len(campaigns)}건을 저장했습니다")
