import json
import os
import unittest
from unittest.mock import patch

import httpx
import psycopg
from fastapi.testclient import TestClient
from openai import OpenAI

from api import app
from campaigns import Campaign


def tool_response(name="get_campaign_report", arguments="{}"):
    return {
        "id": "resp_tool", "object": "response", "created_at": 0,
        "status": "completed", "model": "gpt-5-mini",
        "output": [{
            "type": "function_call", "id": "fc_report", "call_id": "call_report",
            "name": name, "arguments": arguments, "status": "completed",
        }],
    }


def text_response(text="D02 배너 광고는 비용 500원, 전환 0건으로 점검 대상입니다."):
    return {
        "id": "resp_answer", "object": "response", "created_at": 0,
        "status": "completed", "model": "gpt-5-mini",
        "output": [{
            "type": "message", "id": "msg_answer", "role": "assistant", "status": "completed",
            "content": [{"type": "output_text", "text": text, "annotations": []}],
        }],
    }


class CampaignAssistantApiTests(unittest.TestCase):
    def setUp(self):
        env_patch = patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://example.invalid/campaigns",
            "OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-5-mini",
        })
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def ask_with_responses(self, responses, database_error=None):
        requests = []

        def handle(request):
            requests.append(json.loads(request.content))
            self.assertLessEqual(len(requests), len(responses), "예상보다 많은 모델 호출")
            return responses[len(requests) - 1]

        campaigns = [Campaign("D01", "검색 광고", 200, 2), Campaign("D02", "배너 광고", 500, 0)]
        with OpenAI(api_key="test-key", http_client=httpx.Client(transport=httpx.MockTransport(handle)), max_retries=0) as model_client:
            with patch("openai.OpenAI", return_value=model_client):
                with patch("storage.load_campaigns_from_db", return_value=campaigns, side_effect=database_error):
                    response = TestClient(app).post("/campaigns/ask", json={"question": "전환 없는 광고 알려줘"})
        return response, requests

    def test_returns_answer_and_passes_actual_report_back_to_model(self):
        response, requests = self.ask_with_responses([
            httpx.Response(200, json=tool_response()), httpx.Response(200, json=text_response()),
        ])
        self.assertEqual(response.status_code, 200)
        expected_report = {
            "total_cost": 700, "flagged_count": 1,
            "flagged_campaigns": [{"campaign_id": "D02", "campaign_name": "배너 광고", "cost": 500, "conversions": 0}],
        }
        self.assertEqual(response.json(), {"answer": text_response()["output"][0]["content"][0]["text"], "report": expected_report})
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]["input"], [{"role": "user", "content": "전환 없는 광고 알려줘"}])
        self.assertEqual(requests[1]["previous_response_id"], "resp_tool")
        tool_output = requests[1]["input"][0]
        self.assertEqual(tool_output["type"], "function_call_output")
        self.assertEqual(tool_output["call_id"], "call_report")
        self.assertEqual(json.loads(tool_output["output"]), expected_report)

    def test_rejects_invalid_questions_before_calling_model(self):
        for payload in ({}, {"question": ""}, {"question": "   "}, {"question": 12}, {"question": "가" * 1001}):
            with self.subTest(payload=payload):
                with patch("openai.OpenAI", side_effect=AssertionError("검증 전에 모델 호출")):
                    response = TestClient(app).post("/campaigns/ask", json=payload)
                self.assertEqual(response.status_code, 422)

    def test_requires_api_key_and_database_settings(self):
        for setting in ("OPENAI_API_KEY", "DATABASE_URL"):
            with self.subTest(setting=setting), patch.dict(os.environ):
                os.environ.pop(setting, None)
                with patch("openai.OpenAI", side_effect=AssertionError("설정 확인 전에 모델 호출")):
                    response = TestClient(app).post("/campaigns/ask", json={"question": "점검해줘"})
                self.assertEqual(response.status_code, 503)

    def test_rejects_unknown_tools_and_invalid_arguments(self):
        for output in (tool_response("delete_campaigns"), tool_response(arguments="not-json"), tool_response(arguments='{"sql": "DROP TABLE campaigns"}'), text_response()):
            with self.subTest(output=output):
                response, requests = self.ask_with_responses([httpx.Response(200, json=output)], database_error=AssertionError("잘못된 도구로 DB 접근"))
                self.assertEqual(response.status_code, 502)
                self.assertEqual(len(requests), 1)

    def test_maps_model_service_errors_without_exposing_details(self):
        response, _ = self.ask_with_responses([
            httpx.Response(429, json={"error": {"message": "private-provider-details", "type": "rate_limit_error", "code": "rate_limit_exceeded"}}),
        ])
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private-provider-details", response.text)

    def test_maps_database_failure_without_second_model_call(self):
        response, requests = self.ask_with_responses([
            httpx.Response(200, json=tool_response()),
        ], database_error=psycopg.OperationalError("private-db-details"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(requests), 1)
        self.assertNotIn("private-db-details", response.text)

    def test_rejects_empty_or_incomplete_final_answer(self):
        incomplete = text_response("부분 답변")
        incomplete["status"] = "incomplete"
        for output in (text_response("   "), incomplete):
            with self.subTest(output=output):
                response, _ = self.ask_with_responses([
                    httpx.Response(200, json=tool_response()), httpx.Response(200, json=output),
                ])
                self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
