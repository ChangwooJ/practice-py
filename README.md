# 광고 데이터 실습: CSV 읽기와 비용 한 칸 변환

1단계의 목표는 `data/campaigns.csv`를 읽어 각 광고를 **열 이름으로 찾을 수 있는 딕셔너리**로 만드는 것이다. 숫자 변환과 데이터 검증은 아직 하지 않는다.

## 먼저 데이터 보기

`data/campaigns.csv`의 첫 줄은 데이터가 아니라 **헤더**다.

```csv
campaign_id,campaign_name,cost,conversions
A01,검색 광고,12000,3
A02,배너 광고,8000,0
```

쉼표는 열을 구분한다. 따라서 두 번째 줄은 `campaign_id=A01`, `campaign_name=검색 광고`, `cost=12000`, `conversions=3`이라는 뜻이다.

## `campaigns.py`를 한 줄씩 읽기

```python
import csv
from pathlib import Path


def load_campaigns(file_path: str | Path) -> list[dict[str, str]]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))
```

1. **`import csv`**: Python에 기본으로 포함된 CSV 처리 도구를 가져온다. 쉼표와 따옴표 규칙을 직접 구현할 필요가 없다.
2. **`from pathlib import Path`**: 파일 경로를 다루는 `Path`를 가져온다. 예를 들어 `Path("data/campaigns.csv")`는 파일 경로 객체다.
3. **`def load_campaigns(...)`**: 함수를 정의한다. `def`는 “이 이름으로 코드를 묶겠다”는 뜻이다. 함수를 정의하는 것만으로 CSV가 바로 읽히지는 않는다. `demo.py`에서 호출할 때 실행된다.
4. **`file_path: str | Path`**: 함수가 문자열 경로나 `Path` 객체를 받는다는 *타입 힌트*다. `|`는 “또는”이라는 뜻이다. 타입 힌트만으로 실행 중 입력을 자동 검사하지는 않는다.
5. **`-> list[dict[str, str]]`**: 반환할 값의 형태를 알려준다. 바깥의 `list`는 광고 여러 건, 안쪽의 `dict`는 광고 한 건이다. 딕셔너리의 키와 값은 모두 문자열이다.
6. **`path = Path(file_path)`**: 받은 경로를 `Path` 객체로 맞춘다. 그래서 뒤에서 `.open()`을 같은 방식으로 호출할 수 있다.
7. **`with path.open("r", encoding="utf-8", newline="") as file:`**: 파일을 읽기 모드(`"r"`)로 연다. `encoding="utf-8"`은 한글을 포함한 텍스트를 어떤 문자 규칙으로 읽을지 지정한다. `newline=""`는 CSV 모듈이 줄바꿈을 직접 처리하도록 한다. `with` 블록이 끝나면 파일이 닫힌다.
8. **`csv.DictReader(file)`**: 첫 줄을 열 이름으로 읽고, 이후 각 줄을 딕셔너리로 만든다. 예를 들어 첫 광고는 `{"campaign_id": "A01", "cost": "12000", ...}` 형태다.
9. **`list(...)`와 `return`**: `DictReader`의 행들을 목록으로 모으고, 그 목록을 함수를 호출한 곳에 돌려준다. `return`이 실행되면 함수의 일이 끝난다.

**주의:** `"12000"`과 `"3"`은 아직 문자열이다. 화면에는 숫자처럼 보여도 지금은 더하거나 나눌 값으로 준비되지 않았다.

## `demo.py`는 함수를 어떻게 사용하나?

`Path(__file__).parent`는 현재 `demo.py`가 있는 폴더다. 여기에 `data`와 `campaigns.csv`를 이어 붙여 파일 위치를 만든다. `load_campaigns(csv_path)`가 파일을 읽으면, `for campaign in campaigns:`가 목록에서 광고를 하나씩 꺼내 `print`한다.

`if __name__ == "__main__":`은 `python demo.py`처럼 이 파일을 직접 실행할 때만 아래 코드를 실행하겠다는 뜻이다. 다른 파일에서 `demo.py`를 가져오기만 할 때는 실행하지 않는다.

## 직접 확인하기

프로젝트 폴더 `C:\SSAFY\practice-py`에서 다음 명령을 실행한다. 외부 패키지는 필요 없다.

```powershell
python demo.py
python -m unittest discover -s tests -v
```

첫 명령은 광고 딕셔너리 두 건을 출력한다. 두 번째 명령은 이름에 쉼표가 들어가도 CSV가 올바르게 읽히는지 확인한다.

## 실제 프로젝트와 연결

[Langflow의 실제 CSV 처리 함수](https://github.com/langflow-ai/langflow/blob/504c02fc47e76087b82b0e7cbe4186e9cdd916d4/src/lfx/src/lfx/components/data_source/csv_to_data.py#L50-L109)에서도 `csv.DictReader`를 사용한다. 그 코드는 파일과 문자열 등 여러 입력을 지원하므로 더 길다. 지금은 `DictReader`가 헤더와 행을 연결하는 부분만 비교하면 충분하다. 이 저장소의 `load_campaigns`는 학습용으로 작성한 코드다.

## 2단계: `cost` 한 칸만 정수로 바꾸기

CSV 읽기 함수 `load_campaigns`는 그대로 둔다. 이번에는 `demo.py`에서 **첫 광고의 비용 한 칸만** 변환한다.

```python
first_campaign = campaigns[0]
raw_cost = first_campaign["cost"]
cost = int(raw_cost)

print("변환 전:", raw_cost, type(raw_cost).__name__)
print("변환 후:", cost, type(cost).__name__)
print("원본 딕셔너리:", first_campaign)
```

1. `campaigns`는 광고 딕셔너리들이 들어 있는 목록이다. `campaigns[0]`은 **첫 번째** 광고를 꺼낸다. Python의 목록 인덱스는 0부터 시작한다.
2. `first_campaign["cost"]`는 첫 광고 딕셔너리에서 `cost`라는 키의 값을 가져온다. CSV에서 읽었으므로 이 값은 문자열 `"12000"`이다.
3. `int(raw_cost)`는 문자열을 정수로 변환한 **새 값**을 만든다. `cost`에는 정수 `12000`이 저장된다.
4. `type(...).__name__`은 자료형 이름을 보여준다. 실행 결과에서 변환 전은 `str`, 변환 후는 `int`다.
5. 마지막 출력의 원본 딕셔너리에는 여전히 `"cost": "12000"`이 들어 있다. `int(raw_cost)`는 원본 딕셔너리를 자동으로 수정하지 않는다.

예상 출력의 핵심은 다음과 같다.

```text
변환 전: 12000 str
변환 후: 12000 int
```

겉으로는 똑같이 `12000`으로 보이지만 자료형이 다르다. `"12000" + "1000"`은 문자열을 이어 `"120001000"`을 만들고, `12000 + 1000`은 숫자를 더해 `13000`을 만든다.

**이번 단계의 범위:** 숫자로 바꿀 수 없는 값에 대한 오류 처리나 모든 광고의 일괄 변환은 아직 추가하지 않았다. 지금은 `int()`가 무엇을 반환하는지 확인하는 데 집중한다.


### 공개 프로젝트에서는 어떻게 쓰나?

[Princeton NLP의 공개 데이터 로더](https://github.com/princeton-nlp/CoFiPruning/blob/main/glue.py#L2512-L2526)는 `csv.DictReader`로 읽은 행에서 `row["Quality"]`를 꺼내 `int(...)`로 변환한다. 우리 코드의 `int(first_campaign["cost"])`와 같은 기본 패턴이다. 이 링크는 실제 저장소의 코드이며, `demo.py`의 변수 이름과 출력 부분은 학습을 위해 별도로 작성했다.


## 3단계: 모든 광고의 비용 더하기

`demo.py`에 다음 부분을 추가했다.

```python
total_cost = 0
for campaign in campaigns:
    campaign_cost = int(campaign["cost"])
    total_cost += campaign_cost
    print(campaign["campaign_name"], "비용:", campaign_cost)

print("총비용:", total_cost)
```

1. `total_cost = 0`: 합계를 담을 변수를 0에서 시작한다. 이런 변수를 **누산기**라고 부른다.
2. `for campaign in campaigns:`: 광고 목록에서 항목을 하나씩 꺼낸다. 첫 반복의 `campaign`은 A01, 두 번째는 A02다.
3. `campaign["cost"]`: 현재 광고의 비용을 문자열로 꺼낸다. 첫 번째는 `"12000"`, 두 번째는 `"8000"`이다.
4. `int(...)`: 문자열을 정수로 변환한다. 비용을 더하기 전에 필요한 단계다.
5. `total_cost += campaign_cost`: 현재 비용을 기존 합계에 더한다. `total_cost = total_cost + campaign_cost`와 같다.
6. 들여쓰기된 `print(...)`는 광고마다 한 번씩 실행된다. 들여쓰기 밖의 마지막 `print(...)`는 반복이 끝난 뒤 한 번만 실행된다.

합계는 `0 → 12000 → 20000`으로 변한다. CSV 원본의 비용은 여전히 문자열이며, 이 예시는 계산할 때만 정수로 바꾼다.

직접 확인할 때는 `python demo.py`를 실행한다. 현재 CSV의 총비용은 `20000`이어야 한다.
