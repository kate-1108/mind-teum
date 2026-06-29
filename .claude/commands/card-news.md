# /card-news

주제 또는 URL을 받아 Mind.teum 브랜드 카드뉴스 HTML을 생성합니다.

## 입력 형식

```
/card-news [주제 또는 URL]
```

예시:
- `/card-news 오늘 하루도 수고했어`
- `/card-news 자기 자신을 사랑하는 법`
- `/card-news https://...`  (URL이면 내용을 먼저 읽어서 요약)

## 작업 순서

1. **컨텍스트 로드**
   - `knowledge/color-system.md` — 버전별 컬러 토큰
   - `knowledge/design-guide.md` — 레이아웃·타이포·슬라이드 구성
   - `templates/card-base.html` — 기본 카드 구조

2. **버전 자동 선택** (주제 분석 후 결정)
   | 주제 | 버전 |
   |------|------|
   | 긍정·성장·동기 | A — Pure Cream |
   | 맑은 감성·산뜻 | B — Cloud White |
   | 따뜻한 공감·일상 | C — Rice Paper |
   | 위로·감성·새벽 | D — Deep Navy 골드 |
   | 성찰·회복 | E — Deep Navy 실버 |

3. **슬라이드 구성 결정**
   - 구조: 커버 1장 + 본문 N장 + CTA 1장
   - 분량: 주제 깊이에 따라 3~8장 (최대 10장)
   - 패턴 선택: design-guide.md의 패턴 A·B·C 참조

4. **문구 작성** (CLAUDE.md 어체 규칙 준수)
   - 해요체·해체 혼용 (`~해요`, `~해`, `~거야`, `~잖아`)
   - 짧은 문장 + 줄바꿈으로 여운
   - 마침표 최소화
   - 이모지 없음
   - 한 줄 최대 13자, 본문 3~5줄

5. **HTML 생성**
   - `templates/card-base.html` 구조를 기반으로
   - 슬라이드 수만큼 개별 HTML 파일 생성
   - 파일명: `output/card-[주제약어]-[번호].html`
     예: `output/card-rest-01.html`, `output/card-rest-02.html`
   - 각 파일은 독립 실행 가능한 완전한 HTML

6. **결과 보고**
   - 생성된 파일 목록
   - 선택된 버전 및 이유
   - PNG 변환 안내: `/card-news-export` 실행

## 카드 HTML 구조 (각 파일)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <!-- card-base.html의 style 블록 전체 복사 -->
</head>
<body>
<div class="card version-[a~e]">
  <span class="card-tag">— 오늘의 마음 —</span>
  <div class="card-body">
    문구 첫 번째 줄<br>
    문구 두 번째 줄<br>
    ...
  </div>
  <span class="card-handle">— @mind.teum —</span>
</div>
</body>
</html>
```

## 주의사항

- 폰트 경로는 항상 `../fonts/` 상대경로 유지
- 이모지 절대 사용 금지
- 텍스트가 카드 60% 이하를 차지하도록 줄 수 조절
- 강조가 필요하면 `.point` 클래스로 포인트 컬러 적용
