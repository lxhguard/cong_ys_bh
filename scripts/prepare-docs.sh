#!/usr/bin/env bash
# 推送 / 本地预览前跑这个：同步 docs-manifest.json + docs-data.js
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/gen-docs-manifest.py
echo "下一步：把 docs-data.js、docs-manifest.json、markdown/ 一起部署。"
