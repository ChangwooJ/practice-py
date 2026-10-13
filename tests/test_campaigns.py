import tempfile
import unittest
from pathlib import Path

from campaigns import Campaign, find_spend_without_conversions, load_campaigns, parse_campaigns


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

    def test_rejects_missing_header_even_without_data_rows(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            csv_path = Path(directory) / "campaigns.csv"
            csv_path.write_text("campaign_id,campaign_name,cost\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "conversions"):
                load_campaigns(csv_path)


class ParseCampaignsTests(unittest.TestCase):
    def test_converts_csv_numbers_into_campaigns(self):
        rows = [{"campaign_id": "A01", "campaign_name": "검색 광고", "cost": "12000", "conversions": "3"}]

        self.assertEqual(
            parse_campaigns(rows),
            [Campaign(campaign_id="A01", campaign_name="검색 광고", cost=12000, conversions=3)],
        )

    def test_rejects_invalid_numbers_with_row_and_field(self):
        cases = [
            ("", "3", "cost"),
            ("unknown", "3", "cost"),
            ("-1", "3", "cost"),
            ("12000", "", "conversions"),
            ("12000", "three", "conversions"),
        ]
        for cost, conversions, field in cases:
            with self.subTest(cost=cost, conversions=conversions):
                rows = [{"campaign_id": "A01", "campaign_name": "검색 광고", "cost": cost, "conversions": conversions}]
                with self.assertRaisesRegex(ValueError, f"2행.*{field}"):
                    parse_campaigns(rows)

    def test_rejects_missing_name_with_row_and_field(self):
        rows = [{"campaign_id": "A01", "campaign_name": "", "cost": "12000", "conversions": "3"}]

        with self.assertRaisesRegex(ValueError, "2행.*campaign_name"):
            parse_campaigns(rows)


class CampaignCheckTests(unittest.TestCase):
    def test_finds_only_campaigns_with_spend_and_no_conversions(self):
        campaigns = [
            Campaign("A01", "검색 광고", 12000, 3),
            Campaign("A02", "배너 광고", 8000, 0),
            Campaign("A03", "무료 광고", 0, 0),
        ]

        self.assertEqual(find_spend_without_conversions(campaigns), [campaigns[1]])


if __name__ == "__main__":
    unittest.main()
