---
name: refactor-system
description: 統合リファクタリングエージェント - 既存システムをマイクロサービスアーキテクチャにリファクタリングするための統合分析・設計を実行。/refactor-system [対象パス] で呼び出し。
user_invocable: true
---

# System Refactoring Orchestrator

既存システムをマイクロサービスアーキテクチャにリファクタリングするための統合エージェントです。

## 概要

このスキルは、既存の設計書やコードを分析し、以下のプロセスを通じてマイクロサービスアーキテクチャへの変換計画を策定します：

1. **システム分析** - 既存コードと設計書の解析
2. **MMI評価** - Modularity Maturity Indexによる成熟度評価
3. **ドメインマッピング** - ビジネスドメインとコードの紐付け
4. **マイクロサービス設計** - ターゲットアーキテクチャの策定
5. **ドメインストーリー** - 各ドメインのユースケース整理

## 使用方法

```
/refactor-system [対象パス] [オプション]
```

### オプション
- `--analyze-only` - 分析のみ実行（設計書生成なし）
- `--skip-mmi` - MMI評価をスキップ
- `--domain=[ドメイン名]` - 特定ドメインのみ対象
- `--output=[出力パス]` - 出力先ディレクトリ指定（デフォルト: `.refactoring-output/`）

## 出力ファイル構造

```
.refactoring-output/
├── 00_summary/
│   └── executive_summary.md          # エグゼクティブサマリー
├── 01_analysis/
│   ├── ubiquitous_language.md        # ユビキタス言語集
│   ├── actors_roles_permissions.md   # アクター・ロール・権限
│   ├── domain_code_mapping.md        # ドメイン-コード対応表
│   └── current_system_overview.md    # 現行システム概要
├── 02_evaluation/
│   ├── mmi_overview.md               # MMI全体サマリー
│   ├── mmi_by_module.md              # モジュール別MMI
│   └── mmi_improvement_plan.md       # MMI改善計画
├── 03_design/
│   ├── domain_analysis.md            # ドメイン分析
│   ├── system_mapping.md             # システムマッピング
│   ├── target_architecture.md        # ターゲットアーキテクチャ
│   ├── transformation_plan.md        # 変換計画
│   └── operations_feedback.md        # 運用・フィードバック計画
└── 04_stories/
    └── [domain]_story.md             # ドメイン別ストーリー
```

## 実行フロー

```mermaid
graph TD
    A[開始] --> B[入力確認]
    B --> C{設計書あり?}
    C -->|Yes| D[設計書解析]
    C -->|No| E[コード解析のみ]
    D --> F[システム分析エージェント]
    E --> F
    F --> G[MMI評価エージェント]
    G --> H[ドメインマッピングエージェント]
    H --> I[マイクロサービス設計エージェント]
    I --> J[ドメインストーリーエージェント]
    J --> K[最終レポート生成]
    K --> L[終了]
```

## 処理詳細

### Phase 1: 入力収集と初期分析

1. 対象ディレクトリのスキャン
2. 設計書ファイルの特定（`.md`, `.docx`, `.xlsx`, `.pdf` など）
3. ソースコードの構造解析
4. 使用技術スタックの特定

### Phase 2: システム分析

Taskツールで `system-analyzer` エージェントを起動し、以下を実行：
- ユビキタス言語の抽出
- アクター・ロール・権限の整理
- ドメイン境界の初期推定

### Phase 3: MMI評価

Taskツールで `mmi-evaluator` エージェントを起動し、以下を評価：
- **Cohesion（凝集度）** - 30%
- **Coupling（結合度）** - 30%
- **Independence（独立性）** - 20%
- **Reusability（再利用性）** - 20%

### Phase 4: ドメインマッピング

Taskツールで `domain-mapper` エージェントを起動し、以下を実行：
- 設計書の概念とコードの対応付け
- ドメインタイプの分類（Pipeline/Blackboard/Dialogue）
- マイクロサービス境界の分類（Process/Master/Integration/Supporting）

### Phase 5: マイクロサービス設計

Taskツールで `microservice-architect` エージェントを起動し、以下を策定：
- コンテキストマップ
- マクロアーキテクチャ
- データストレージ設計
- 移行計画

### Phase 6: ドメインストーリー

Taskツールで `domain-storyteller` エージェントを起動し、各ドメインについて：
- アクター特定
- ワークアイテム整理
- アクティビティフロー記述
- 例外シナリオ検討

## 依存スキル

このスキルは以下のサブスキルを使用します：
- `/analyze-system` - システム分析
- `/evaluate-mmi` - MMI評価
- `/map-domains` - ドメインマッピング
- `/design-microservices` - マイクロサービス設計
- `/create-domain-story` - ドメインストーリー作成

## 使用例

### 基本的な使用

```
/refactor-system ./src
```

### 特定ドメインのみ分析

```
/refactor-system ./src --domain=Order
```

### 分析のみ実行

```
/refactor-system ./src --analyze-only
```

## 注意事項

- 大規模なコードベースの場合、処理に時間がかかる場合があります
- 中間ファイルは `.refactoring-output/` に保存されます
- 既存の出力ファイルは上書きされます（バックアップ推奨）
- 設計書がない場合でもコードから推論可能ですが、精度が低下する可能性があります
