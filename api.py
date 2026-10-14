import os

import openai
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

import campaign_assistant
import storage
from campaigns import build_campaign_report


app = FastAPI()


class QuestionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=1000)


@app.get("/campaigns/report")
def get_campaign_report():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 설정이 필요합니다")

    try:
        campaigns = storage.load_campaigns_from_db(database_url)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="광고 데이터를 조회할 수 없습니다") from exc

    return build_campaign_report(campaigns)


@app.post("/campaigns/ask")
def ask_campaign_question(request: QuestionRequest):
    database_url = os.getenv("DATABASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    if not database_url or not api_key:
        raise HTTPException(status_code=503, detail="데이터베이스와 AI 연결 설정이 필요합니다")

    model = os.getenv("OPENAI_MODEL") or "gpt-5-mini"
    try:
        with openai.OpenAI(api_key=api_key, timeout=60, max_retries=0) as client:
            return campaign_assistant.answer_question(request.question, database_url, client, model)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="광고 데이터를 조회할 수 없습니다") from exc
    except (openai.OpenAIError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="AI 답변을 생성하지 못했습니다") from exc
