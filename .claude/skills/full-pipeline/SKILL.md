---
name: full-pipeline
description: 完全パイプライン実行 - 調査から設計・コード生成まで全フェーズを一括実行。/full-pipeline [対象パス] で呼び出し。
user_invocable: true
---

# Full Pipeline Execution Agent

レガシーシステムの調査から設計・コード生成まで、全フェーズを一括で実行する統合オーケストレーターです。

## 概要

このエージェントは以下のフェーズを順次実行します：

| フェーズ | スキル | 出力先 |
|---------|--------|--------|
| 0 | /system-investigation | reports/before/{project}/ |
| 0.5a | /security-analysis | reports/before/{project}/ |
| 0.5b | /access-control-analysis | reports/before/{project}/ |
| 1 | /analyze-system | reports/01_analysis/ |
| 1.5a | /data-model-analysis | reports/01_analysis/ |
| 1.5b | /db-design-analysis | reports/01_analysis/ |
| 1.5c | /er-diagram-analysis | reports/01_analysis/ |
| 2a | /evaluate-mmi | reports/02_evaluation/ |
| 2b | /ddd-evaluation | reports/02_evaluation/ |
| 2.5 | /integrate-evaluations | reports/02_evaluation/ |
| 3 | /ddd-redesign | reports/03_design/ |
| 4 | /design-microservices | reports/03_design/ |
| 4.7 | /select-scalardb-edition | work/{project}/ |
| 4.8 | /design-scalardb-app-patterns | reports/03_design/ |
| 5 | /design-scalardb | reports/03_design/ |
| 5.5 | /design-scalardb-analytics | reports/03_design/ (optional) |
| 5.9 | /review-scalardb --mode=design | reports/03_design/ |
| 5.95 | /design-api | reports/03_design/api-specifications/ |
| 6 | /design-implementation | reports/06_implementation/ |
| 7 | /generate-test-specs | reports/07_test-specs/ |
| 8 | /generate-scalardb-code | generated/{service}/ |
| 8.5 | /review-scalardb --mode=code | reports/03_design/ |
| 8.7 | /design-infrastructure | reports/08_infrastructure/, generated/infrastructure/ |
| 9 | /estimate-cost | reports/05_estimate/ |
| 10 | /create-domain-story | reports/04_stories/ |
| 11 | /build-graph | reports/graph/ |
| 12 | /fix-mermaid | (validation) |
| 13 | Executive Summary | reports/00_summary/ |

## 前提条件

### 必須
- 対象ディレクトリにソースコードまたは設計書が存在すること
- Python環境（graph構築用）: `pip install ryugraph pandas markdown pymdown-extensions`
- Node.js（Mermaid用）: `npm install -g @mermaid-js/mermaid-cli`

### 推奨
- Serena MCP Server（コード解析精度向上）

## 使用方法

```bash
# 基本実行（全フェーズ）
/full-pipeline ./path/to/source

# 出力先カスタマイズ
/full-pipeline ./path/to/source --output=./custom-output/

# 特定ドメインのみ
/full-pipeline ./path/to/source --domain=Order,Customer

# 分析のみ（設計・コード生成スキップ）
/full-pipeline ./path/to/source --analyze-only

# コード生成スキップ
/full-pipeline ./path/to/source --skip-codegen

# セキュリティ分析スキップ
/full-pipeline ./path/to/source --skip-security

# データモデル詳細分析スキップ
/full-pipeline ./path/to/source --skip-data-model

# Analytics不要
/full-pipeline ./path/to/source --skip-analytics

# ドメインストーリースキップ
/full-pipeline ./path/to/source --skip-stories

# インフラ設計スキップ
/full-pipeline ./path/to/source --skip-infrastructure

# グラフ構築スキップ
/full-pipeline ./path/to/source --skip-graph

# 特定フェーズから再開
/full-pipeline ./path/to/source --resume-from=phase-6
```

## 実行プロンプト

あなたは統合パイプラインオーケストレーターです。
レガシーシステムの調査から設計・コード生成まで、全フェーズを順次実行してください。

### Step 0: ユーザー入力確認（必須）

**重要**: 実行前に必ず以下の項目をユーザーに確認してください。

#### 1. 調査対象フォルダの確認

引数で対象パスが指定されていない場合、または確認が必要な場合は、以下を質問してください：

```
調査対象のフォルダを指定してください。
例: ./src, ./SampleCode, /path/to/project
```

AskUserQuestionツールを使用：
```json
{
  "questions": [{
    "question": "調査対象のフォルダパスを指定してください",
    "header": "対象フォルダ",
    "options": [
      {"label": "カレントディレクトリ", "description": "現在のディレクトリ全体を調査"},
      {"label": "src/", "description": "srcディレクトリを調査"},
      {"label": "パス指定", "description": "カスタムパスを入力"}
    ],
    "multiSelect": false
  }]
}
```

#### 2. 出力先ディレクトリの確認

デフォルト出力先: `./reports/`（カレントディレクトリ配下）

以下のように確認してください：

```
出力先ディレクトリを確認してください。
デフォルト: ./reports/（カレントディレクトリ配下）
変更する場合は別のパスを指定してください。
```

AskUserQuestionツールを使用：
```json
{
  "questions": [{
    "question": "レポートの出力先ディレクトリを確認してください",
    "header": "出力先",
    "options": [
      {"label": "./reports/ (推奨)", "description": "カレントディレクトリ配下のreportsフォルダ"},
      {"label": "カスタムパス", "description": "別のパスを指定"}
    ],
    "multiSelect": false
  }]
}
```

**実行への反映:**
- 対象フォルダ → Step 1 初期化の `対象パス` として全フェーズのソース解析対象に使用
- 出力先 → Step 1 初期化の `出力先` として `reports/`, `generated/`, `work/` のベースディレクトリに使用

### Step 1: 初期化

1. **引数の解析**
   ```
   対象パス: $ARGUMENTS または Step 0 で確認した値（必須）
   出力先: --output オプション または Step 0 で確認した値 (デフォルト: ./reports/, ./generated/)
   オプション: --domain, --analyze-only, --skip-codegen, --skip-security, --skip-data-model, --skip-analytics, --skip-infrastructure, --skip-stories, --skip-graph, --resume-from
   ```

2. **プロジェクト名の決定**
   - 対象パスから抽出（例: `./SampleCode/` → `SampleCode`）

3. **出力ディレクトリの初期化**
   ```bash
   mkdir -p reports/{before/$PROJECT,00_summary,01_analysis,02_evaluation,03_design/api-specifications,04_stories,05_estimate,06_implementation,07_test-specs,08_infrastructure,graph/data,graph/visualizations,sizing-estimates}
   mkdir -p generated generated/infrastructure
   mkdir -p work/$PROJECT
   ```

4. **進捗レジストリの初期化**
   ```json
   // work/{project}/pipeline-progress.json
   {
     "project": "{project}",
     "target_path": "{対象パス}",
     "started_at": "{ISO8601}",
     "options": {
       "analyze_only": false,
       "skip_codegen": false,
       "skip_analytics": false,
       "skip_stories": false,
       "skip_graph": false,
       "domains": []
     },
     "phases": {}
   }
   ```

### Step 2: Phase 0 - システム調査

**スキル**: `/system-investigation`

```
実行: /system-investigation {対象パス}
```

**出力ファイル**:
- `reports/before/{project}/technology-stack.md`
- `reports/before/{project}/codebase-structure.md`
- `reports/before/{project}/issues-and-debt.md`
- `reports/before/{project}/ddd-readiness.md`

**進捗更新**:
```json
{
  "phases": {
    "system-investigation": {
      "status": "completed",
      "started_at": "...",
      "completed_at": "...",
      "outputs": ["reports/before/{project}/..."]
    }
  }
}
```

### Step 3: Phase 0.5 - セキュリティ分析（オプション）

**スキル**: `/security-analysis`, `/access-control-analysis`

**重要**: これらは並行実行可能です。

```
並行実行:
  - /security-analysis {対象パス}
  - /access-control-analysis {対象パス}
```

**出力ファイル**:
- `reports/before/{project}/security-analysis.md`
- `reports/before/{project}/access-control-analysis.md`

**スキップ条件**: `--skip-security` オプション指定時

### Step 4: Phase 1 - システム分析

**スキル**: `/analyze-system`

```
実行: /analyze-system {対象パス}
```

**出力ファイル**:
- `reports/01_analysis/system-overview.md`
- `reports/01_analysis/ubiquitous-language.md`
- `reports/01_analysis/actors-roles-permissions.md`
- `reports/01_analysis/domain-code-mapping.md`

### Step 5: Phase 1.5 - データモデル詳細分析（オプション）

**スキル**: `/data-model-analysis`, `/db-design-analysis`, `/er-diagram-analysis`

**実行順序**: data-model-analysis → db-design-analysis → er-diagram-analysis（順次依存）

```
順次実行:
  1. /data-model-analysis {対象パス}
  2. /db-design-analysis {対象パス}
  3. /er-diagram-analysis {対象パス}
```

**出力ファイル**:
- `reports/01_analysis/data-model-analysis.md`
- `reports/01_analysis/db-design-analysis.md`
- `reports/01_analysis/er-diagram-current.md`

**スキップ条件**: `--skip-data-model` オプション指定時

### Step 6: Phase 2a/2b - 並行評価

**スキル**: `/evaluate-mmi`, `/ddd-evaluation`

**重要**: これらは並行実行可能です。

```
並行実行:
  - /evaluate-mmi {対象パス}
  - /ddd-evaluation {対象パス}
```

**出力ファイル**:
- `reports/02_evaluation/mmi-overview.md`
- `reports/02_evaluation/mmi-by-module.md`
- `reports/02_evaluation/mmi-improvement-plan.md`
- `reports/02_evaluation/ddd-strategic-evaluation.md`
- `reports/02_evaluation/ddd-tactical-evaluation.md`
- `reports/02_evaluation/ddd-improvement-plan.md`

### Step 7: Phase 2.5 - 評価統合

**スキル**: `/integrate-evaluations`

**前提**: Phase 2a と Phase 2b の両方が完了していること

```
実行: /integrate-evaluations {対象パス}
```

**出力ファイル**:
- `reports/02_evaluation/integrated-evaluation.md`
- `reports/02_evaluation/priority-matrix.md`
- `reports/02_evaluation/unified-improvement-plan.md`

### Step 8: Phase 3 - DDD再設計

**スキル**: `/ddd-redesign`

```
実行: /ddd-redesign {対象パス}
```

**出力ファイル**:
- `reports/03_design/domain-analysis.md`
- `reports/03_design/bounded-contexts-redesign.md`
- `reports/03_design/context-map.md`
- `reports/03_design/aggregate-redesign.md`
- `reports/03_design/ubiquitous-language-refined.md`
- `reports/03_design/system-mapping.md`
- `reports/03_design/ddd-migration-roadmap.md`

### Step 9: Phase 4 - マイクロサービス設計

**スキル**: `/design-microservices`

```
実行: /design-microservices {対象パス}
```

**出力ファイル**:
- `reports/03_design/target-architecture.md`
- `reports/03_design/transformation-plan.md`
- `reports/03_design/operations-feedback.md`

### Step 10: Phase 4.7 - ScalarDBエディション選定

**スキル**: `/select-scalardb-edition`

```
実行: /select-scalardb-edition
```

**出力ファイル**:
- `work/{project}/scalardb-edition-config.md`

**注意**: 対話形式のスキルです。ユーザーに要件を確認し、最適なエディション（OSS/Enterprise Standard/Premium）を選定します。

### Step 11: Phase 4.8 - ScalarDBアプリケーション設計パターン

**スキル**: `/design-scalardb-app-patterns`

**前提**: Phase 4.7（エディション選定）が完了していること

```
実行: /design-scalardb-app-patterns {対象パス}
```

**出力ファイル**:
- `reports/03_design/scalardb-app-patterns.md`
- `reports/03_design/scalardb-database-selection.md`

**注意**: Phase 5（ScalarDB設計）と並行実行も可能ですが、パイプラインでは順次実行します。

### Step 12: Phase 5 - ScalarDB設計

**スキル**: `/design-scalardb`

```
実行: /design-scalardb {対象パス}
```

**出力ファイル**:
- `reports/03_design/scalardb-architecture.md`
- `reports/03_design/scalardb-schema.md`
- `reports/03_design/scalardb-transaction.md`
- `reports/03_design/scalardb-migration.md`

### Step 13: Phase 5.5 - ScalarDB Analytics設計（オプション）

**条件**: `--skip-analytics` が指定されていない場合

**スキル**: `/design-scalardb-analytics`

```
実行: /design-scalardb-analytics {対象パス}
```

**出力ファイル**:
- `reports/03_design/scalardb-analytics-architecture.md`
- `reports/03_design/scalardb-analytics-queries.md`

### Step 14: Phase 5.9 - ScalarDB設計レビュー

**スキル**: `/review-scalardb --mode=design`

**前提**: Phase 5（ScalarDB設計）が完了していること

```
実行: /review-scalardb --mode=design
```

**出力ファイル**:
- `reports/03_design/scalardb-design-review.md`

**注意**: 設計品質を検証し、エディション整合性・Key設計・トランザクション境界をチェックします。Context7で最新仕様も参照します。

### Step 15: Phase 5.95 - API設計

**スキル**: `/design-api`

**前提**: Phase 5.9（ScalarDB設計レビュー）が完了していること。ScalarDBスキーマ設計の結果を踏まえてAPI設計を行う。

```
実行: /design-api {対象パス}
```

**出力ファイル**:
- `reports/03_design/api-design-overview.md`
- `reports/03_design/api-gateway-design.md`
- `reports/03_design/api-security-design.md`
- `reports/03_design/api-specifications/*.yaml`

### Step 16: Phase 6 - 実装仕様

**条件**: `--analyze-only` が指定されていない場合

**スキル**: `/design-implementation`

```
実行: /design-implementation {対象パス}
```

**出力ファイル**:
- `reports/06_implementation/domain-services-spec.md`
- `reports/06_implementation/repository-interfaces-spec.md`
- `reports/06_implementation/value-objects-spec.md`
- `reports/06_implementation/exception-mapping.md`
- `reports/06_implementation/saga-orchestration-spec.md`
- `reports/06_implementation/implementation-checklist.md`
- `reports/06_implementation/api-gateway-implementation-spec.md`

### Step 17: Phase 7 - テスト仕様

**条件**: `--analyze-only` が指定されていない場合

**スキル**: `/generate-test-specs`

```
実行: /generate-test-specs {対象パス}
```

**出力ファイル**:
- `reports/07_test-specs/bdd-scenarios/*.feature`
- `reports/07_test-specs/unit-test-specs.md`
- `reports/07_test-specs/integration-test-specs.md`
- `reports/07_test-specs/edge-case-specs.md`
- `reports/07_test-specs/performance-test-specs.md`
- `reports/07_test-specs/test-data-requirements.md`

### Step 18: Phase 8 - コード生成

**条件**: `--analyze-only` および `--skip-codegen` が指定されていない場合

**スキル**: `/generate-scalardb-code`

```
実行: /generate-scalardb-code {対象パス}
```

**出力ファイル**:
- `generated/{service}/src/main/java/...`
- `generated/{service}/src/test/java/...`
- `generated/{service}/src/main/resources/...`
- `generated/{service}/build.gradle`
- `generated/{service}/Dockerfile`
- `generated/{service}/k8s/...`
- `generated/{service}/GENERATED.md`

### Step 19: Phase 8.5 - ScalarDBコードレビュー

**条件**: Phase 8（コード生成）が完了している場合

**スキル**: `/review-scalardb --mode=code`

```
実行: /review-scalardb --mode=code
```

**出力ファイル**:
- `reports/03_design/scalardb-code-review.md`

**注意**: 生成コードの品質を検証し、coding-patterns準拠・エディション別API使用・トランザクション管理をチェックします。

### Step 19.5: Phase 8.7 - インフラ基盤構成設計（オプション）

**条件**: `--skip-infrastructure` が指定されていない場合

**スキル**: `/design-infrastructure`

```
実行: /design-infrastructure
```

入力:
- `reports/03_design/target-architecture.md` ← Phase 4
- `reports/03_design/scalardb-schema.md` ← Phase 5
- `work/{project}/scalardb-edition-config.md` ← Phase 4.7
- `reports/sizing-estimates/*.md` ← 事前に `/scalardb-sizing-estimator` 実行済みの場合のみ

**出力ファイル**:
- `reports/08_infrastructure/infrastructure-architecture.md`
- `reports/08_infrastructure/deployment-guide.md`
- `reports/08_infrastructure/environment-matrix.md`
- `reports/08_infrastructure/security-configuration.md`
- `generated/infrastructure/k8s/` — Kubernetes manifests
- `generated/infrastructure/terraform/` — IaC modules & environments

**スキップ条件**: `--skip-infrastructure` オプション指定時

### Step 20: Phase 9 - コスト見積もり

**スキル**: `/estimate-cost`

```
実行: /estimate-cost ./reports
```

**出力ファイル**:
- `reports/05_estimate/cost-summary.md`
- `reports/05_estimate/infrastructure-detail.md`
- `reports/05_estimate/license-requirements.md`

### Step 21: Phase 10 - ドメインストーリー（オプション）

**条件**: `--skip-stories` が指定されていない場合

**スキル**: `/create-domain-story`

各ドメインに対して実行:
```
実行: /create-domain-story --domain={domain}
```

**出力ファイル**:
- `reports/04_stories/{domain}-story.md`

### Step 22: Phase 11 - ナレッジグラフ構築（オプション）

**条件**: `--skip-graph` が指定されていない場合

**スキル**: `/build-graph`

```
実行: /build-graph {対象パス}
```

**出力ファイル**:
- `reports/graph/data/*.csv`
- `knowledge.ryugraph/`

### Step 23: Phase 12 - Mermaid検証・修正

**スキル**: `/fix-mermaid`

```
実行: /fix-mermaid ./reports
```

全Markdownファイル内のMermaid図を検証・修正。

### Step 24: Phase 13 - エグゼクティブサマリー生成

**出力**: `reports/00_summary/executive-summary.md`

以下の情報を統合したサマリーを生成:

```markdown
# {プロジェクト名} リファクタリング分析レポート

## エグゼクティブサマリー

### 分析日時
{ISO8601}

### 対象システム
- パス: {対象パス}
- 技術スタック: {technology-stack.mdから}
- コード行数: {概算}

### 評価結果
| 指標 | スコア | 評価 |
|------|--------|------|
| MMI総合 | {score}/100 | {level} |
| DDD適合性 | {score}/100 | {level} |
| リファクタリング推奨度 | {High/Medium/Low} | |

### 推奨アーキテクチャ
{target-architecture.mdから要約}

### 識別された境界コンテキスト
{bounded-contexts-redesign.mdからリスト}

### 推定コスト
| 項目 | 月額 | 年額 |
|------|------|------|
| インフラ | ${cost} | ${cost} |
| ライセンス | ${cost} | ${cost} |
| **合計** | **${cost}** | **${cost}** |

### 次のステップ
1. 生成コードのレビュー (`generated/`)
2. ScalarDBスキーマの作成
3. CI/CDパイプラインの構築
4. 段階的移行の開始

### 生成ファイル一覧
{全出力ファイルのリスト}

### 実行ログ
{pipeline-progress.jsonから}
```

### Step 25: 最終レポートのコンパイル

**スキル**: `/compile-report`

```
実行: /compile-report
```

**出力ファイル**:
- `reports/00_summary/full-report.html`

### Step 26: 完了通知

進捗レジストリを最終更新:
```json
{
  "completed_at": "{ISO8601}",
  "status": "completed",
  "summary": {
    "total_phases": 13,
    "completed_phases": 13,
    "skipped_phases": [],
    "output_files_count": {n},
    "generated_services": ["{service1}", "{service2}"]
  }
}
```

## エラーハンドリング

### 前提条件エラー
- 対象パスが存在しない → エラー終了、メッセージ表示
- 必須ツールがない → 警告表示、該当フェーズスキップ

### フェーズ実行エラー
- フェーズ失敗時 → 進捗レジストリに記録、次フェーズ継続可否を判断
- 依存フェーズ失敗 → 後続フェーズをスキップ

### 再開時の動作
- `--resume-from` 指定時 → 指定フェーズから再開
- 進捗レジストリに `completed` がある → そのフェーズをスキップ

## 出力構造

```
./
├── reports/
│   ├── before/{project}/        ← Phase 0
│   ├── 00_summary/              ← Phase 13
│   ├── 01_analysis/             ← Phase 1
│   ├── 02_evaluation/           ← Phase 2a, 2b, 2.5
│   ├── 03_design/               ← Phase 3, 4, 4.8, 5, 5.5, 5.9, 5.95, 8.5
│   │   └── api-specifications/
│   ├── 04_stories/              ← Phase 10
│   ├── 05_estimate/             ← Phase 9
│   ├── 06_implementation/       ← Phase 6
│   ├── 07_test-specs/           ← Phase 7
│   │   └── bdd-scenarios/
│   ├── 08_infrastructure/       ← Phase 8.7
│   ├── graph/                   ← Phase 11
│   │   ├── data/
│   │   └── visualizations/
│   └── sizing-estimates/        ← ScalarDBサイジング
├── generated/                   ← Phase 8, 8.7
│   ├── {service}/
│   │   ├── src/
│   │   ├── build.gradle
│   │   ├── Dockerfile
│   │   ├── k8s/
│   │   └── GENERATED.md
│   └── infrastructure/          ← Phase 8.7
│       ├── k8s/
│       ├── terraform/
│       └── openshift/
├── work/{project}/              ← 中間状態
│   └── pipeline-progress.json
└── knowledge.ryugraph/          ← Phase 11

```

## 所要時間目安

| フェーズ | 小規模 | 中規模 | 大規模 |
|---------|--------|--------|--------|
| Phase 0-1 | 5分 | 15分 | 30分 |
| Phase 2a-2.5 | 10分 | 30分 | 60分 |
| Phase 3-5.5 | 15分 | 45分 | 90分 |
| Phase 6-8 | 20分 | 60分 | 120分 |
| Phase 9-13 | 10分 | 30分 | 60分 |
| **合計** | **60分** | **3時間** | **6時間** |

※ AIエージェントの処理速度、対象システムの複雑さにより変動

## 関連スキル

| スキル | 用途 |
|--------|------|
| `/refactor-system` | 従来の統合オーケストレーター（コード生成なし） |
| `/scalardb-sizing-estimator` | 対話式サイジング見積もり |
| `/query-graph` | 生成されたナレッジグラフへのクエリ |
| `/visualize-graph` | グラフの可視化 |
