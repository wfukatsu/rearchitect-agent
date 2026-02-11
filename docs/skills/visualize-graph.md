# /visualize-graph — ナレッジグラフ可視化

**カテゴリ**: Knowledge Graph（ナレッジグラフ） | **Phase 12**

RyuGraphデータベースの内容をMermaid/DOT/HTML形式で可視化します。

## 使用方法

```bash
/visualize-graph ./reports/graph/visualizations
```

## 前提条件

### 必須
- Python 3.9+
- `ryugraph`, `pandas` パッケージ
- `/build-graph` が実行済みで `knowledge.ryugraph` が存在すること

### オプション
- `graphviz` パッケージ（DOT → PNG変換用）
- `mermaid-cli`（Mermaid → PNG変換用）

## 可視化形式

| 形式 | 説明 | 用途 |
|------|------|------|
| **Mermaid** | Markdown埋め込み可能な図 | レポート、ドキュメント |
| **DOT** | Graphviz形式 | 大規模グラフの詳細可視化 |
| **HTML** | D3.jsインタラクティブグラフ | ブラウザでの探索的分析 |

## 実行ステップ

1. **グラフデータの読み込み** — RyuGraphからノード・エッジを読み込み
2. **フィルタリング** — 特定のドメインやノードタイプでフィルタ
3. **レイアウト計算** — ノード配置の最適化
4. **各形式での出力** — Mermaid/DOT/HTMLファイル生成

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/graph/visualizations/graph-overview.md` | 全体グラフ（Mermaid） |
| `reports/graph/visualizations/graph-by-context.md` | コンテキスト別グラフ |
| `reports/graph/visualizations/graph.dot` | DOT形式 |
| `reports/graph/visualizations/interactive-graph.html` | D3.jsインタラクティブグラフ |

## オプション

| フラグ | 説明 |
|--------|------|
| `--format=mermaid` | Mermaid形式のみ出力 |
| `--format=html` | HTML形式のみ出力 |
| `--filter=Entity` | 特定ノードタイプでフィルタ |
| `--domain=Order` | 特定ドメインでフィルタ |

## 関連スキル

- 前提: [/build-graph](build-graph.md)
- 補完: [/query-graph](query-graph.md)
- 統合: [/compile-report](compile-report.md)（HTMLレポートに埋め込み）
