# 광고 성과 점검 도구

CSV 광고 데이터를 읽고, 값이 유효한지 확인한 뒤 비용이 발생했지만 전환이 없는 광고를 찾는 실습 프로젝트입니다.

## 설치

Python 3.10 이상이 필요합니다.

```powershell
python -m pip install -r requirements.txt
```

## 실행

```powershell
python demo.py
python -m uvicorn api:app --reload
```

API 실행 후 `http://127.0.0.1:8000/campaigns/report`에서 결과를 확인할 수 있습니다.

## 테스트

```powershell
python -m unittest discover -s tests -v
```
