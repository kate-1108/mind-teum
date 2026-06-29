# Mind.teum 카드뉴스 자동생성 프로젝트

## 프로젝트 개요
Mind.teum (@mind.teum) 인스타그램 카드뉴스를 자동으로 생성하는 시스템이에요.
Notion에서 콘텐츠를 불러오고, HTML/CSS로 카드를 렌더링한 뒤, Playwright로 PNG로 캡처해요.

## 폴더 구조
```
E:\projects\mind-teum\
├── CLAUDE.md              ← 이 파일 (프로젝트 안내서)
├── fonts\                 ← 로컬 폰트 파일
│   ├── 강원교육새음.ttf    ← 본문용 (긍정·성장 주제)
│   ├── KNPSKkomi.otf      ← 본문용 (위로·감성 주제)
│   └── SUIT-Light.ttf     ← 태그·핸들용 (공통)
├── knowledge\             ← 브랜드 참조 문서
│   └── color-system.md    ← 컬러 시스템 (5가지 버전)
├── templates\             ← HTML 카드 템플릿
│   └── card-base.html     ← 기본 카드 템플릿
├── scripts\               ← 실행 스크립트
│   └── export.py          ← Playwright PNG 캡처 스크립트
└── output\                ← 생성된 PNG 저장 폴더
```

## 브랜드 정보

### 기본
- 브랜드명: Mind.teum (마인드틈)
- 인스타그램: @mind.teum
- 슬로건: 마음이 쉬어가는 작은 틈
- 타깃: 지친 일상을 보내는 20~40대 남녀

### 어체
- 해요체와 해체 혼용 (`~해요`, `~해`, `~거야`, `~잖아`)
- 친구에게 말하듯 편안하고 따뜻한 톤
- 2인칭 직접 호칭 사용 (`너`, `당신`)
- 짧은 문장 + 줄바꿈으로 호흡감과 여운 조절
- 마침표(`.`) 사용 최소화 — 쉼표(`,`)나 줄바꿈으로 여운 남기기
- 이모지 없음, 텍스트만으로 감성 전달
- 1인칭 내면 서술 + 2인칭 공감 혼합
- 출처/핸들 표기: `— @mind.teum —` 형식

**어체 예시**
```
힘든 시간을
도드리고, 버티고, 해서야
너에게 하루라는
향긋한 일상이 찾아올 거야.

오늘도 그렇게 잘 버텼어,
수고했어.
```

### 카드 구성 요소
- 상단 태그: `— 오늘의 마음 —` 또는 `— 마인드틈 —`
- 본문: 3~5줄 감성 문구
- 하단 핸들: `— @mind.teum —`

## 컬러 시스템
상세 내용은 `knowledge/color-system.md` 참조

### 빠른 참조 — 버전별 선택 가이드
| 콘텐츠 주제 | 버전 | 배경 | 포인트 |
|------------|------|------|--------|
| 긍정·성장·동기 | A Pure Cream | `#fdfcfa` | `#1c2d4a` |
| 맑은 감성 | B Cloud White | `#fafbfc` | `#1c2d4a` |
| 따뜻한 공감 | C Rice Paper | `#fcfbf8` | `#1c2d4a` |
| 위로·감성 (다크) | D Deep Navy 골드 | `#0e1624` | `#c8b888` |
| 성장·성찰 (다크) | E Deep Navy 실버 | `#0e1624` | `#c0c8d4` |

### 공통 컬러
- 본문 텍스트 (라이트): `#221e1a`
- 본문 텍스트 (다크): `#f5f8fc`
- 캡션/핸들 (공통): `#786e62`

## 폰트 시스템
```css
/* 본문 — 긍정·성장 주제 */
@font-face {
  font-family: 'GangwonEdu';
  src: url('../fonts/강원교육새음.ttf') format('truetype');
}

/* 본문 — 위로·감성 주제 */
@font-face {
  font-family: 'Kkomi';
  src: url('../fonts/KNPSKkomi.otf') format('opentype');
}

/* 태그·핸들 공통 */
@font-face {
  font-family: 'SUIT';
  src: url('../fonts/SUIT-Light.ttf') format('truetype');
  font-weight: 300;
}
```

### 폰트 사용 규칙
| 요소 | 폰트 | 굵기 | 크기 |
|------|------|------|------|
| 본문 (긍정·성장) | GangwonEdu | normal | 60px |
| 본문 (위로·감성) | Kkomi | normal | 60px |
| 상단 태그 | SUIT | 300 | 22px |
| 하단 핸들 | SUIT | 300 | 24px |
| 줄간격 | - | - | 2.0 |
| 태그 letter-spacing | - | - | 0.14em |
| 핸들 letter-spacing | - | - | 0.10em |

## 카드 규격
- 크기: 1080 x 1350px (인스타그램 캐러셀 표준, 4:5 비율)
- border-radius: 14px
- border: 0.5px solid (버전별 서피스 컬러)
- 배경 효과: CSS fractalNoise 노이즈 필터 (종이 질감)
- 패딩: 80px (상하), 72px (좌우)

## 작업 흐름

### 카드 생성 요청 형식
```
주제: [콘텐츠 주제]
버전: [A~E 중 선택 또는 자동]
문구: [본문 텍스트] (없으면 자동 생성)
슬라이드 수: [1~10]
```

### 자동화 파이프라인
1. Notion에서 콘텐츠 불러오기 (Notion MCP 사용)
2. 버전 자동 선택 (주제 분석)
3. HTML 카드 생성 (templates/card-base.html 기반)
4. Playwright로 PNG 캡처 (scripts/export.py)
5. output 폴더에 저장

## 주요 명령어

### Playwright 설치 (최초 1회)
```bash
pip install playwright
playwright install chromium
```

### PNG 캡처 실행
```bash
python scripts/export.py --input templates/card.html --output output/card.png
```

## 참고 레퍼런스 계정

### @gamsung_train (감성기차)
- 다크·감성·손글씨 스타일
- 종이 질감 흰 배경 또는 다크 배경
- 캐릭터 일러스트 + 감성 문구 조합
- 해요체·해체 혼용, 줄바꿈으로 호흡감
- 출처 표기: `— 감성열차 —`

### @powerofpositivity
- 라이트·긍정·미니멀 스타일
- 풍경 사진(노을·꽃밭·바다·하늘) 위에 텍스트 오버레이
- 노란 형광 하이라이트로 핵심 문장 강조
- 폰트 믹스: 필기체(본문) + 볼드 산세리프(강조)
- 1카드 1메시지 원칙 철저히 준수
- 독자에게 직접 말 거는 2인칭 문장 (`~한 당신에게`, `~해도 괜찮아`)
