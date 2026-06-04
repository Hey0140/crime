# 리팩토링 제안서 — 《죽은 자의 생일파티》

> 작성일: 2026-06-04 · 상태: **Phase 0~5 실행 완료** · 작업 브랜치: `refactor/restructure` · 롤백 태그: `pre-refactor`

이 문서는 레포 구조 정리 계획서이자 실행 기록입니다. 아래 1~9장은 계획 당시 분석이며, **실행 결과는 10장**에 정리되어 있습니다. 결정 사항: 파일명 의미있는 ASCII화 / 예비 리소스·Notion 원본 모두 레포 tracked 보관 / Phase 4(RES 맵)는 인코딩 문제 해소로 생략.

---

## 1. 현재 상태 요약

### 1.1 무엇이 진입점인가
```
index.html  ──(meta refresh + location.replace)──▶  죽은자의_생일파티_게임.html
```
- `index.html`은 4줄짜리 리다이렉트 셸이고, **실제 게임은 `죽은자의_생일파티_게임.html`** (약 237KB) 한 파일에 모든 스토리/방/단서 HTML이 JS 데이터로 **인라인 내장**되어 있다.
- 게임 파일은 자급자족형이라 디스크에서는 **폰트 · 음원 · 이미지만** 로드한다.

### 1.2 폴더 구성과 "초기 버전"의 흔적
```
crime/
├─ index.html                       # 진입점(리다이렉트)
├─ 죽은자의_생일파티_게임.html        # ★ 최신 게임 본체 (최상단에 새로 생성됨)
├─ .gitignore                       # 내용: .omx
├─ .idea/                           # JetBrains IDE 설정 (커밋되면 안 되는 것)
├─ fonts/
│  ├─ MaruBuriTTF/                  # ★ 게임이 사용 (5개)
│  └─ MaruBuriOTF/                  # 미사용 (5개)
├─ soundtrack/
│  ├─ *.mp3                         # 51개 중 25개만 사용
│  ├─ README.txt                    # 음원 출처 메모
│  └─ 크라임씬_OST_분류_검수반영.xlsx  # OST 분류표
└─ notion_mystery_game_html/        # ◀ 초기 버전(Notion 내보내기) 원본
   ├─ index.html                    # Notion 내보내기 진입점 (미사용)
   ├─ 《죽은 자의 생일파티》 ….html     # 방·문서별 .html 56개 (미사용)
   ├─ 《죽은 자의 생일파티》/           # 이 안의 PNG 일부를 새 게임이 참조
   └─ new_background_images/         # 방 배경 PNG 10개 (전부 사용)
```

**핵심 사정**: 원래 게임은 `notion_mystery_game_html/` 안의 Notion 내보내기였다. 이후 최상단에 새 게임 파일(`죽은자의_생일파티_게임.html`)을 만들면서, **옛 폴더에 흩어져 있던 이미지 리소스를 그 자리에서 그대로 참조**하도록 했다. 그 결과:
- 리소스(이미지)가 "원본 저작 자료"와 한 폴더에 뒤섞여 있다.
- 새 게임이 안 쓰는 `.html` 56개 + 미사용 이미지/음원/폰트가 그대로 남았다.

---

## 2. 사용/미사용 파일 인벤토리 (실측)

전체 에셋 107개 기준 — **사용 75 / 미사용 32**. 여기에 `.html` 56개와 메타 파일이 추가로 정리 대상.

> ⚠️ **2026-06-04 갱신**: PR #1(`fix : 도이준 파일 수정`)을 머지하면서 `…/프라이빗 라운지 🔒/ChatGPT_Image_…_01_28_46.png`가 **미사용 → 사용**으로 바뀜(도이준 개인 메모의 "클럽 VIP ROOM 팔찌" 단서). 아래 수치는 이를 반영한 값이다. 자세한 영향은 9장 참고.

### 2.1 게임에서 도달 불가한 파일 — 처리 방침

> **정책 결정(2026-06-04)**: 미사용 mp3와 미사용 이미지는 **삭제하지 않고 예비 리소스로 보존**한다. 삭제는 OTF 폰트만.

| 분류 | 개수 | 용량(대략) | 처리 |
|---|---|---|---|
| 미사용 폰트 `fonts/MaruBuriOTF/` | 5 | — | **삭제** (TTF만 사용) |
| 미사용 음원 `soundtrack/*.mp3` | 26 | 약 93MB | **보존** (예비 리소스) |
| 미사용 이미지(1장) | 1 | — | **보존** (예비 리소스, 아래 ※) |
| Notion `.html` 페이지 | 56 | — | 아카이브(2.3) — `index.html` 포함, 새 게임이 링크 안 함 |
| IDE 설정 `.idea/` | — | — | gitignore 처리 권장 |

※ 미사용 이미지 1장:
- `…/문해준 비서실 🔒/ChatGPT_Image_…_01_02_34.png` — 향후 단서로 붙을 수 있어 보존. (같은 패턴이던 `…/프라이빗 라운지 🔒/…_01_28_46.png`는 PR #1로 실제 **사용됨** → 보존 방침의 근거.)

참고 — 보존하기로 한 미사용 음원 26개 (파일명, `soundtrack/` 하위):
```
awakening-by-lucjo, beyond-these-walls-by-scott-buckley, black-vortex-by-kevin-macleod,
celestial-by-scott-buckley, descent-into-hell-live-by-audio-library-beats,
divertimento-k131-by-kevin-macleod, dreams-by-firefles, eglair-by-alex-productions,
expedition-by-alex-productions, eyes-in-the-void-by-scott-buckley, heroic-by-alex-productions,
impromptu-in-quarter-by-kevin-macleod, its-okay-by-firefles, liberation-forces-by-ghostrifter-avalon,
life-in-motion-by-scott-buckley, luminance-by-scott-buckley, mischief-in-the-garden-by-audio-library-beats,
odyssey-by-lucjo, rebel-by-alex-productions, reset-by-alex-productions, resurgence-by-ghostrifter-official,
reverie-pt-3-by-lucjo, shoulders-of-giants-by-scott-buckley, timeless-by-alex-productions,
traveling-around-the-world-by-alex-productions, weapon-by-alex-productions
```

### 2.2 보존 대상 (반드시 유지)
- `index.html`, `죽은자의_생일파티_게임.html`
- `fonts/MaruBuriTTF/` 5개
- 사용 중 mp3 25개
- `notion_mystery_game_html/new_background_images/` 10개
- `notion_mystery_game_html/《죽은 자의 생일파티》/` 하위에서 **실제 참조되는 PNG 45개** (배경 10 + 인물 7 + 초대장 6 + 표지/단서 등 22)

### 2.3 보관(아카이브) 권장
- `soundtrack/README.txt`, `크라임씬_OST_분류_검수반영.xlsx` → 출처/저작권 추적용이므로 삭제보다 `docs/`로 이동
- Notion `.html` 56개 → 삭제해도 게임은 동작하지만, **원본 저작 자료**이므로 별도 `archive/`(gitignore)로 격리 후 필요 시 참조 권장

---

## 3. 가장 큰 리스크 — 리소스 경로 인코딩이 뒤죽박죽

> 이 부분이 리팩토링 난이도의 핵심이라 먼저 명시한다.

게임 HTML 안의 이미지 참조 문자열이 **한 가지 형식이 아니다.** 같은 종류의 리소스인데도 케이스마다 인코딩이 다르다(실측 결과):

| 참조 형태 | 예시 | 비고 |
|---|---|---|
| percent-encoded 전체경로 | `notion_mystery_game_html/%E3%80%8A…%F0%9F%94%92/…png` | 대부분(약 42건) |
| 리터럴 유니코드 전체경로 | `…/도세아 작업실 🔒/초대장/도세아초대장.png` | 초대장 6장 |
| 파일명만 / 부분 경로 | 일부 단서 이미지 | 폴더 표기 방식이 케이스마다 상이 |

게다가 경로에 **공백 · 한글 · `《》` 특수문자 · 🔒 이모지**가 섞여 있다. 이는:
- 웹서버/호스팅(GitHub Pages 등)에서 대소문자·정규화·인코딩 차이로 **404가 나기 쉽고**,
- 단순 "찾아 바꾸기"로 경로를 옮기면 **일부 인코딩 형태를 놓쳐 깨진 링크**가 남는다.

**결론**: 경로를 옮기려면 "옛 참조 문자열(모든 인코딩 형태) → 새 경로" 매핑을 만들어 일괄 치환해야 안전하다. 그래서 아래 4.3의 *리소스 인덱스(JS 맵) 도입* 방식을 권한다.

> **실제 사례(PR #1)**: 도이준 단서 이미지를 추가한 커밋은 경로를 **리터럴 유니코드 전체경로**(`…/프라이빗 라운지 🔒/ChatGPT_Image_…_01_28_46.png`)로 박았다. 즉 새 콘텐츠가 들어올 때마다 인코딩 형태가 **계속 늘어난다.** RES 맵을 도입하지 않으면 이 혼재는 시간이 갈수록 악화된다.

---

## 4. 제안하는 목표 구조

### 4.1 디렉터리 레이아웃
```
crime/
├─ index.html                 # 진입점 (게임으로 redirect 유지, 또는 game을 index로 승격)
├─ game.html                  # 죽은자의_생일파티_게임.html → ASCII 이름으로 변경
├─ assets/
│  ├─ fonts/                  # MaruBuri TTF 5개
│  ├─ audio/                  # 사용 mp3 25개 (필요시 slug로 정리)
│  └─ img/
│     ├─ bg/                  # 방 배경 10 (new_background_images)
│     ├─ characters/          # 등장인물 7 (+ 표지)
│     ├─ invitations/         # 초대장 6
│     └─ clues/               # 나머지 단서 이미지 ~21 (방별 prefix)
├─ docs/
│  ├─ ost-credits.xlsx        # 크라임씬_OST_분류_검수반영.xlsx
│  └─ soundtrack-README.txt
└─ archive/                   # (gitignore) 원본 Notion 내보내기 통째 보관
   └─ notion_mystery_game_html/
```

### 4.2 파일명 규칙 (ASCII slug)
타임스탬프 기반 파일명(`ChatGPT_Image_2026년_6월_2일_오전_08_28_15.png`)은 의미를 알 수 없고 인코딩 문제의 원인이므로 **의미 있는 ASCII slug**로 변경 권장.

매핑 예시(일부):
| 현재 | 제안 |
|---|---|
| `…/등장인물/…_06_51_01.png` | `assets/img/characters/dojinmyeong.png` |
| `…/등장인물/…_08_28_15.png` | `assets/img/characters/dosea.png` |
| `…/도세아 작업실 🔒/초대장/도세아초대장.png` | `assets/img/invitations/dosea.png` |
| `…/new_background_images/중앙생일홀.png` | `assets/img/bg/main-hall.png` |
| `…/회장 개인 전시실 🔒/지갑 속 숨겨둔 사진/…_10_13_31.png` | `assets/img/clues/gallery-wallet-photo.png` |

> 전체 44장에 대한 매핑표는 실행 단계에서 별도 `migration-map.csv`로 작성한다(현재 참조 문자열 ↔ 새 경로 1:1).

### 4.3 게임 HTML의 리소스 참조 방식 개선 (권장)
경로를 코드 곳곳에 흩뿌리는 대신, **리소스 인덱스 한 곳**으로 모은다.

```html
<script>
const RES = {
  bg: {
    mainHall: "assets/img/bg/main-hall.png",
    studio:   "assets/img/bg/studio.png",
    // …
  },
  characters: { dojinmyeong: "assets/img/characters/dojinmyeong.png", /* … */ },
  invitations: { dosea: "assets/img/invitations/dosea.png", /* … */ },
  clues: { galleryWalletPhoto: "assets/img/clues/gallery-wallet-photo.png", /* … */ },
  audio: { theme: "assets/audio/penumbra-by-scott-buckley.mp3", /* … */ },
};
</script>
```
- 장점: 경로 변경 시 **한 곳만** 수정, 인코딩 이슈 원천 제거(ASCII 고정), 깨진 링크 점검이 쉬움.
- 다만 인라인 HTML 문자열(`"html": "…<img src=…>…"`) 안에 박힌 참조가 많아, 1차 단계에서는 **단순 경로 치환**만 하고 RES 맵 도입은 후속 단계로 분리하는 것도 가능.

---

## 5. 단계별 실행 계획

작은 PR로 쪼개 각 단계마다 **게임이 정상 동작하는지 검증** 후 다음 단계로.

### Phase 0 — 안전장치
- [ ] 현재 상태로 커밋/태그(`pre-refactor`) 생성 → 언제든 롤백 가능
- [ ] `.gitignore`에 `.idea/`, `archive/`, `.omx` 정리
- [ ] **사용/미사용 판정 스크립트**를 `tools/`에 커밋(아래 6장) → 회귀 검증용

### Phase 1 — 죽은 파일 제거 (저위험)
- [ ] `fonts/MaruBuriOTF/` 삭제 (**이번 단계의 유일한 삭제 대상**)
- [ ] ~~미사용 mp3 삭제~~ → **보존**(예비 리소스, 정책 결정 2.1)
- [ ] ~~미사용 이미지 삭제~~ → **보존**(예비 리소스, 정책 결정 2.1)
- [ ] 검증: 스크립트로 "참조됐는데 디스크에 없는 파일 0건" 확인 + 브라우저 실행
- *이 단계는 경로를 건드리지 않으므로 게임 동작에 영향 없음.*

### Phase 2 — Notion 원본 격리
- [ ] `notion_mystery_game_html/` 중 **사용 중 PNG 45개**를 `assets/img/...`로 복사
- [ ] 게임 HTML의 이미지 참조 경로를 새 위치로 치환(모든 인코딩 형태 대응, `migration-map.csv` 기준)
- [ ] 검증 후, 남은 Notion `.html` + **미사용 이미지(보존 대상)**를 `archive/`로 이동 — **삭제하지 않음**

### Phase 3 — 에셋 정리/리네이밍
- [ ] `fonts/`, `soundtrack/`(→`assets/audio/`) 이동 및 경로 치환
- [ ] 이미지 ASCII slug 리네이밍(4.2 매핑표)
- [ ] `docs/`로 xlsx·README 이동

### Phase 4 — (선택) 리소스 인덱스 도입
- [ ] 4.3의 `RES` 맵 도입, 인라인 참조를 키 기반으로 전환

### Phase 5 — 진입점 정리
- [ ] `죽은자의_생일파티_게임.html` → `game.html` 리네임
- [ ] `index.html` 리다이렉트 대상 갱신(또는 game을 그대로 `index.html`로 승격)

---

## 6. 검증 방법 (회귀 방지)

각 단계 후 동일 스크립트로 **깨진 링크 0 / 고아 파일 추적**을 자동 확인한다. (현재 분석에 쓴 로직)

판정 원리:
1. 게임 HTML에서 모든 에셋 확장자 참조를 추출(리터럴/percent-encoded/파일명 단위 모두).
2. **참조됐는데 디스크에 없음** = 깨진 링크 → 0건이어야 함.
3. **디스크에 있는데 참조 없음** = 고아 파일 → 기대 목록(OTF 삭제분 외에는 보존 중인 예비 mp3·이미지)과 일치하는지 대조. *예비 리소스를 보존하므로 고아 파일이 0이 될 필요는 없다 — 목록이 예상과 같은지만 본다.*

수동 검증(필수): 로컬 서버로 띄워 각 방 진입 → 배경·인물·초대장·단서 이미지·BGM 재생 확인.
```bash
python -m http.server 8000   # http://localhost:8000/ 접속해 한 바퀴 플레이
```
> ⚠️ `file://`로 직접 열면 일부 브라우저가 한글/인코딩 경로 리소스를 막을 수 있으니 **로컬 HTTP 서버**로 검증할 것.

---

## 7. 기대 효과

| 항목 | Before | After |
|---|---|---|
| 레포 용량 | 잡다한 미사용 파일 혼재 | OTF만 제거(예비 mp3·이미지는 보존) |
| 리소스 위치 | 원본 저작 폴더에 뒤섞임 | `assets/`로 일원화 |
| 경로 인코딩 | percent/리터럴/부분 혼재(깨지기 쉬움) | ASCII 고정 |
| 파일명 | 타임스탬프(의미 불명) | 의미 있는 slug |
| 유지보수 | 경로가 코드 전체에 산재 | (선택)`RES` 맵 한 곳 |

---

## 8. 미해결/결정 필요 사항
- Notion `.html` 56개: **완전 삭제** vs **`archive/` 보관**? (원본 저작 자료라 보관 권장)
- 진입점: `index.html` 리다이렉트 유지 vs `game.html`을 `index.html`로 승격?
- 이미지 ASCII 리네이밍을 **할지**(Phase 3) — 안 하면 인코딩 리스크가 일부 잔존.
- 게임 본체가 단일 거대 HTML인데, 이번 범위는 **파일/경로 정리에 한정**하고 코드 분리(JS/CSS 외부화)는 별도 과제로 둘지.

---

## 9. 변경 검토 로그 — PR #1 (2026-06-04)

pull한 변경(`95090fe` Merge / `ea5bdc9` `fix : 도이준 파일 수정`, author 이혜연)이 계획에 주는 영향 검토 결과.

**무엇이 바뀌었나** — 단 2개 파일:
1. `죽은자의_생일파티_게임.html`: 도이준 개인 메모(`custom_doijun_private_memo`) 섹션에 단서 이미지 2장 추가 — "클럽 VIP ROOM 팔찌"(`…/프라이빗 라운지 🔒/…_01_28_46.png`)와 "넥타이핀"(`…/프라이빗 라운지 🔒/image.png`).
2. `…/프라이빗 라운지 🔒 ….html` (Notion 원본): 동일 수정의 원본 측 반영. **게임 동작과 무관**(아카이브 대상 그대로).

**계획에 준 영향**
- 인벤토리 수치 갱신: 미사용 33 → **32**, 사용 74 → **75**. 미사용 이미지 2장 → **1장**(`…_01_28_46.png`가 사용으로 전환). 2장에서 본문 반영 완료.
- **삭제 자동화의 위험 재확인**: 만약 PR #1 이전에 "미사용 이미지 2장"을 자동 삭제했다면, 이 fix가 곧바로 **깨진 단서**가 됐을 것이다. → 이를 근거로 **미사용 mp3·이미지는 삭제하지 않고 예비 리소스로 보존**하기로 확정(2.1 정책 결정). 삭제는 OTF 폰트만.
- **인코딩 혼재 악화 확인**: 새 참조가 리터럴 유니코드 경로로 추가됨(3장 사례 참조).

**새로 식별된 리스크 — 동시 작업 충돌**
- 이 레포는 **여러 명이 게임 본체(`죽은자의_생일파티_게임.html`)에 콘텐츠 PR**을 올리고 있다(PR #1이 그 예). 본체는 한 줄 minified라 **줄 단위 머지가 거의 불가능** → 경로 일괄 치환 같은 대규모 변경은 진행 중인 콘텐츠 PR과 **충돌이 확정적**.
- 대응: Phase 2~4(본체 경로 치환)는 **콘텐츠 PR이 비는 시점에 짧게, 단독으로** 처리하고 즉시 머지. Phase 1(죽은 파일 삭제)·Phase 0(스크립트/gitignore)은 본체를 안 건드리므로 충돌 위험이 낮아 **먼저 진행 가능**.

---

## 10. 실행 결과 (Phase 0~5 완료)

브랜치 `refactor/restructure`, 롤백 태그 `pre-refactor`. 각 단계 후 `tools/check-assets.py`로 **깨진 링크 0** 확인.

### 최종 구조
```
crime/
├─ index.html              # 진입점 → game.html 리다이렉트
├─ game.html               # 게임 본체(구 죽은자의_생일파티_게임.html)
├─ assets/
│  ├─ fonts/               # MaruBuri TTF 5
│  ├─ audio/               # 사용 BGM 25
│  ├─ img/{bg,characters,invitations,clues}/ + cover.png   # 사용 이미지 45
│  └─ spare/{img,audio}/   # 예비(미사용) 리소스: 이미지 1 + mp3 26 (tracked 보존)
├─ source/notion_mystery_game_html/   # 원본 Notion 내보내기(.html) — tracked 보존
├─ docs/                   # migration-map.csv, ost-credits.xlsx, soundtrack-README.txt
└─ tools/check-assets.py   # 깨진 링크/고아 파일 검증
```

### 커밋
| 단계 | 내용 |
|---|---|
| Phase 0 | 문서·검증 스크립트·gitignore(`.idea/`,`archive/`) |
| Phase 1 | 미사용 OTF 폰트 5개 삭제 (유일한 삭제) |
| Phase 2 | 사용 이미지 45 → `assets/img`(ASCII), 경로 114곳 치환, 예비 이미지·Notion 원본 격리 |
| Phase 3 | 폰트·음원 → `assets/{fonts,audio}`, 미사용 mp3 26 → `assets/spare/audio`, 메타 → `docs/` |
| Phase 5 | `game.html` 리네임, `index.html`·검증 스크립트 갱신 |
| Phase 4 | **생략** — ASCII 경로화로 인코딩 문제가 해소되어 RES 맵 불필요 |

### 핵심 기법
- 게임 HTML의 리소스 참조는 인코딩 혼재(percent/리터럴) → **본문에 실재하는 raw 문자열만 추출해 그대로 치환**, 인코딩 추측 배제.
- 모든 파일 이동은 git이 100% rename으로 추적(히스토리 보존).
- 단계마다 `check-assets.py` 깨진 링크 0 + `DATA` JSON 파싱 검증.

### 남은 수동 검증 (권장)
- 로컬 HTTP 서버(`python -m http.server`)로 한 바퀴 플레이: 각 방 배경·인물·초대장·단서 이미지 + BGM 재생 확인. (자동 검증은 경로 무결성까지만 보장)
