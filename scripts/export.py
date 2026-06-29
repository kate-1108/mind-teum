"""
HTML 카드 → PNG 변환 스크립트 (Playwright)

사용법:
  # 단일 파일
  python scripts/export.py output/card-01.html

  # 여러 파일
  python scripts/export.py output/card-01.html output/card-02.html

  # output/ 폴더 전체 일괄 변환
  python scripts/export.py --all
"""

import sys
import argparse
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from playwright.sync_api import sync_playwright

CARD_W = 1080
CARD_H = 1350
PROJECT_ROOT = Path(__file__).parent.parent


def export_card(page, html_path: Path, out_path: Path) -> None:
    url = html_path.resolve().as_uri()
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.wait_for_function("document.fonts.ready")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": CARD_W, "height": CARD_H})


def main():
    parser = argparse.ArgumentParser(description="Mind.teum 카드 HTML → PNG 변환")
    parser.add_argument("files", nargs="*", help="변환할 HTML 파일 경로")
    parser.add_argument("--all", action="store_true", help="output/ 폴더의 모든 HTML 일괄 변환")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "output"), help="PNG 저장 폴더 (기본: output/)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if args.all:
        html_files = sorted(output_dir.glob("*.html"))
        if not html_files:
            print("output/ 폴더에 HTML 파일이 없어요.")
            sys.exit(1)
    elif args.files:
        html_files = [Path(f) for f in args.files]
    else:
        parser.print_help()
        sys.exit(1)

    print(f"{len(html_files)}개 파일 변환 시작...")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": CARD_W, "height": CARD_H})

        for html_path in html_files:
            if not html_path.exists():
                print(f"  건너뜀 (파일 없음): {html_path}")
                continue
            out_path = output_dir / (html_path.stem + ".png")
            export_card(page, html_path, out_path)
            print(f"  ✓ {html_path.name} → {out_path.name}")

        browser.close()

    print("완료.")


if __name__ == "__main__":
    main()
