import unittest

from fastapi.testclient import TestClient

from api import app


class CampaignReportApiTests(unittest.TestCase):
    def test_returns_totals_and_flagged_campaigns_from_csv(self):
        response = TestClient(app).get("/campaigns/report")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_cost": 20000,
                "flagged_count": 1,
                "flagged_campaigns": [
                    {"campaign_id": "A02", "campaign_name": "배너 광고", "cost": 8000, "conversions": 0}
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
