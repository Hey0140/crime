# CLAUDE.md

머더미스터리 HTML 게임 《죽은 자의 생일파티》 레포. 이 문서는 이 레포에서 작업할 때의 프로젝트 고유 규칙과, 그 아래의 일반 코딩 가이드라인으로 구성된다.

---

## 프로젝트 개요

- **진입점**: `index.html` → meta refresh + `location.replace`로 `죽은자의_생일파티_게임.html`로 리다이렉트.
- **게임 본체**: `죽은자의_생일파티_게임.html` **단일 파일**. 모든 스토리·방·단서 HTML이 `<script>` 안의 JS 데이터(`DATA`/`N` 객체)로 **인라인 내장**되어 있다. 빌드 단계·번들러·패키지 매니저 없음. 그냥 정적 HTML.
- **리소스(디스크에서 로드하는 것)**:
  - `fonts/MaruBuriTTF/*.ttf` — `MaruBuriOTF/`는 미사용
  - `soundtrack/*.mp3` — 일부만 사용
  - `notion_mystery_game_html/new_background_images/*.png` — 방 배경
  - `notion_mystery_game_html/《죽은 자의 생일파티》/**/*.png` — 인물·초대장·단서 이미지
  - 어떤 파일이 실제로 참조되는지는 외워두지 말고 매번 게임 HTML을 grep해서 확인할 것(아래 4번).
- **`notion_mystery_game_html/`의 정체**: 초기 버전(Notion 내보내기) 원본. 게임 본체는 이 폴더의 **이미지 PNG만** 골라 참조하며, 그 안의 `.html`과 `index.html`은 **참조하지 않는다**(원본 저작 자료).

## 이 레포에서 작업할 때 반드시 지킬 것

1. **리소스 경로 인코딩이 일관되지 않다.** 같은 이미지라도 참조 문자열이 ① percent-encoded 전체경로(`%E3%80%8A…`), ② 리터럴 유니코드 전체경로(`…/도세아 작업실 🔒/초대장/…png`), ③ 파일명 단위 등 **케이스마다 다르게** 박혀 있다. 경로를 옮기거나 이름을 바꿀 때는 **모든 인코딩 형태를 찾아** 치환해야 한다. 단순 1회 찾아바꾸기는 깨진 링크를 남긴다.

2. **경로에 공백·한글·`《》`·🔒 이모지가 섞여 있다.** 새 리소스를 추가할 때는 가능하면 **ASCII 파일명**을 쓰고, 기존 경로를 건드릴 일이 있으면 인코딩 깨짐에 주의한다.

3. **테스트는 로컬 HTTP 서버로 한다.** `file://`로 직접 열면 브라우저가 한글/인코딩 경로 리소스를 막아 이미지·음원이 안 뜰 수 있다.
   ```bash
   python -m http.server 8000   # http://localhost:8000/ 에서 한 바퀴 플레이
   ```
   변경 후엔 각 방 진입 → 배경·인물·초대장·단서 이미지 표시 + BGM 재생까지 눈으로 확인.

4. **파일을 지우기 전에 참조 여부를 검증한다.** 리소스가 게임 HTML 어딘가에서 (모든 인코딩 형태로) 참조되는지 확인하고, "참조됐는데 디스크에 없음 = 깨진 링크"가 0건인지 점검한다. 한글/이모지 경로는 콘솔 출력 시 인코딩 에러가 나기 쉬우니 결과는 파일로 써서 확인하는 편이 안전하다. 사용/미사용 목록이나 개수가 필요하면 외운 값을 쓰지 말고 그때그때 직접 뽑아낼 것.

5. **거대 단일 HTML이다.** 본체를 편집할 때는 인라인 JS 데이터 구조(`DATA`/`N`, 방 id, `locked`/`answers` 등 게임 로직)를 깨지 않도록 국소적으로 수정한다. 대규모 코드 분리(JS/CSS 외부화)는 별도 합의된 과제로만 진행한다.

6. **`notion_mystery_game_html/`의 `.html`은 손대지 않는다.** 게임과 무관한 원본 자료다. 정리/삭제는 별도 리팩토링 과제(`REFACTORING_PROPOSAL.md`)에서 합의 후 진행.

7. 자세한 정리/구조 개편 계획은 `REFACTORING_PROPOSAL.md` 참고. 그 작업은 합의 전까지 실행하지 않는다.

---

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.