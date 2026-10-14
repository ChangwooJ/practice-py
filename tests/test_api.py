import os
import unittest
from unittest.mock import patch

import psycopg
from fastapi.testclient import TestClient

from api import app
from campaigns import Campaign


class CampaignReportApiTests(unittest.TestCase):
    def setUp(self):
        env_patch = patch.dict(os.environ, {"DATABASE_URL": "postgresql://example.invalid/campaigns"})
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def test_returns_report_from_database_campaigns(self):
        campaigns = [
            Campaign("D01", "검색 광고", 200, 2),
            Campaign("D02", "DB 배너 광고", 500, 0),
            Campaign("D03", "무료 광고", 0, 0),
        ]
        with patch("storage.load_campaigns_from_db", return_value=campaigns):
            response = TestClient(app).get("/campaigns/report")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_cost": 700,
                "flagged_count": 1,
                "flagged_campaigns": [
                    {"campaign_id": "D02", "campaign_name": "DB 배너 광고", "cost": 500, "conversions": 0}
                ],
            },
        )

    def test_returns_empty_report_for_empty_database(self):
        with patch("storage.load_campaigns_from_db", return_value=[]):
            response = TestClient(app).get("/campaigns/report")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"total_cost": 0, "flagged_count": 0, "flagged_campaigns": []})

    def test_returns_503_when_database_url_is_missing(self):
        os.environ.pop("DATABASE_URL", None)
        response = TestClient(app).get("/campaigns/report")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "데이터베이스 연결 설정이 필요합니다"})

    def test_returns_503_without_exposing_database_error(self):
        with patch("storage.load_campaigns_from_db", side_effect=psycopg.OperationalError("private-db-details")):
            response = TestClient(app).get("/campaigns/report")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "광고 데이터를 조회할 수 없습니다"})
        self.assertNotIn("private-db-details", response.text)


if __name__ == "__main__":
    unittest.main()
