# /full-pipeline — 完全パイプライン実行

**カテゴリ**: Orchestration（統括）

調査から設計・コード生成まで全26+フェーズを一括で自動実行する統合オーケストレーターです。

## 使用方法

```bash
# 基本実行
/full-pipeline ./path/to/source

# オプション付き実行
/full-pipeline ./path/to/source --output=./custom-output/
/full-pipeline ./path/to/source --domain=Order,Customer
/full-pipeline ./path/to/source --analyze-only
/full-pipeline ./path/to/source --skip-security --skip-analytics
/full-pipeline ./path/to/source --resume-from=phase-6
```

## 概要

以下のフェーズを自動的に順次実行します。

| フェーズ | スキル | 出力先 |
|---------|--------|--------|
| 0 | `/system-investigation` | `reports/before/{project}/` |
| 0.5a | `/security-analysis` | `reports/before/{project}/` |
| 0.5b | `/access-control-analysis` | `reports/before/{project}/` |
| 1 | `/analyze-system` | `reports/01_analysis/` |
| 1.5a | `/data-model-analysis` | `reports/01_analysis/` |
| 1.5b | `/db-design-analysis` | `reports/01_analysis/` |
| 1.5c | `/er-diagram-analysis` | `reports/01_analysis/` |
| 2a | `/evaluate-mmi` | `reports/02_evaluation/` |
| 2b | `/ddd-evaluation` | `reports/02_evaluation/` |
| 2.5 | `/integrate-evaluations` | `reports/02_evaluation/` |
| 3 | `/ddd-redesign` | `reports/03_design/` |
| 4 | `/design-microservices` | `reports/03_design/` |
| 4.7 | `/select-scalardb-edition` | `work/{project}/` |
| 4.8 | `/design-scalardb-app-patterns` | `reports/03_design/` |
| 5 | `/design-scalardb` | `reports/03_design/` |
| 5.5 | `/design-scalardb-analytics` | `reports/03_design/` |
| 5.9 | `/review-scalardb --mode=design` | `reports/03_design/` |
| 5.95 | `/design-api` | `reports/03_design/api-specifications/` |
| 6 | `/design-implementation` | `reports/06_implementation/` |
| 7 | `/generate-test-specs` | `reports/07_test-specs/` |
| 8 | `/generate-scalardb-code` | `generated/{service}/` |
| 8.5 | `/review-scalardb --mode=code` | `reports/03_design/` |
| 8.7 | `/design-infrastructure` | `reports/08_infrastructure/` |
| 9 | `/estimate-cost` | `reports/05_estimate/` |
| 10 | `/create-domain-story` | `reports/04_stories/` |
| 11 | `/build-graph` | `reports/graph/` |
| 12 | `/fix-mermaid` | （検証のみ） |
| 13 | Executive Summary | `reports/00_summary/` |

## 前提条件

### 必須
- 対象ディレクトリにソースコードまたは設計書が存在すること

### 推奨
- Python環境: `pip install ryugraph pandas markdown pymdown-extensions`
- Node.js: `npm install -g @mermaid-js/mermaid-cli`
- Serena MCP Server

## オプション

| フラグ | 説明 |
|--------|------|
| `--output=PATH` | 出力先ディレクトリ指定 |
| `--domain=Name1,Name2` | 特定ドメインのみ対象 |
| `--analyze-only` | 分析フェーズのみ実行（Phase 3以降スキップ） |
| `--skip-codegen` | コード生成スキップ（Phase 8, 8.5） |
| `--skip-security` | セキュリティ分析スキップ（Phase 0.5a, 0.5b） |
| `--skip-data-model` | データモデル詳細分析スキップ（Phase 1.5a-c） |
| `--skip-analytics` | ScalarDB Analytics設計スキップ（Phase 5.5） |
| `--skip-stories` | ドメインストーリースキップ（Phase 10） |
| `--skip-infrastructure` | インフラ設計スキップ（Phase 8.7） |
| `--skip-graph` | グラフ構築スキップ（Phase 11） |
| `--resume-from=phase-N` | 指定フェーズから再開 |

## 実行ステップ

1. **ユーザー入力確認** — 対象フォルダ、出力先ディレクトリを確認
2. **初期化** — 引数解析、プロジェクト名決定、ディレクトリ作成、進捗レジストリ作成
3. **Phase 0** — システム調査
4. **Phase 0.5** — セキュリティ・アクセス制御分析（並行実行）
5. **Phase 1** — システム分析
6. **Phase 1.5** — データモデル詳細分析（順次依存）
7. **Phase 2a/2b** — MMI/DDD評価（並行実行）
8. **Phase 2.5** — 評価統合
9. **Phase 3** — DDD再設計
10. **Phase 4〜5.95** — マイクロサービス・ScalarDB・API設計
11. **Phase 6〜8.7** — 実装仕様・テスト仕様・コード生成・インフラ設計
12. **Phase 9〜11** — 見積もり・ドメインストーリー・グラフ構築
13. **Phase 12〜13** — Mermaid検証・エグゼクティブサマリー
14. **最終レポート** — `/compile-report` で HTML 統合レポート生成
15. **完了通知**

## 出力ファイル

```
reports/
├── before/{project}/     ← Phase 0, 0.5
├── 00_summary/           ← Phase 13
├── 01_analysis/          ← Phase 1, 1.5
├── 02_evaluation/        ← Phase 2, 2.5
├── 03_design/            ← Phase 3〜5.95
├── 04_stories/           ← Phase 10
├── 05_estimate/          ← Phase 9
├── 06_implementation/    ← Phase 6
├── 07_test-specs/        ← Phase 7
├── 08_infrastructure/    ← Phase 8.7
└── graph/                ← Phase 11

generated/
├── {service}/            ← Phase 8
└── infrastructure/       ← Phase 8.7
```

## 関連スキル

- [/workflow](workflow.md) — 対話的にフェーズを選択して実行
- [/refactor-system](refactor-system.md) — コード生成なしの分析・設計実行
