# Refactoring Agent - Claude Code プロジェクト設定

## プロジェクト概要

このプロジェクトは、既存システムを分析し、Modularity Maturity Index (MMI) に基づいて評価を行い、マイクロサービスアーキテクチャへのリファクタリング計画を策定するためのClaude Codeエージェント群です。

## 利用可能なスキル

### メインオーケストレーター

| スキル | コマンド | 説明 |
|-------|--------|------|
| System Refactoring | `/refactor-system` | 統合リファクタリングエージェント |

### サブスキル

| スキル | コマンド | 説明 |
|-------|--------|------|
| System Analyzer | `/analyze-system` | システム分析・ユビキタス言語抽出 |
| MMI Evaluator | `/evaluate-mmi` | Modularity Maturity Index評価 |
| Domain Mapper | `/map-domains` | ドメインマッピング・コンテキスト設計 |
| Microservice Architect | `/design-microservices` | マイクロサービス設計・移行計画 |
| ScalarDB Architect | `/design-scalardb` | ScalarDB Clusterを使用したデータアーキテクチャ設計 |
| ScalarDB Analytics Architect | `/design-scalardb-analytics` | ScalarDB Analyticsを使用した分析基盤設計 |
| Domain Storyteller | `/create-domain-story` | ドメインストーリーテリング |

### ナレッジグラフスキル

| スキル | コマンド | 説明 |
|-------|--------|------|
| Graph Builder | `/build-graph` | RyuGraphデータベースを構築 |
| Graph Explorer | `/query-graph` | ユビキタス言語ベースでグラフを探索 |
| Graph Visualizer | `/visualize-graph` | グラフをMermaid/DOT/HTML形式で可視化 |

### ユーティリティスキル

| スキル | コマンド | 説明 |
|-------|--------|------|
| Report Compiler | `/compile-report` | Markdownレポートを統合HTMLに変換 |
| Mermaid Renderer | `/render-mermaid` | Mermaid図をPNG/SVG/PDF画像に変換 |
| Mermaid Fixer | `/fix-mermaid` | Mermaid図のシンタックスエラーを修正 |

## クイックスタート

### 1. フルリファクタリング分析

```bash
# 対象ディレクトリを指定して実行
/refactor-system ./path/to/source
```

### 2. 個別スキルの実行

```bash
# システム分析のみ
/analyze-system ./path/to/source

# MMI評価のみ
/evaluate-mmi ./path/to/source

# ドメインストーリー作成
/create-domain-story --domain=Order

# Mermaid図を画像に変換
/render-mermaid ./.refactoring-output/

# Mermaid図のエラーを修正
/fix-mermaid ./.refactoring-output/

# ナレッジグラフを構築
/build-graph ./path/to/source

# グラフを探索（自然言語）
/query-graph 「注文」に関連するクラスを教えて

# グラフを探索（Cypher）
/query-graph MATCH (e:Entity)-[:HAS_TERM]->(t:UbiquitousTerm) RETURN e, t LIMIT 10

# グラフを可視化
/visualize-graph ./reports/graph/visualizations

# 特定ドメインのみ可視化
/visualize-graph --domain Audit

# ScalarDB Clusterを使用したデータアーキテクチャ設計
/design-scalardb ./path/to/source

# ScalarDB Analyticsを使用した分析基盤設計
/design-scalardb-analytics ./path/to/source

# レポートをHTMLにコンパイル
/compile-report

# ダークテーマでPDF出力も生成
/compile-report --theme dark --pdf
```

## 出力先

すべての出力は `reports/` ディレクトリに保存されます。

```
reports/
├── 00_summary/           # エグゼクティブサマリー
│   ├── executive-summary.md
│   └── full-report.html  # 統合HTMLレポート
├── 01_analysis/          # システム分析結果
├── 02_evaluation/        # MMI評価結果
├── 03_design/            # マイクロサービス設計
├── 04_stories/           # ドメインストーリー
├── graph/                # GraphDB用データ
│   ├── data/             # CSVファイル
│   ├── visualizations/   # 可視化ファイル
│   ├── schema.md         # グラフスキーマ
│   └── statistics.md     # 統計情報
└── 99_appendix/          # 付録

<プロジェクトルート>/
└── knowledge.ryugraph/   # RyuGraphデータベース
```

## ツール優先順位

このプロジェクトでは、以下の優先順位でツールを使用してください：

### コード解析

1. **Serenaツール** （最優先）
   - `mcp__serena__get_symbols_overview` - ファイル構造把握
   - `mcp__serena__find_symbol` - シンボル検索
   - `mcp__serena__find_referencing_symbols` - 参照追跡
   - `mcp__serena__list_dir` - ディレクトリ走査

2. **Glob/Grep** - パターンマッチング
3. **Read** - ファイル内容確認

### 対話的な情報収集

- `AskUserQuestion` - ユーザーへの質問

### タスク管理

- `TodoWrite` - 進捗管理
- `Task` - サブエージェント起動

## 設計原則

### MMI評価の4軸

| 軸 | 重み | 説明 |
|---|-----|------|
| Cohesion | 30% | 単一責務性 |
| Coupling | 30% | 疎結合性 |
| Independence | 20% | デプロイ独立性 |
| Reusability | 20% | 再利用性 |

### ドメイン分類

**ビジネス構造軸：**
- Pipeline Domain（順序的フロー）
- Blackboard Domain（共有データ協調）
- Dialogue Domain（双方向インタラクション）

**マイクロサービス境界軸：**
- Process Domain（ビジネスプロセス）
- Master Domain（マスタデータ）
- Integration Domain（外部連携）
- Supporting Domain（横断機能）

## ワークフロー

```mermaid
graph TD
    A[/refactor-system] --> B[/analyze-system]
    B --> C[/evaluate-mmi]
    C --> D[/map-domains]
    D --> E[/design-microservices]
    E --> F[/design-scalardb]
    F --> F2{分析要件あり?}
    F2 -->|Yes| FA[/design-scalardb-analytics]
    F2 -->|No| G[/create-domain-story]
    FA --> G
    G --> H[Executive Summary生成]
    H --> K[/compile-report]
    K --> L[統合HTMLレポート]
    B --> I[/build-graph]
    I --> J[/query-graph]
    I --> M[/visualize-graph]
```

### GraphDBワークフロー

```mermaid
graph LR
    A[/analyze-system] --> B[分析結果MD]
    B --> C[parse_analysis.py]
    C --> D[CSVファイル]
    D --> E[build_graph.py]
    E --> F[knowledge.ryugraph]
    F --> G[/query-graph]
    G --> H[関連コード・仕様]
    F --> I[/visualize-graph]
    I --> J[Mermaid/DOT/HTML]
```

## エラーハンドリング

- 設計書がない場合 → コードからの推論（精度低下を警告）
- 大規模コードベース → サンプリング分析を提案
- 言語非対応 → 手動解析を提案

## カスタマイズ

### 出力先の変更

```bash
/refactor-system ./src --output=./custom-output/
```

### 特定ドメインのみ分析

```bash
/refactor-system ./src --domain=Order,Customer
```

### 分析のみ（設計書生成なし）

```bash
/refactor-system ./src --analyze-only
```

## RyuGraph セットアップ

GraphDBスキルを使用するには、RyuGraphのインストールが必要です：

```bash
pip install ryugraph pandas
```

### 手動でのグラフ構築

```bash
# 1. 分析結果からCSVを生成
python scripts/parse_analysis.py \
  --input-dir ./reports/01_analysis \
  --output-dir ./reports/graph/data

# 2. GraphDBを構築
python scripts/build_graph.py \
  --data-dir ./reports/graph/data \
  --db-path ./knowledge.ryugraph

# 3. クエリを実行
python scripts/query_graph.py \
  --db-path ./knowledge.ryugraph \
  --interactive

# 4. グラフを可視化
python scripts/visualize_graph.py \
  --data-dir ./reports/graph/data \
  --output-dir ./reports/graph/visualizations

# 5. レポートをHTMLにコンパイル
python scripts/compile_report.py \
  --input-dir ./reports \
  --output ./reports/00_summary/full-report.html \
  --title "リファクタリング分析レポート"
```

## 参考資料

- [ScalarDB Documentation](https://scalardb.scalar-labs.com/docs/)
- [ScalarDB Analytics](https://scalardb.scalar-labs.com/docs/latest/scalardb-analytics/)
- [RyuGraph Documentation](https://ryugraph.io/docs/)
- [Modularity Maturity Index](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/modularity-maturity-index.md)
- [Domain-Driven Transformation](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/domain-driven-transformation.md)
- [Domain Storytelling](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/domain-storytelling.md)

## バージョン

- バージョン: 1.0.0
- 作成日: 2024
- 作成者: Claude Code
