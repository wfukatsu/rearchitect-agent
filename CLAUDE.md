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
| Domain Storyteller | `/create-domain-story` | ドメインストーリーテリング |

### ユーティリティスキル

| スキル | コマンド | 説明 |
|-------|--------|------|
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
```

## 出力先

すべての出力は `.refactoring-output/` ディレクトリに保存されます。

```
.refactoring-output/
├── 00_summary/         # エグゼクティブサマリー
├── 01_analysis/        # システム分析結果
├── 02_evaluation/      # MMI評価結果
├── 03_design/          # マイクロサービス設計
├── 04_stories/         # ドメインストーリー
└── 99_appendix/        # 付録
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
    E --> F[/create-domain-story]
    F --> G[Executive Summary生成]
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

## 参考資料

- [Modularity Maturity Index](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/modularity-maturity-index.md)
- [Domain-Driven Transformation](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/domain-driven-transformation.md)
- [Domain Storytelling](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/domain-storytelling.md)

## バージョン

- バージョン: 1.0.0
- 作成日: 2024
- 作成者: Claude Code
