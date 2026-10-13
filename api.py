from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI

from campaigns import find_spend_without_conversions, load_campaigns, parse_campaigns


app = FastAPI()
DATA_PATH = Path(__file__).parent / "data" / "campaigns.csv"


@app.get("/campaigns/report")
def get_campaign_report():
    campaigns = parse_campaigns(load_campaigns(DATA_PATH))
    flagged = find_spend_without_conversions(campaigns)

    return {
        "total_cost": sum(campaign.cost for campaign in campaigns),
        "flagged_count": len(flagged),
        "flagged_campaigns": [asdict(campaign) for campaign in flagged],
    }
