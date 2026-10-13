import os
import unittest
from uuid import uuid4

import psycopg

from campaigns import Campaign
from storage import create_campaign_table, load_campaigns_from_db, save_campaigns


class PostgresStorageTests(unittest.TestCase):
    @unittest.skipUnless(os.getenv("TEST_DATABASE_URL"), "테스트용 PostgreSQL 주소가 필요합니다")
    def test_saves_reads_and_updates_campaign_by_id(self):
        dsn = os.environ["TEST_DATABASE_URL"]
        campaign_id = f"TEST_{uuid4().hex}"
        original = Campaign(campaign_id, "테스트 광고", 100, 0)
        updated = Campaign(campaign_id, "수정된 광고", 200, 2)

        create_campaign_table(dsn)
        try:
            save_campaigns(dsn, [original])
            self.assertEqual(
                [campaign for campaign in load_campaigns_from_db(dsn) if campaign.campaign_id == campaign_id],
                [original],
            )

            save_campaigns(dsn, [updated])
            self.assertEqual(
                [campaign for campaign in load_campaigns_from_db(dsn) if campaign.campaign_id == campaign_id],
                [updated],
            )
        finally:
            with psycopg.connect(dsn) as connection:
                connection.execute("DELETE FROM campaigns WHERE campaign_id = %s", (campaign_id,))


if __name__ == "__main__":
    unittest.main()
