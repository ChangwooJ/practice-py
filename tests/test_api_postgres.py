import os
import unittest
from unittest.mock import patch
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import make_conninfo

from api import app
from campaigns import Campaign
from storage import create_campaign_table, save_campaigns


@unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "테스트용 PostgreSQL 주소가 필요합니다")
class CampaignApiPostgresTests(unittest.TestCase):
    def test_api_reflects_saved_campaigns_and_later_updates(self):
        dsn = os.environ["TEST_DATABASE_URL"]
        schema_name = f"api_test_{uuid4().hex}"
        isolated_dsn = make_conninfo(dsn, options=f"-csearch_path={schema_name}")
        with psycopg.connect(dsn) as connection:
            connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name)))

        try:
            create_campaign_table(isolated_dsn)
            save_campaigns(isolated_dsn, [
                Campaign("D01", "검색 광고", 200, 2),
                Campaign("D02", "DB 배너 광고", 500, 0),
            ])
            with patch.dict(os.environ, {"DATABASE_URL": isolated_dsn}):
                with TestClient(app) as client:
                    response = client.get("/campaigns/report")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {
                        "total_cost": 700,
                        "flagged_count": 1,
                        "flagged_campaigns": [
                            {"campaign_id": "D02", "campaign_name": "DB 배너 광고", "cost": 500, "conversions": 0}
                        ],
                    })

                    save_campaigns(isolated_dsn, [Campaign("D02", "DB 배너 광고", 900, 1)])
                    response = client.get("/campaigns/report")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {
                        "total_cost": 1100, "flagged_count": 0, "flagged_campaigns": []
                    })
        finally:
            with psycopg.connect(dsn) as connection:
                connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema_name)))


if __name__ == "__main__":
    unittest.main()
