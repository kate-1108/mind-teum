# /card-news-export

`output/` 폴더의 HTML 카드를 PNG로 일괄 변환합니다.

## 입력 형식

```
/card-news-export              # output/ 전체 HTML 일괄 변환
/card-news-export [파일명...]  # 특정 파일만 변환
```

예시:
- `/card-news-export`
- `/card-news-export output/card-rest-01.html output/card-rest-02.html`

## 작업 순서

1. 변환 대상 결정
   - 인수 없으면: `output/*.html` 전체
   - 인수 있으면: 지정된 파일만

2. `scripts/export.py` 실행

   ```bash
   # 전체 일괄
   python scripts/export.py --all

   # 특정 파일
   python scripts/export.py output/card-rest-01.html output/card-rest-02.html
   ```

3. 결과 보고
   - 생성된 PNG 파일 목록
   - 저장 경로: `output/[파일명].png`
   - 크기: 1080 × 1350px

## 주의사항

- Playwright가 설치되어 있어야 함 (`pip install playwright && python -m playwright install chromium`)
- PNG는 HTML과 같은 이름으로 `output/` 폴더에 저장됨
- 기존 PNG가 있으면 덮어씀
