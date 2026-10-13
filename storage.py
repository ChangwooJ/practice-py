import psycopg

from campaigns import Campaign


def create_campaign_table(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                campaign_id TEXT PRIMARY KEY,
                campaign_name TEXT NOT NULL,
                cost INTEGER NOT NULL CHECK (cost >= 0),
                conversions INTEGER NOT NULL CHECK (conversions >= 0)
            )
            """
        )


def save_campaigns(dsn: str, campaigns: list[Campaign]) -> None:
    rows = [
        (campaign.campaign_id, campaign.campaign_name, campaign.cost, campaign.conversions)
        for campaign in campaigns
    ]
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO campaigns (campaign_id, campaign_name, cost, conversions)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (campaign_id) DO UPDATE SET
                    campaign_name = EXCLUDED.campaign_name,
                    cost = EXCLUDED.cost,
                    conversions = EXCLUDED.conversions
                """,
                rows,
            )


def load_campaigns_from_db(dsn: str) -> list[Campaign]:
    with psycopg.connect(dsn) as connection:
        rows = connection.execute(
            "SELECT campaign_id, campaign_name, cost, conversions FROM campaigns ORDER BY campaign_id"
        ).fetchall()
    return [Campaign(row[0], row[1], row[2], row[3]) for row in rows]
