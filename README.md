# 광고 성과 점검 도구

PostgreSQL의 광고 점검 결과를 JSON 또는 자연어 답변으로 조회합니다.

## 설치

Python 3.10 이상과 접속 가능한 PostgreSQL 데이터베이스가 필요합니다.

```powershell
python -m pip install -r requirements.txt
```

## 실행

DB를 미리 만든 뒤 같은 PowerShell 창에서 실제 접속 주소를 설정합니다.
자연어 API를 사용할 때는 서버 실행 전에 OpenAI API 키도 설정합니다.

```powershell
$env:DATABASE_URL = "postgresql://사용자:비밀번호@localhost:5432/campaign_study"
$env:OPENAI_API_KEY = "발급받은 API 키"
$env:OPENAI_MODEL = "gpt-5-mini"
python import_csv.py
python -m uvicorn api:app --reload
```

`OPENAI_MODEL`은 생략하면 `gpt-5-mini`를 사용합니다.
키를 파일이나 Git에 저장하지 않습니다.

- `GET /campaigns/report`: DB 점검 결과. OpenAI 키가 필요하지 않습니다.
- `POST /campaigns/ask`: 질문에 대한 설명과 근거 보고서. 질문과 보고서가 OpenAI API에 전달됩니다.

`http://127.0.0.1:8000/docs`에서 `POST /campaigns/ask`의 **Try it out**으로 요청할 수 있습니다.

```json
{"question": "비용은 나갔는데 전환이 없는 광고를 알려줘"}
```

CSV 수정 사항은 `python import_csv.py`로 다시 저장해야 API에 반영됩니다.
CSV만 실행하려면 `python demo.py`를 사용합니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
```

OpenAI 응답은 테스트용 HTTP 응답으로 대체하며 실제 모델 호출은 하지 않습니다.
DB 통합 테스트까지 실행하려면 스키마 생성 권한이 있는 테스트 DB를 설정합니다.

```powershell
$env:TEST_DATABASE_URL = "postgresql://사용자:비밀번호@localhost:5432/campaign_study_test"
python -m unittest discover -s tests -v
```
