import os
from dataclasses import asdict

import psycopg
from fastapi import FastAPI, HTTPException

import storage
from campaigns import find_spend_without_conversions


app = FastAPI()


@app.get("/campaigns/report")
def get_campaign_report():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 설정이 필요합니다")

    try:
        campaigns = storage.load_campaigns_from_db(database_url)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="광고 데이터를 조회할 수 없습니다") from exc

    flagged = find_spend_without_conversions(campaigns)

    return {
        "total_cost": sum(campaign.cost for campaign in campaigns),
        "flagged_count": len(flagged),
        "flagged_campaigns": [asdict(campaign) for campaign in flagged],
    }
