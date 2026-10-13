# 광고 성과 점검 도구

CSV 광고 데이터를 읽고, 값이 유효한지 확인한 뒤 비용이 발생했지만 전환이 없는 광고를 찾는 실습 프로젝트입니다.

## 설치

Python 3.10 이상과 PostgreSQL 서버가 필요합니다.

```powershell
python -m pip install -r requirements.txt
```

## 실행

```powershell
python demo.py
python -m uvicorn api:app --reload
```

API 실행 후 `http://127.0.0.1:8000/campaigns/report`에서 결과를 확인할 수 있습니다. 현재 API는 CSV를 읽습니다.

## PostgreSQL에 CSV 저장

접속 가능한 데이터베이스의 주소를 `DATABASE_URL` 환경 변수에 넣은 뒤 실행합니다.

```powershell
$env:DATABASE_URL = "postgresql://사용자:비밀번호@localhost:5432/campaign_study"
python import_csv.py
```

같은 광고 ID를 다시 저장하면 기존 행의 이름, 비용, 전환 수가 갱신됩니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
```
