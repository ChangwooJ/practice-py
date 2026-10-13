import tempfile
import unittest
from pathlib import Path

from campaigns import load_campaigns


class LoadCampaignsTests(unittest.TestCase):
    def test_reads_rows_by_column_name_and_preserves_quoted_commas(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            csv_path = Path(directory) / "campaigns.csv"
            csv_path.write_text(
                'campaign_id,campaign_name,cost,conversions\n'
                'A01,"검색, 브랜드 광고",12000,3\n'
                'A02,배너 광고,8000,0\n',
                encoding="utf-8",
            )

            self.assertEqual(
                load_campaigns(csv_path),
                [
                    {"campaign_id": "A01", "campaign_name": "검색, 브랜드 광고", "cost": "12000", "conversions": "3"},
                    {"campaign_id": "A02", "campaign_name": "배너 광고", "cost": "8000", "conversions": "0"},
                ],
            )


if __name__ == "__main__":
    unittest.main()
