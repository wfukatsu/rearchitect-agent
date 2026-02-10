---
name: workflow
description: インタラクティブワークフロー選択 - 実行したい処理を段階的に選択して実行。/workflow で呼び出し。
user_invocable: true
---

# Interactive Workflow Selection Agent

レガシーシステムのリファクタリング分析・設計・実装において、実行したい処理を対話的に選択して段階的に実行するワークフローオーケストレーターです。

## 概要

このエージェントは、ユーザーが実行したい処理を選択し、段階的にプロジェクトを進めることができるインタラクティブなワークフローを提供します。

## 使用方法

```bash
# 基本実行（対話的に選択）
/workflow

# 対象パス指定
/workflow ./path/to/source

# 出力先指定
/workflow ./path/to/source --output=./custom-output/
```

## 実行プロンプト

あなたはインタラクティブワークフローオーケストレーターです。
ユーザーが実行したい処理を段階的に選択し、適切なスキルを実行してください。

### Step 1: 実行タイプの選択（必須）

**必ず最初にユーザーに実行タイプを質問してください。**

AskUserQuestionツールを使用して以下を質問：

```json
{
  "questions": [{
    "question": "実行したい処理タイプを選択してください",
    "header": "ワークフロー",
    "options": [
      {
        "label": "完全パイプライン実行 (推奨)",
        "description": "調査→分析→評価→設計→実装→コード生成まで全フェーズを一括実行"
      },
      {
        "label": "分析・評価まで実行",
        "description": "Phase 0-2: システム調査→分析→MMI/DDD評価→評価統合まで"
      },
      {
        "label": "設計から実行",
        "description": "Phase 3-8: DDD再設計→ScalarDB設計→実装→コード生成（実行範囲を追加選択）"
      },
      {
        "label": "個別フェーズ選択",
        "description": "サイジング見積もり・ドメインストーリー等を含む全フェーズから個別に選択"
      }
    ],
    "multiSelect": false
  }]
}
```

### Step 2: 対象パスの確認

ユーザーが引数で対象パスを指定していない場合、以下を質問：

```json
{
  "questions": [{
    "question": "調査対象のフォルダパスを指定してください",
    "header": "対象フォルダ",
    "options": [
      {
        "label": "カレントディレクトリ (.)",
        "description": "現在のディレクトリ全体を調査"
      },
      {
        "label": "src/",
        "description": "srcディレクトリを調査"
      },
      {
        "label": "カスタムパス",
        "description": "別のパスを指定（テキスト入力）"
      }
    ],
    "multiSelect": false
  }]
}
```

### Step 3: 出力先の確認（オプション）

デフォルト出力先: `./reports/`

変更する場合のみ質問：

```json
{
  "questions": [{
    "question": "レポートの出力先ディレクトリを確認してください",
    "header": "出力先",
    "options": [
      {
        "label": "./reports/ (推奨)",
        "description": "カレントディレクトリ配下のreportsフォルダ"
      },
      {
        "label": "カスタムパス",
        "description": "別のパスを指定"
      }
    ],
    "multiSelect": false
  }]
}
```

**実行への反映:**
- 完全パイプライン実行 → `/full-pipeline` に委譲（Phase 0〜13 全フェーズ）
- 分析・評価まで実行 → Phase 0〜2.5 のスキルを順次実行
- 設計から実行 → Step 4.3a でスコープを追加質問後、該当フェーズを実行（前提: Phase 1-2 完了済み）
- 個別フェーズ選択 → Step 4.7a/4.7b でカテゴリ→フェーズを2段階で選択

### Step 4: 選択に基づく実行

#### 4.1 完全パイプライン実行の場合

**スキル呼び出し**: `/full-pipeline {対象パス}`

実行内容:
- Phase 0: システム調査
- Phase 1: システム分析
- Phase 2a/2b: MMI評価 + DDD評価
- Phase 2.5: 評価統合
- Phase 3: DDD再設計
- Phase 4: マイクロサービス設計
- Phase 4.7: ScalarDBエディション選定
- Phase 4.8: ScalarDBアプリパターン設計
- Phase 5: ScalarDB設計
- Phase 5.5: ScalarDB Analytics設計
- Phase 5.9: ScalarDB設計レビュー
- Phase 5.95: API設計
- Phase 6: 実装仕様
- Phase 7: テスト仕様
- Phase 8: コード生成
- Phase 8.5: ScalarDBコードレビュー
- Phase 8.7: インフラ基盤構成設計
- Phase 9: コスト見積もり
- Phase 10: ドメインストーリー
- Phase 11: ナレッジグラフ構築
- Phase 12: Mermaid検証
- Phase 13: エグゼクティブサマリー

#### 4.2 分析・評価まで実行の場合

**スキル呼び出し**:
1. `/system-investigation {対象パス}`
2. `/analyze-system {対象パス}`
3. `/evaluate-mmi {対象パス}` と `/ddd-evaluation {対象パス}` を並行実行
4. `/integrate-evaluations {対象パス}`

実行後、次のステップを提案：

```
分析が完了しました。

次のステップ:
1. DDD再設計の実行 (/ddd-redesign)
2. マイクロサービス設計の実行 (/design-microservices)
3. エグゼクティブサマリーのみ生成
4. ここで終了

どれを実行しますか？
```

#### 4.3 設計から実行の場合

**前提条件**: Phase 1-2 (分析・評価) の結果が存在すること

##### Step 4.3a: 実行スコープの選択

```json
{
  "questions": [{
    "question": "どこまで実行しますか？",
    "header": "スコープ",
    "options": [
      {"label": "設計のみ (推奨)", "description": "Phase 3-5.95: DDD再設計→マイクロサービス→ScalarDB→API設計"},
      {"label": "実装仕様まで", "description": "Phase 3-7: 設計 + 実装仕様書 + テスト仕様書の生成"},
      {"label": "コード生成まで", "description": "Phase 3-8: 設計 + 実装仕様 + Spring Boot/ScalarDBコード生成"},
      {"label": "見積もりまで含む", "description": "Phase 3-9: 設計 + 実装 + コード生成 + インフラ費用見積もり"}
    ],
    "multiSelect": false
  }]
}
```

**設計フェーズ（Phase 3-5.95）の実行**:
1. `/ddd-redesign {対象パス}`
2. `/design-microservices {対象パス}`
3. `/select-scalardb-edition` （ScalarDBエディション選定）
4. `/design-scalardb-app-patterns {対象パス}` （ドメインタイプ別設計パターン）
5. `/design-scalardb {対象パス}` （ScalarDBスキーマ・トランザクション設計）
6. `/review-scalardb --mode=design` （ScalarDB設計レビュー）
7. `/design-api {対象パス}` （ScalarDBスキーマ設計結果を踏まえたAPI設計）

オプションで質問：

```json
{
  "questions": [{
    "question": "ScalarDB Analyticsの設計も含めますか？",
    "header": "Analytics",
    "options": [
      {"label": "含める", "description": "分析基盤の設計も実施"},
      {"label": "含めない", "description": "OLTPのみ"}
    ],
    "multiSelect": false
  }]
}
```

含める場合: `/design-scalardb-analytics {対象パス}` を追加実行

オプションで質問：

```json
{
  "questions": [{
    "question": "インフラ基盤構成（IaC）の設計も含めますか？",
    "header": "インフラ",
    "options": [
      {"label": "含める", "description": "Terraform/Kubernetes/OpenShift構成を生成"},
      {"label": "含めない (推奨)", "description": "アプリケーション設計のみ"}
    ],
    "multiSelect": false
  }]
}
```

含める場合: `/design-infrastructure` を追加実行（コード生成後）

**実装仕様フェーズ（Phase 6-7）の実行**（スコープに含まれる場合）:
1. `/design-implementation {対象パス}`
2. `/generate-test-specs {対象パス}`

**コード生成フェーズ（Phase 8）の実行**（スコープに含まれる場合）:
1. `/generate-scalardb-code {対象パス}`

**見積もりフェーズ（Phase 9）の実行**（スコープに含まれる場合）:
1. `/scalardb-sizing-estimator`

実行後、完了通知と次のステップを提案。

#### 4.7 個別フェーズ選択の場合

2段階の選択で実行フェーズを絞り込む。

##### Step 4.7a: カテゴリ選択

```json
{
  "questions": [{
    "question": "実行したいフェーズのカテゴリを選択してください（複数選択可）",
    "header": "カテゴリ",
    "options": [
      {"label": "調査・分析", "description": "Phase 0-1.5: システム調査、セキュリティ分析、システム分析、データモデル分析"},
      {"label": "評価", "description": "Phase 2-2.5: MMI評価、DDD評価、評価統合"},
      {"label": "設計", "description": "Phase 3-5.95: DDD再設計、マイクロサービス、ScalarDB、API設計"},
      {"label": "実装・生成・その他", "description": "Phase 6-12: 実装仕様、コード生成、見積もり、グラフ構築"}
    ],
    "multiSelect": true
  }]
}
```

##### Step 4.7b: フェーズ選択（カテゴリ別）

選択されたカテゴリに応じて、以下のAskUserQuestionを表示する。

**「調査・分析」が選択された場合:**

```json
{
  "questions": [{
    "question": "調査・分析フェーズを選択してください（複数選択可）",
    "header": "調査・分析",
    "options": [
      {"label": "Phase 0: システム調査", "description": "technology-stack, codebase-structure, issues-and-debt"},
      {"label": "Phase 0.5: セキュリティ分析", "description": "OWASP Top 10 + ゼロトラスト + アクセス制御"},
      {"label": "Phase 1: システム分析", "description": "ubiquitous-language, domain-code-mapping, actors"},
      {"label": "Phase 1.5: データモデル分析", "description": "データモデル + DB設計 + ER図"}
    ],
    "multiSelect": true
  }]
}
```

**「評価」が選択された場合:**

```json
{
  "questions": [{
    "question": "評価フェーズを選択してください（複数選択可）",
    "header": "評価",
    "options": [
      {"label": "Phase 2a: MMI評価", "description": "モジュール成熟度指標の4軸評価"},
      {"label": "Phase 2b: DDD評価", "description": "DDD原則への適合性評価"},
      {"label": "Phase 2.5: 評価統合", "description": "MMI + DDD結果を統合し改善計画を策定"}
    ],
    "multiSelect": true
  }]
}
```

**「設計」が選択された場合:**

```json
{
  "questions": [{
    "question": "設計フェーズを選択してください（複数選択可）",
    "header": "設計",
    "options": [
      {"label": "Phase 3-4: DDD再設計 + マイクロサービス", "description": "境界コンテキスト、集約設計、ターゲットアーキテクチャ"},
      {"label": "Phase 4.7-4.8: ScalarDB選定 + パターン", "description": "エディション選定、ドメイン別設計パターン・DB選定"},
      {"label": "Phase 5-5.9: ScalarDB設計 + レビュー", "description": "スキーマ・トランザクション設計 + Analytics + 設計レビュー"},
      {"label": "Phase 5.95: API設計", "description": "REST/GraphQL/gRPC/AsyncAPI仕様書"}
    ],
    "multiSelect": true
  }]
}
```

**「実装・生成・その他」が選択された場合:**

```json
{
  "questions": [{
    "question": "実装・生成・その他のフェーズを選択してください（複数選択可）",
    "header": "実装・その他",
    "options": [
      {"label": "Phase 6-7: 実装仕様 + テスト仕様", "description": "ドメインサービス仕様、BDD/統合テスト仕様"},
      {"label": "Phase 8-8.7: コード生成 + インフラ設計", "description": "Spring Boot/ScalarDBコード + レビュー + Kubernetes/IaC構成"},
      {"label": "Phase 9-10: 見積もり + ストーリー", "description": "コスト見積もり + ドメインストーリーテリング"},
      {"label": "Phase 11-12: グラフ + Mermaid", "description": "ナレッジグラフ構築 + Mermaid検証・修正"}
    ],
    "multiSelect": true
  }]
}
```

選択されたフェーズを依存関係順に実行。

### Step 5: 進捗管理

各フェーズ実行時、進捗を記録：

```json
// work/{project}/workflow-progress.json
{
  "workflow_type": "complete|analysis-only|design-only|...",
  "target_path": "{対象パス}",
  "output_path": "{出力先}",
  "started_at": "{ISO8601}",
  "current_phase": "phase-3",
  "completed_phases": ["phase-0", "phase-1", "phase-2a", "phase-2b", "phase-2.5"],
  "pending_phases": ["phase-3", "phase-4", ...],
  "user_selections": {
    "include_analytics": true,
    "include_stories": true,
    "include_graph": true
  }
}
```

### Step 6: 完了後の提案

各実行タイプ完了後、次のステップを提案：

**分析完了後**:
- 設計フェーズへ進む
- エグゼクティブサマリーのみ生成
- 終了

**設計完了後**:
- 実装仕様生成へ進む
- コスト見積もり実行
- 終了

**実装仕様完了後**:
- コード生成へ進む
- 終了

**コード生成完了後**:
- ナレッジグラフ構築
- HTML総合レポート生成
- 終了

**サイジング見積もり完了後**:
- HTMLレポート確認
- 別のワークフロー実行
- 終了

### Step 7: エグゼクティブサマリー生成（オプション）

任意のタイミングで実行可能。

以下の質問で確認：

```json
{
  "questions": [{
    "question": "エグゼクティブサマリーを生成しますか？",
    "header": "サマリー",
    "options": [
      {"label": "生成する", "description": "これまでの結果を統合したサマリーを作成"},
      {"label": "スキップ", "description": "サマリーは後で生成"}
    ],
    "multiSelect": false
  }]
}
```

生成する場合、`reports/00_summary/executive-summary.md` を作成。

### Step 8: HTML総合レポート生成（オプション）

以下の質問で確認：

```json
{
  "questions": [{
    "question": "HTML総合レポートを生成しますか？",
    "header": "HTMLレポート",
    "options": [
      {"label": "生成する", "description": "全Markdownレポートを統合したHTMLを作成"},
      {"label": "スキップ", "description": "Markdownのみで十分"}
    ],
    "multiSelect": false
  }]
}
```

生成する場合、`/compile-report` を実行。

## フェーズ依存関係

実行可能なフェーズの前提条件：

| フェーズ | 前提条件 |
|---------|---------|
| Phase 0 | なし |
| Phase 1 | Phase 0完了推奨（なくても実行可） |
| Phase 2a/2b | Phase 1完了推奨 |
| Phase 2.5 | Phase 2a, 2b完了 |
| Phase 3 | Phase 2完了推奨 |
| Phase 4 | Phase 3完了 |
| Phase 4.7 | なし（ただしPhase 4完了推奨） |
| Phase 4.8 | Phase 4.7完了 |
| Phase 5 | Phase 4完了（Phase 4.7推奨） |
| Phase 5.5 | Phase 5完了 |
| Phase 5.9 | Phase 5完了 |
| Phase 5.95 | Phase 5.9完了 |
| Phase 6 | Phase 3-5.95完了 |
| Phase 7 | Phase 6完了 |
| Phase 8 | Phase 6-7完了 |
| Phase 8.5 | Phase 8完了 |
| Phase 8.7 | Phase 4完了（target-architecture.md） |
| Phase 9 | Phase 3-5完了推奨 |
| Phase 10 | Phase 3完了 |
| Phase 11 | Phase 1完了 |
| Phase 12 | Markdownファイル存在 |

**依存関係チェック**: 選択されたフェーズの前提条件が満たされていない場合、警告を表示し、前提フェーズの実行を提案。

## エラーハンドリング

### 前提条件未満足
```
警告: Phase 4を実行するにはPhase 3の完了が必要です。

以下のいずれかを選択してください:
1. Phase 3から実行する
2. Phase 4のみ実行する（リスクあり）
3. キャンセル
```

### フェーズ実行失敗
```
エラー: Phase 2a (MMI評価) が失敗しました。

選択肢:
1. Phase 2aをスキップして次へ進む
2. Phase 2aをリトライする
3. ワークフローを中断
```

### 対象パス不存在
```
エラー: 指定されたパス '{パス}' が存在しません。

対象パスを再指定してください。
```

## 出力構造

```
./
├── reports/
│   ├── before/{project}/        ← Phase 0
│   ├── 00_summary/              ← エグゼクティブサマリー
│   ├── 01_analysis/             ← Phase 1
│   ├── 02_evaluation/           ← Phase 2a, 2b, 2.5
│   ├── 03_design/               ← Phase 3, 4, 4.8, 5, 5.5, 5.9, 5.95, 8.5
│   ├── 04_stories/              ← Phase 10
│   ├── 05_estimate/             ← Phase 9
│   ├── 06_implementation/       ← Phase 6
│   ├── 07_test-specs/           ← Phase 7
│   ├── 08_infrastructure/       ← Phase 8.7
│   └── graph/                   ← Phase 11
├── generated/                   ← Phase 8, 8.7
│   ├── {service}/
│   └── infrastructure/          ← Phase 8.7
└── work/{project}/              ← 進捗管理
    └── workflow-progress.json
```

## 実行例

### 例1: 完全パイプライン

```
User: /workflow ./src

Agent: [実行タイプ選択を質問]
User: 完全パイプライン実行

Agent: [出力先確認]
User: ./reports/ (推奨)

Agent: [全フェーズ実行開始]
...
Agent: 完了しました。reports/00_summary/full-report.html を確認してください。
```

### 例2: 分析・評価→設計

```
User: /workflow ./src

Agent: [実行タイプ選択を質問]
User: 分析・評価まで実行

Agent: [Phase 0-2.5 実行]
Agent: 分析完了。次のステップは？
User: DDD再設計の実行

Agent: [Phase 3-5.5 実行]
Agent: 設計完了。次のステップは？
User: ここで終了
```

### 例3: サイジング見積もり（個別フェーズ選択）

```
User: /workflow

Agent: [実行タイプ選択を質問]
User: 個別フェーズ選択

Agent: [カテゴリ選択を質問 (Step 4.7a)]
User: 実装・生成・その他

Agent: [フェーズ選択を質問 (Step 4.7b)]
User: Phase 9-10: 見積もり + ストーリー

Agent: [/scalardb-sizing-estimator 実行]
Agent: [対話的にパラメータ収集]
Agent: 見積もり完了。reports/sizing-estimates/ を確認してください。
```

## 関連スキル

| スキル | 用途 |
|--------|------|
| `/full-pipeline` | 非対話的な完全パイプライン実行 |
| `/refactor-system` | 従来の統合オーケストレーター（コード生成なし） |
| `/scalardb-sizing-estimator` | 対話式サイジング見積もり |
| 個別フェーズスキル | 各フェーズの詳細仕様を参照 |

## 備考

- **柔軟性**: ユーザーは任意のタイミングでワークフローを中断・再開可能
- **段階的実行**: 大規模プロジェクトでは、分析→設計→実装と段階的に進めることを推奨
- **進捗保存**: `work/{project}/workflow-progress.json` で進捗を管理し、中断時も再開可能
- **カスタマイズ**: 各フェーズの詳細オプションは、該当スキルのSKILL.mdを参照
