---
description: GraphDB可視化エージェント - RyuGraphデータベースの内容をMermaid/DOT/HTML形式で可視化。
argument-hint: [出力パス]
---

# GraphDB可視化エージェント

RyuGraphデータベースの内容を可視化し、Mermaid図やインタラクティブHTMLとして出力します。

## 使用方法

```bash
# 全形式で可視化
/visualize-graph ./reports/graph/visualizations

# 特定ドメインのみ
/visualize-graph --domain Audit

# Mermaid形式のみ
/visualize-graph --format mermaid
```

## 出力形式

- **Mermaid** (.mmd) - ドキュメント埋め込み用
- **DOT** (.dot) - Graphviz用
- **HTML** (.html) - インタラクティブビュー

## オプション

| オプション | 説明 |
|-----------|------|
| `--format` | mermaid/dot/html/all |
| `--domain` | フィルタするドメイン |
| `--node-type` | フィルタするノードタイプ |
| `--max-nodes` | 最大ノード数 |

詳細は `.claude/skills/visualize-graph/SKILL.md` を参照してください。
