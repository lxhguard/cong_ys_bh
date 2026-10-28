# 原神 · 私人站点 / 简历

站点：原神.ciji.lol（GitHub Pages）

## 文档怎么更新

1. 改 / 增删 `markdown/` 下的 `.md` / `.html`
2. **推到 `main`** → GitHub Actions（`.github/workflows/prepare-docs.yml`）会自动跑 `scripts/gen-docs-manifest.py`，更新并提交：
   - `docs-manifest.json`（文件列表）
   - `docs-data.js`（列表 + 正文，给 `index.html` 用）
3. Pages 部署后，打开站点 Docs 页就能读到最新内容

本地预览也可手动生成：

```bash
bash scripts/prepare-docs.sh
# 或
python3 scripts/gen-docs-manifest.py
```

也可在 GitHub → Actions → **Prepare docs** → **Run workflow** 手动触发。
