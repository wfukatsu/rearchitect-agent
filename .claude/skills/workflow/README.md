# Workflow Skill - インタラクティブワークフロー選択

## 概要

`/workflow` スキルは、レガシーシステムのリファクタリング分析・設計・実装において、実行したい処理を対話的に選択して段階的に実行できるインタラクティブなワークフローオーケストレーターです。

## 特徴

✅ **対話的な処理選択**: 最初に実行タイプを選択できる
✅ **段階的実行**: 分析のみ、設計のみなど、部分的に実行可能
✅ **柔軟な進行**: 各フェーズ完了後に次のステップを提案
✅ **進捗管理**: 中断・再開が可能
✅ **依存関係チェック**: 前提条件が満たされているか自動確認

## 使用方法

### 基本実行

```bash
# 対話的にワークフローを開始
/workflow

# 対象パス指定
/workflow ./path/to/source

# 出力先指定
/workflow ./src --output=./custom-reports/
```

### 実行タイプ

#### 1. 完全パイプライン実行（推奨）

調査→分析→評価→設計→実装→コード生成まで全フェーズを一括実行。

**含まれるフェーズ**:
- Phase 0: システム調査
- Phase 1: システム分析
- Phase 2a/2b: MMI評価 + DDD評価
- Phase 2.5: 評価統合
- Phase 3: DDD再設計
- Phase 4: マイクロサービス設計
- Phase 4.5: API設計
- Phase 5: ScalarDB設計
- Phase 5.5: ScalarDB Analytics設計
- Phase 6: 実装仕様
- Phase 7: テスト仕様
- Phase 8: コード生成
- Phase 9-13: コスト見積もり、ドメインストーリー、グラフ構築など

**実行時間**: 小規模 60分、中規模 3時間、大規模 6時間

**出力先**:
- `reports/` - 各種分析・設計ドキュメント
- `generated/` - 生成されたSpring Bootコード
- `knowledge.ryugraph` - ナレッジグラフDB

---

#### 2. 分析のみ実行

Phase 0-2.5: システム調査→分析→評価まで実行。

**実行フェーズ**:
1. `/system-investigation` - 技術スタック、コードベース構造調査
2. `/analyze-system` - ユビキタス言語、ドメイン分析
3. `/evaluate-mmi` - モジュール成熟度評価（並行実行）
4. `/ddd-evaluation` - DDD原則適合性評価（並行実行）
5. `/integrate-evaluations` - MMI+DDD統合改善計画

**実行後の選択肢**:
- DDD再設計へ進む
- マイクロサービス設計へ進む
- エグゼクティブサマリーのみ生成
- 終了

**出力先**:
- `reports/before/{project}/` - 現行システム調査結果
- `reports/01_analysis/` - 分析結果
- `reports/02_evaluation/` - 評価・改善計画

---

#### 3. 設計のみ実行

Phase 3-5.5: DDD再設計→マイクロサービス設計→API/DB設計。

**前提条件**: Phase 1-2（分析・評価）の結果が存在すること

**実行フェーズ**:
1. `/ddd-redesign` - 境界コンテキスト、集約設計
2. `/design-microservices` - ターゲットアーキテクチャ
3. `/design-api` - REST/GraphQL/gRPC設計
4. `/design-scalardb` - ScalarDBスキーマ・トランザクション設計
5. `/design-scalardb-analytics` - ScalarDB Analytics設計（オプション）

**実行後の選択肢**:
- 実装仕様生成へ進む
- コスト見積もり実行
- ドメインストーリー作成
- 終了

**出力先**:
- `reports/03_design/` - 設計ドキュメント
- `reports/03_design/api-specifications/` - APIスペック

---

#### 4. 実装仕様生成

Phase 6-7: 実装仕様書→テスト仕様書の生成。

**前提条件**: Phase 3-5（設計）の結果が存在すること

**実行フェーズ**:
1. `/design-implementation` - ドメインサービス、リポジトリ、値オブジェクト実装仕様
2. `/generate-test-specs` - BDD、単体テスト、統合テスト仕様

**実行後の選択肢**:
- コード生成へ進む
- コスト見積もり実行
- 終了

**出力先**:
- `reports/06_implementation/` - 実装仕様
- `reports/07_test-specs/` - テスト仕様

---

#### 5. コード生成のみ

Phase 8: Spring Boot/ScalarDBコードの生成。

**前提条件**: Phase 6-7（実装仕様）の結果が存在すること

**実行フェーズ**:
1. `/generate-scalardb-code` - Spring Boot/ScalarDB完全コード生成

**出力先**:
- `generated/{service}/src/` - Javaソースコード
- `generated/{service}/build.gradle` - Gradleビルドファイル
- `generated/{service}/Dockerfile` - Dockerイメージ定義
- `generated/{service}/k8s/` - Kubernetes YAML

---

#### 6. サイジング見積もり

ScalarDB Cluster/Analytics/インフラのサイジングと費用見積もり。

**実行内容**:
- 対話的にサイジングパラメータ収集（環境、性能、可用性など）
- ScalarDB Pod数、Kubernetes Node数、DB構成を算出
- 月額・年額費用を見積もり
- コスト削減オプションを提案

**出力先**:
- `reports/sizing-estimates/` - サイジングレポート（Markdown + HTML）

---

#### 7. 個別フェーズ選択

実行したい個別フェーズを複数選択。

**選択可能なフェーズ**:
- Phase 0: システム調査
- Phase 1: システム分析
- Phase 2a: MMI評価
- Phase 2b: DDD評価
- Phase 2.5: 評価統合
- Phase 3: DDD再設計
- Phase 4: マイクロサービス設計
- Phase 4.5: API設計
- Phase 5: ScalarDB設計
- Phase 5.5: Analytics設計
- Phase 6: 実装仕様
- Phase 7: テスト仕様
- Phase 8: コード生成
- Phase 9: コスト見積もり
- Phase 10: ドメインストーリー
- Phase 11: グラフ構築
- Phase 12: Mermaid検証

依存関係チェックあり: 前提条件が満たされていない場合は警告。

---

## 実行例

### 例1: 完全パイプライン

```bash
$ /workflow ./SampleCode

# [対話的に選択]
実行タイプ: 完全パイプライン実行

# 全フェーズ実行...

✅ 完了
reports/00_summary/full-report.html を確認してください
```

---

### 例2: 分析→設計と段階的に進める

```bash
$ /workflow ./src

# [対話的に選択]
実行タイプ: 分析のみ実行

# Phase 0-2.5 実行...

✅ 分析完了

次のステップ:
1. DDD再設計の実行
2. マイクロサービス設計の実行
3. エグゼクティブサマリーのみ生成
4. ここで終了

選択: DDD再設計の実行

# Phase 3-5.5 実行...

✅ 設計完了

次のステップ:
1. 実装仕様生成へ進む
2. コスト見積もり実行
3. 終了

選択: 終了
```

---

### 例3: サイジング見積もりのみ

```bash
$ /workflow

# [対話的に選択]
実行タイプ: サイジング見積もり

環境: 全環境（開発・テスト・ステージング・本番）
クラウド: AWS
ライセンス: 直接契約 Premium
性能: 中規模（2,000 TPS）
可用性: 99.95%
# ... その他パラメータ収集

✅ 見積もり完了

月額費用: ¥5,721,600
年間費用: ¥68,659,200

詳細: reports/sizing-estimates/scalardb-all-environments-sizing-estimate.html
```

---

### 例4: 個別フェーズ選択

```bash
$ /workflow ./src

# [対話的に選択]
実行タイプ: 個別フェーズ選択

選択フェーズ:
☑ Phase 3: DDD再設計
☑ Phase 4: マイクロサービス設計
☑ Phase 5: ScalarDB設計

# 選択フェーズのみ実行...

✅ 完了
```

## フェーズ依存関係

| フェーズ | 前提条件 | 備考 |
|---------|---------|------|
| Phase 0 | なし | 最初に実行可能 |
| Phase 1 | Phase 0推奨 | なくても実行可 |
| Phase 2a/2b | Phase 1推奨 | 並行実行可能 |
| Phase 2.5 | Phase 2a, 2b完了 | 必須 |
| Phase 3 | Phase 2完了推奨 | - |
| Phase 4 | Phase 3完了 | 必須 |
| Phase 4.5 | Phase 4完了 | 必須 |
| Phase 5 | Phase 4完了 | 必須 |
| Phase 5.5 | Phase 5完了 | オプション |
| Phase 6 | Phase 3-5完了 | 必須 |
| Phase 7 | Phase 6完了 | 必須 |
| Phase 8 | Phase 6-7完了 | 必須 |
| Phase 9 | Phase 3-5推奨 | いつでも実行可 |
| Phase 10 | Phase 3完了 | - |
| Phase 11 | Phase 1完了 | - |
| Phase 12 | Markdown存在 | - |

## 進捗管理

実行中の進捗は `work/{project}/workflow-progress.json` に保存されます。

```json
{
  "workflow_type": "complete",
  "target_path": "./SampleCode",
  "output_path": "./reports",
  "started_at": "2026-01-23T12:00:00Z",
  "current_phase": "phase-4",
  "completed_phases": [
    "phase-0",
    "phase-1",
    "phase-2a",
    "phase-2b",
    "phase-2.5",
    "phase-3"
  ],
  "pending_phases": [
    "phase-4",
    "phase-4.5",
    "phase-5",
    "..."
  ],
  "user_selections": {
    "include_analytics": true,
    "include_stories": true,
    "include_graph": true
  }
}
```

中断しても、再度 `/workflow` を実行すると続きから再開できます。

## 出力構造

```
./
├── reports/
│   ├── before/{project}/        # Phase 0: 現行システム調査
│   ├── 00_summary/              # エグゼクティブサマリー
│   ├── 01_analysis/             # Phase 1: システム分析
│   ├── 02_evaluation/           # Phase 2: MMI/DDD評価
│   ├── 03_design/               # Phase 3-5: 設計
│   │   └── api-specifications/
│   ├── 04_stories/              # Phase 10: ドメインストーリー
│   ├── 05_estimate/             # Phase 9: コスト見積もり
│   ├── 06_implementation/       # Phase 6: 実装仕様
│   ├── 07_test-specs/           # Phase 7: テスト仕様
│   │   └── bdd-scenarios/
│   ├── graph/                   # Phase 11: ナレッジグラフ
│   │   └── data/
│   └── sizing-estimates/        # サイジング見積もり
├── generated/                   # Phase 8: 生成コード
│   └── {service}/
│       ├── src/
│       ├── build.gradle
│       ├── Dockerfile
│       └── k8s/
├── work/{project}/              # 進捗管理
│   └── workflow-progress.json
└── knowledge.ryugraph/          # Phase 11: グラフDB
```

## エラーハンドリング

### 前提条件未満足

```
⚠️ 警告: Phase 4を実行するにはPhase 3の完了が必要です。

以下のいずれかを選択してください:
1. Phase 3から実行する
2. Phase 4のみ実行する（リスクあり）
3. キャンセル
```

### フェーズ実行失敗

```
❌ エラー: Phase 2a (MMI評価) が失敗しました。

選択肢:
1. Phase 2aをスキップして次へ進む
2. Phase 2aをリトライする
3. ワークフローを中断
```

### 対象パス不存在

```
❌ エラー: 指定されたパス './invalid-path' が存在しません。

対象パスを再指定してください。
```

## Tips

### 大規模プロジェクトの場合

段階的に進めることを推奨：

1. **Week 1**: 分析のみ実行 → レビュー
2. **Week 2**: 設計のみ実行 → レビュー
3. **Week 3**: 実装仕様生成 → レビュー
4. **Week 4**: コード生成 → 検証

### 小規模プロジェクトの場合

完全パイプライン実行で一気に処理：

```bash
/workflow ./src
→ 完全パイプライン実行
```

60分程度で全フェーズ完了。

### サイジングのみ必要な場合

```bash
/workflow
→ サイジング見積もり
```

対話的にパラメータを入力し、見積もりレポートを取得。

## 関連スキル

| スキル | 用途 |
|--------|------|
| `/full-pipeline` | 非対話的な完全パイプライン実行 |
| `/refactor-system` | 従来の統合オーケストレーター（コード生成なし） |
| `/scalardb-sizing-estimator` | 対話式サイジング見積もり |
| 個別フェーズスキル | 各フェーズの詳細実行 |
| `/compile-report` | HTML総合レポート生成 |
| `/query-graph` | 生成されたナレッジグラフへのクエリ |

## トラブルシューティング

### Q: "Phase X の結果が見つかりません" と表示される

A: 前提フェーズが未実行です。以下を確認：
- `reports/` ディレクトリに該当フェーズの出力があるか
- 前提フェーズから実行するか、`--force` オプションで強制実行

### Q: ワークフローが途中で中断した

A: 再度 `/workflow` を実行すると、進捗ファイルから自動的に続きを再開します。
強制的に最初からやり直す場合: `work/{project}/workflow-progress.json` を削除。

### Q: サイジング見積もりで想定外の費用が表示される

A: 以下を確認：
- 本番環境のTPS・可用性設定が適切か
- Reserved Instances等の削減オプションを適用していないか
- ScalarDB Analyticsの稼働時間設定（業務時間のみ推奨）

## 次のステップ

1. **ワークフローを実行**: `/workflow` でスタート
2. **レポート確認**: `reports/00_summary/` のサマリーを確認
3. **生成コード確認**: `generated/` の実装コードをレビュー
4. **グラフ探索**: `/query-graph` でナレッジグラフをクエリ
5. **コスト最適化**: Reserved Instances等の適用を検討

---

**作成日**: 2026-01-25
**バージョン**: 1.0
