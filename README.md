# 광고 성과 점검 도구

PostgreSQL에 저장한 광고 데이터에서 비용이 발생했지만 전환이 없는 광고를 조회합니다.

## 설치

Python 3.10 이상과 접속 가능한 PostgreSQL 데이터베이스가 필요합니다.

```powershell
python -m pip install -r requirements.txt
```

## API 실행

접속할 데이터베이스를 미리 만든 뒤, 같은 PowerShell 창에서 다음 순서로 실행합니다. 주소의 사용자·비밀번호·DB 이름을 실제 값으로 바꿉니다.

```powershell
$env:DATABASE_URL = "postgresql://사용자:비밀번호@localhost:5432/campaign_study"
python import_csv.py
python -m uvicorn api:app --reload
```

`http://127.0.0.1:8000/campaigns/report`에서 결과를 확인합니다.
CSV를 수정했다면 `python import_csv.py`를 다시 실행해야 DB와 API 결과에 반영됩니다.
DB 설정이 없거나 조회할 수 없으면 API가 503을 반환합니다.

## CSV 단독 실행

```powershell
python demo.py
```

## 테스트

```powershell
python -m unittest discover -s tests -v
```

DB 통합 테스트까지 실행하려면 별도 테스트용 DB 주소를 설정합니다. API 통합 테스트에는 스키마 생성 권한이 필요합니다.

```powershell
$env:TEST_DATABASE_URL = "postgresql://사용자:비밀번호@localhost:5432/campaign_study_test"
python -m unittest discover -s tests -v
```
