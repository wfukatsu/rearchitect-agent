---
description: GraphDB構築エージェント - ユビキタス言語とコード解析結果からRyuGraphデータベースを構築。
argument-hint: [対象パス]
---

# GraphDB構築エージェント

既存のシステム分析結果とソースコードを解析し、RyuGraph GraphDBにユビキタス言語ベースのナレッジグラフを構築するエージェントです。

## 実行手順

1. 対象ディレクトリの分析結果（`reports/01_analysis/`）を読み込む
2. Serenaツールでソースコードを解析
3. CSVファイルを生成
4. `scripts/build_graph.py` でRyuGraphデータベースを構築
5. 統計情報を出力

## 出力

- `<対象パス>/knowledge.ryugraph/` - GraphDBデータベース
- `<対象パス>/reports/graph/` - 中間ファイルと統計

詳細は `.claude/skills/build-graph/SKILL.md` を参照してください。
