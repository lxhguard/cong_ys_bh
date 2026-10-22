#!/usr/bin/env python3
"""扫描 markdown/ 下全部 .md，生成 docs-manifest.json。

本地也可手动跑：
  python3 scripts/gen-docs-manifest.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "markdown"
OUT = ROOT / "docs-manifest.json"


def main() -> None:
    files: list[str] = []
    if DOCS_ROOT.is_dir():
        files = [
            p.relative_to(ROOT).as_posix()
            for p in sorted(DOCS_ROOT.rglob("*.md"))
            if p.is_file()
        ]
    payload = {"files": files}
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({len(files)} files)")


if __name__ == "__main__":
    main()
