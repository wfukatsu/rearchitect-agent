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
        "label": "完全パイプライン実行",
        "description": "調査→分析→評価→設計→実装→コード生成まで全フェーズを一括実行（推奨）"
      },
      {
        "label": "分析のみ実行",
        "description": "Phase 0-2: システム調査→分析→MMI/DDD評価まで実行"
      },
      {
        "label": "設計のみ実行",
        "description": "Phase 3-5: DDD再設計→マイクロサービス設計→API/DB設計"
      },
      {
        "label": "実装仕様生成",
        "description": "Phase 6-7: 実装仕様書→テスト仕様書の生成"
      },
      {
        "label": "コード生成のみ",
        "description": "Phase 8: Spring Boot/ScalarDBコードの生成"
      },
      {
        "label": "サイジング見積もり",
        "description": "ScalarDB Cluster/Analytics/インフラのサイジングと費用見積もり"
      },
      {
        "label": "個別フェーズ選択",
        "description": "実行したい個別フェーズを選択"
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
- 分析のみ実行 → Phase 0〜2.5 のスキルを順次実行
- 設計のみ実行 → Phase 3〜5.95 のスキルを順次実行（前提: Phase 1-2 完了済み）
- 実装仕様生成 → Phase 6〜7 のスキルを順次実行（前提: Phase 3-5 完了済み）
- コード生成のみ → Phase 8 の `/generate-scalardb-code` を実行（前提: Phase 6 完了済み）
- サイジング見積もり → `/scalardb-sizing-estimator` を実行（独立実行可能）
- 個別フェーズ選択 → Step 4.2 で個別フェーズを追加質問

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
- Phase 9: コスト見積もり
- Phase 10: ドメインストーリー
- Phase 11: ナレッジグラフ構築
- Phase 12: Mermaid検証
- Phase 13: エグゼクティブサマリー

#### 4.2 分析のみ実行の場合

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

#### 4.3 設計のみ実行の場合

**前提条件**: Phase 1-2 (分析・評価) の結果が存在すること

**スキル呼び出し**:
1. `/ddd-redesign {対象パス}`
2. `/design-microservices {対象パス}`
3. `/select-scalardb-edition` （ScalarDBエディション選定）
4. `/design-api {対象パス}`
5. `/design-scalardb {対象パス}` と `/design-scalardb-app-patterns {対象パス}` を並行実行
6. `/review-scalardb --mode=design` （ScalarDB設計レビュー）

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

実行後、次のステップを提案：

```
設計が完了しました。

次のステップ:
1. 実装仕様の生成 (/design-implementation)
2. コスト見積もりの実行 (/estimate-cost)
3. ドメインストーリーの作成
4. ここで終了

どれを実行しますか？
```

#### 4.4 実装仕様生成の場合

**前提条件**: Phase 3-5 (設計) の結果が存在すること

**スキル呼び出し**:
1. `/design-implementation {対象パス}`
2. `/generate-test-specs {対象パス}`

実行後、次のステップを提案：

```
実装仕様・テスト仕様が完了しました。

次のステップ:
1. コード生成の実行 (/generate-scalardb-code)
2. コスト見積もりの実行 (/estimate-cost)
3. ここで終了

どれを実行しますか？
```

#### 4.5 コード生成のみの場合

**前提条件**: Phase 6-7 (実装仕様) の結果が存在すること

**スキル呼び出し**: `/generate-scalardb-code {対象パス}`

実行後、完了通知とコード確認方法を表示。

#### 4.6 サイジング見積もりの場合

**スキル呼び出し**: `/scalardb-sizing-estimator`

対話的にサイジングパラメータを収集し、見積もりを生成。

実行後、見積もりレポートの場所を表示。

#### 4.7 個別フェーズ選択の場合

利用可能なフェーズを提示：

```json
{
  "questions": [{
    "question": "実行したいフェーズを選択してください（複数選択可）",
    "header": "フェーズ",
    "options": [
      {"label": "Phase 0: システム調査", "description": "technology-stack, codebase-structure"},
      {"label": "Phase 0.5a: セキュリティ分析", "description": "OWASP Top 10、ゼロトラスト準備度（オプション）"},
      {"label": "Phase 0.5b: アクセス制御分析", "description": "ゼロトラストアクセス制御（オプション）"},
      {"label": "Phase 1: システム分析", "description": "ubiquitous-language, domain-code-mapping"},
      {"label": "Phase 1.5a: データモデル分析", "description": "エンティティ、リレーションシップ（オプション）"},
      {"label": "Phase 1.5b: DB設計分析", "description": "テーブル定義、インデックス（オプション）"},
      {"label": "Phase 1.5c: ER図分析", "description": "現行ER図の生成（オプション）"},
      {"label": "Phase 2a: MMI評価", "description": "モジュール成熟度評価"},
      {"label": "Phase 2b: DDD評価", "description": "DDD原則適合性評価"},
      {"label": "Phase 2.5: 評価統合", "description": "MMI+DDD統合改善計画"},
      {"label": "Phase 3: DDD再設計", "description": "境界コンテキスト、集約設計"},
      {"label": "Phase 4: マイクロサービス設計", "description": "ターゲットアーキテクチャ"},
      {"label": "Phase 4.7: ScalarDBエディション選定", "description": "OSS/Enterprise Standard/Premium選定"},
      {"label": "Phase 4.8: ScalarDBアプリパターン設計", "description": "ドメインタイプ別設計パターン・DB選定"},
      {"label": "Phase 5: ScalarDB設計", "description": "スキーマ、トランザクション設計"},
      {"label": "Phase 5.5: Analytics設計", "description": "ScalarDB Analytics設計"},
      {"label": "Phase 5.9: ScalarDB設計レビュー", "description": "設計品質検証・ベストプラクティス準拠"},
      {"label": "Phase 5.95: API設計", "description": "REST/GraphQL/gRPC/AsyncAPI設計"},
      {"label": "Phase 6: 実装仕様", "description": "ドメインサービス、リポジトリ仕様"},
      {"label": "Phase 7: テスト仕様", "description": "BDD、単体/統合テスト仕様"},
      {"label": "Phase 8: コード生成", "description": "Spring Boot/ScalarDBコード"},
      {"label": "Phase 8.5: ScalarDBコードレビュー", "description": "生成コードの品質検証"},
      {"label": "Phase 9: コスト見積もり", "description": "インフラ/ライセンス費用"},
      {"label": "Phase 10: ドメインストーリー", "description": "ドメインストーリーテリング"},
      {"label": "Phase 11: グラフ構築", "description": "ナレッジグラフ構築"},
      {"label": "Phase 12: Mermaid検証", "description": "Mermaid図の検証・修正"}
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
│   ├── 03_design/               ← Phase 3-5.5
│   ├── 04_stories/              ← Phase 10
│   ├── 05_estimate/             ← Phase 9
│   ├── 06_implementation/       ← Phase 6
│   ├── 07_test-specs/           ← Phase 7
│   └── graph/                   ← Phase 11
├── generated/                   ← Phase 8
│   └── {service}/
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

### 例2: 分析のみ→設計

```
User: /workflow ./src

Agent: [実行タイプ選択を質問]
User: 分析のみ実行

Agent: [Phase 0-2.5 実行]
Agent: 分析完了。次のステップは？
User: DDD再設計の実行

Agent: [Phase 3-5.5 実行]
Agent: 設計完了。次のステップは？
User: ここで終了
```

### 例3: サイジング見積もり

```
User: /workflow

Agent: [実行タイプ選択を質問]
User: サイジング見積もり

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
