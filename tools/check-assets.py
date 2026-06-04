#!/usr/bin/env python3
"""게임 HTML이 참조하는 리소스와 디스크의 리소스를 대조한다.

용도:
  - 깨진 링크   : 게임이 참조하는데 디스크에 없는 파일 (있으면 안 됨)
  - 고아 파일   : 디스크에 있는데 게임이 참조하지 않는 파일 (예비 리소스로 보존 중일 수 있음)

게임 본체는 리소스 경로를 percent-encoded / 리터럴 유니코드 / 파일명 단위 등
여러 형태로 박아두므로, 각 파일명을 가능한 인코딩 형태로 모두 만들어 본문에서 찾는다.
(레포 규칙: 개수를 외우지 말고 매번 이 스크립트로 직접 뽑아낼 것.)

종료 코드: 깨진 링크가 있으면 1, 없으면 0.
"""
import glob
import os
import sys
import urllib.parse

# 에셋 참조가 흩어져 있는 파일들: game.html(폰트 @font-face 등) + game.json(데이터·노드 html 내 <img>)
SCAN_FILES = ("game.html", "game.json")
ASSET_EXTS = ("mp3", "png", "jpg", "jpeg", "webp", "gif", "svg", "ttf", "otf", "woff", "woff2")

# 한글/이모지 경로가 콘솔 인코딩(cp949 등)에서 깨지지 않도록 강제 UTF-8 출력
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def name_forms(name):
    """파일명이 게임 HTML에 나타날 수 있는 형태들."""
    return {
        name,
        urllib.parse.quote(name),
        urllib.parse.quote(name, safe=""),
        name.replace(" ", "%20"),
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    game = ""
    scanned = []
    for fn in SCAN_FILES:
        if os.path.exists(fn):
            with open(fn, encoding="utf-8", errors="replace") as f:
                game += "\n" + f.read()
            scanned.append(fn)

    assets = set()
    for ext in ASSET_EXTS:
        assets.update(p.replace("\\", "/") for p in glob.glob("**/*." + ext, recursive=True))
    assets = sorted(assets)

    orphans = []
    for path in assets:
        base = os.path.basename(path)
        if not any(form in game for form in name_forms(base) if form):
            orphans.append(path)

    # 깨진 링크: 게임에서 자산 확장자로 끝나는 경로 문자열을 뽑아 디코드 후 존재 확인
    import re
    broken = []
    pat = re.compile(r'["\']([^"\']*?\.(?:%s))["\']' % "|".join(ASSET_EXTS), re.I)
    seen = set()
    for m in pat.finditer(game):
        ref = m.group(1)
        if ref.startswith(("http://", "https://", "data:")):
            continue
        # 실제 리소스 참조는 항상 디렉터리를 포함한다. '/'가 없는 건
        # JS가 동적 조립하는 확장자 조각(예: ".mp3") 같은 false positive.
        if "/" not in ref:
            continue
        dec = urllib.parse.unquote(ref).split("#")[0].split("?")[0]
        dec = dec.replace("\\", "/").lstrip("./")
        if not dec or dec in seen:
            continue
        seen.add(dec)
        if not os.path.exists(dec):
            broken.append(dec)

    print("스캔 파일:", ", ".join(scanned))
    print("디스크 자산 총:", len(assets), "| 고아(미참조):", len(orphans), "| 깨진 링크:", len(broken))
    print()
    print("=== 깨진 링크 (참조됐는데 디스크에 없음) — 0이어야 함 ===")
    for b in sorted(set(broken)):
        print("  !!", b)
    if not broken:
        print("  (없음)")
    print()
    print("=== 고아 파일 (디스크에 있는데 미참조) — 보존 중인 예비 리소스 포함 ===")
    for o in orphans:
        print("  ?", o)
    if not orphans:
        print("  (없음)")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
