# 광고 성과 점검 도구

CSV 광고 데이터를 읽고, 값이 유효한지 확인한 뒤 비용이 발생했지만 전환이 없는 광고를 찾는 실습 프로젝트입니다.

## 실행

Python 3.10 이상에서 실행합니다. 현재 단계에는 외부 패키지가 필요하지 않습니다.

```powershell
python demo.py
python -m unittest discover -s tests -v
```

현재 예시 데이터의 결과는 총 광고비 20,000원, 점검 대상 A02 배너 광고 1건입니다.

## 파일

- `data/campaigns.csv`: 예시 광고 데이터
- `campaigns.py`: CSV 읽기, 값 검증, 점검 규칙
- `demo.py`: 현재 기능 실행
- `tests/test_campaigns.py`: 데이터 처리 테스트

다음 구현 단계는 FastAPI에서 현재 점검 결과를 조회할 수 있게 만드는 것입니다.
