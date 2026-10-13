# 데이터 처리 코드 자세히 읽기

이 문서는 `campaigns.py`의 현재 구현을 읽기 위한 설명이다. 실행 흐름은 `load_campaigns` → `parse_campaigns` → `find_spend_without_conversions` 순서다.

## 1. CSV를 읽은 직후의 값

`load_campaigns`가 첫 데이터 행을 읽으면 대략 다음 딕셔너리가 나온다.

```python
{
    "campaign_id": "A01",
    "campaign_name": "검색 광고",
    "cost": "12000",
    "conversions": "3",
}
```

`"12000"`과 `"3"`은 **문자열**이다. `parse_campaigns`는 이 행을 검사하고 계산 가능한 광고 객체로 바꾼다.

## 2. `Campaign`은 어떤 객체인가?

```python
@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    campaign_name: str
    cost: int
    conversions: int
```

- `class Campaign:`은 광고 한 건의 형태를 정의한다.
- `@dataclass`는 필드 값을 받아 객체를 만드는 `__init__` 등을 자동으로 만들어 준다. 그래서 아래처럼 생성할 수 있다.
- `frozen=True`는 만든 후 `campaign.cost = 5000`처럼 필드를 다시 대입하지 못하게 한다.
- `cost: int`는 타입 힌트다. **이 힌트나 `frozen=True`가 문자열을 정수로 자동 변환하거나 잘못된 입력을 검사하지는 않는다.** 그 일은 아래의 검증 함수가 맡는다.

```python
campaign = Campaign(campaign_id="A01", campaign_name="검색 광고", cost=12000, conversions=3)
```

`campaign_id=` 같은 표기는 **키워드 인자**다. 어느 값이 어느 필드에 들어가는지 이름으로 명시한다. 만든 객체에서는 `campaign.cost`처럼 점(`.`)으로 필드에 접근한다. 원래 CSV 행은 딕셔너리이므로 `row["cost"]`처럼 대괄호로 접근한다.

## 3. `_required_text`: 값이 있는지 확인하기

```python
def _required_text(row: dict[str, str], field: str, row_number: int) -> str:
    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"{row_number}행 {field}: 값이 필요합니다")
    return value.strip()
```

- 이름 앞의 `_`는 **이 파일 내부에서 쓰는 보조 함수**라는 관례다. Python이 호출을 금지하는 기능은 아니다.
- `row.get(field)`는 딕셔너리에서 `field`라는 키의 값을 찾는다. 키가 없으면 `None`을 돌려준다. `row[field]`를 썼다면 없는 키에서 `KeyError`가 난다.
- `value is None`은 값이 아예 없는지 확인한다. 여기서 `is`는 `None`이라는 특별한 객체와의 동일성 검사에 쓴다.
- `value.strip()`은 문자열 양끝의 공백을 제거한 **새 문자열**을 돌려준다. `"  검색 광고  ".strip()`은 `"검색 광고"`, `"   ".strip()`은 `""`이다.
- `not value.strip()`은 공백을 제거한 결과가 빈 문자열인지 확인한다. 빈 문자열은 조건식에서 거짓으로 취급된다.
- `or`는 앞 조건이 참이면 뒤 조건을 실행하지 않는다. 따라서 `value`가 `None`일 때 `.strip()`을 호출하지 않아 오류를 피한다.
- `raise ValueError(...)`는 잘못된 데이터를 만났다고 호출자에게 알린다. `f"..."`는 변수 값을 문자열에 끼워 넣는 **f-string**이다. 예를 들어 `row_number=2`, `field="campaign_name"`이면 `2행 campaign_name: 값이 필요합니다`가 된다.
- 정상 값이면 `return value.strip()`으로 양끝 공백을 제거한 문자열을 돌려준다.

## 4. `_nonnegative_int`: 숫자 형식과 범위 확인하기

```python
def _nonnegative_int(row: dict[str, str], field: str, row_number: int) -> int:
    value = _required_text(row, field, row_number)
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{row_number}행 {field}: 0 이상의 정수가 필요합니다") from exc
    if number < 0:
        raise ValueError(f"{row_number}행 {field}: 0 이상의 정수가 필요합니다")
    return number
```

1. 먼저 `_required_text(...)`를 호출한다. 값이 없거나 공백뿐이면 여기에서 멈추고 오류를 낸다.
2. `int(value)`가 `"12000"`을 정수 `12000`으로 바꾼다. `"three"`처럼 바꿀 수 없는 값이면 `ValueError`가 발생한다.
3. `try`는 오류가 날 수 있는 변환을 시도하고, `except ValueError as exc`는 그 오류를 `exc`라는 이름으로 받는다.
4. `raise ... from exc`는 CSV 행·열을 포함한 새 오류를 만들면서 **원래 변환 오류도 원인으로 남긴다.** 로그를 볼 때 원인을 추적할 수 있다.
5. 정수로 변환됐어도 음수라면 `number < 0`에서 거부한다. 광고비와 전환 수는 이번 실습에서 0 이상이어야 한다고 정했다.
6. 통과하면 `return number`로 정수를 돌려준다.

## 5. `parse_campaigns`: 검증한 값으로 객체 만들기

```python
def parse_campaigns(rows: list[dict[str, str]]) -> list[Campaign]:
    campaigns = []
    for row_number, row in enumerate(rows, start=2):
        campaigns.append(
            Campaign(
                campaign_id=_required_text(row, "campaign_id", row_number),
                campaign_name=_required_text(row, "campaign_name", row_number),
                cost=_nonnegative_int(row, "cost", row_number),
                conversions=_nonnegative_int(row, "conversions", row_number),
            )
        )
    return campaigns
```

- `rows: list[dict[str, str]]`는 CSV 행 딕셔너리들의 목록을 받는다는 타입 힌트다. `-> list[Campaign]`는 결과가 `Campaign` 객체들의 목록이라는 뜻이다.
- `campaigns = []`는 결과를 담을 빈 목록을 만든다.
- `enumerate(rows, start=2)`는 각 행과 번호를 함께 돌려준다. `start=2`는 CSV 1행이 헤더이기 때문에 첫 **데이터**를 2행으로 표시하기 위한 키워드 인자다.
- `for row_number, row in ...`는 번호와 실제 행을 각각 변수에 담는다. 첫 번째 반복에서는 `row_number`가 `2`, `row`가 A01 딕셔너리다.
- `Campaign(...)`의 네 인자는 **객체를 만들기 전에** 각각 계산된다. 문자열 필드는 `_required_text`, 숫자 필드는 `_nonnegative_int`가 검증한다. 어느 하나라도 오류를 내면 객체 생성과 `append`는 실행되지 않는다.
- `campaigns.append(...)`는 완성된 객체를 결과 목록의 맨 뒤에 넣는다. 첫 번째 반복 후에는 A01 객체 한 개, 두 번째 반복 후에는 A01과 A02 객체 두 개가 들어 있다.
- 모든 행이 끝나면 `return campaigns`가 완성된 목록을 돌려준다.

첫 번째 행의 흐름을 값으로 적으면 다음과 같다.

```text
"A01" → _required_text → "A01" ┐
"검색 광고" → _required_text → "검색 광고" ├→ Campaign("A01", "검색 광고", 12000, 3)
"12000" → _nonnegative_int → 12000 ┤
"3" → _nonnegative_int → 3 ┘
```

## 6. `load_campaigns`와 점검 규칙에서 새로 나온 문법

`load_campaigns`의 `reader.fieldnames`는 CSV 헤더의 열 이름 목록이다. `reader.fieldnames or []`는 헤더가 없어서 값이 `None`이면 빈 목록을 대신 사용한다. `set(...)`은 열 이름을 집합으로 만들고, `required_columns - set(...)`은 **필수 열 중 실제 헤더에 없는 것**을 찾는다. `sorted(...)`는 빠진 열 이름의 출력 순서를 고정하고, `", ".join(...)`은 여러 이름을 쉼표로 연결한다. `if missing_columns:`는 빠진 열이 하나라도 있는지 확인한다.

```python
if campaign.cost > 0 and campaign.conversions == 0:
    flagged.append(campaign)
```

`and`는 두 조건이 **모두 참**일 때만 참이다. 따라서 비용 8,000원·전환 0건인 A02는 추가되고, 비용 0원·전환 0건인 광고는 추가되지 않는다. `flagged.append(campaign)`은 조건에 맞는 기존 `Campaign` 객체를 결과 목록에 넣는다.
