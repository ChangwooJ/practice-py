from pathlib import Path

from campaigns import load_campaigns


if __name__ == "__main__":
    csv_path = Path(__file__).parent / "data" / "campaigns.csv"
    campaigns = load_campaigns(csv_path)

    first_campaign = campaigns[0]
    raw_cost = first_campaign["cost"]
    cost = int(raw_cost)

    print("변환 전:", raw_cost, type(raw_cost).__name__)
    print("변환 후:", cost, type(cost).__name__)
    print("원본 딕셔너리:", first_campaign)

    total_cost = 0
    for campaign in campaigns:
        campaign_cost = int(campaign["cost"])
        total_cost += campaign_cost
        print(campaign["campaign_name"], "비용:", campaign_cost)

    print("총비용:", total_cost)
