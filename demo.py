from pathlib import Path

from campaigns import find_spend_without_conversions, load_campaigns, parse_campaigns


if __name__ == "__main__":
    csv_path = Path(__file__).parent / "data" / "campaigns.csv"
    raw_rows = load_campaigns(csv_path)
    campaigns = parse_campaigns(raw_rows)

    total_cost = 0
    for campaign in campaigns:
        total_cost += campaign.cost

    flagged = find_spend_without_conversions(campaigns)

    print("총 광고비:", total_cost, "원")
    print("점검 대상:", len(flagged), "건")
    for campaign in flagged:
        print(campaign.campaign_id, campaign.campaign_name, "비용:", campaign.cost, "전환:", campaign.conversions)
