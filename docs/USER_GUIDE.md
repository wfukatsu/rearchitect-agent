# Refactoring Agent ユーザーガイド

既存システムをマイクロサービスアーキテクチャにリファクタリングするための Claude Code エージェント群の使い方と解説です。

## 目次

1. [概要](#概要)
2. [セットアップ](#セットアップ)
3. [クイックスタート](#クイックスタート)
4. [スキル一覧と使い方](#スキル一覧と使い方)
5. [実行フロー](#実行フロー)
6. [出力ファイルの読み方](#出力ファイルの読み方)
7. [ナレッジグラフの活用](#ナレッジグラフの活用)
8. [カスタマイズオプション](#カスタマイズオプション)
9. [トラブルシューティング](#トラブルシューティング)
10. [ベストプラクティス](#ベストプラクティス)

---

## 概要

### このエージェントでできること

Refactoring Agent は、以下のプロセスを自動化・支援します：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Refactoring Agent                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  入力: 既存システムのソースコード + 設計書（オプション）           │
│                          ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. システム分析        → ユビキタス言語、アクター抽出       │   │
│  │ 2. MMI評価            → モジュール成熟度の定量評価        │   │
│  │ 3. ドメインマッピング   → 境界づけられたコンテキスト設計    │   │
│  │ 4. マイクロサービス設計 → ターゲットアーキテクチャ策定    │   │
│  │ 5. API設計            → REST/GraphQL/gRPC/AsyncAPI仕様  │   │
│  │ 6. ScalarDB設計       → 分散トランザクション設計          │   │
│  │ 7. ScalarDBサイジング → Pod数、K8s構成、コスト見積もり    │   │
│  │ 8. ドメインストーリー   → ビジネスプロセスの可視化         │   │
│  │ 9. コスト見積もり      → インフラ・ライセンス費用算出      │   │
│  │ 10.HTMLレポート生成   → 統合HTMLレポート出力            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  出力: 包括的なリファクタリング計画書 + ナレッジグラフ            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 主な特徴

| 特徴 | 説明 |
|-----|------|
| **自動分析** | ソースコードと設計書から自動的にドメイン知識を抽出 |
| **定量評価** | MMI（Modularity Maturity Index）による客観的な成熟度評価 |
| **DDD準拠** | ドメイン駆動設計の原則に基づいたマイクロサービス境界の設計 |
| **API設計** | REST/GraphQL/gRPC/AsyncAPI仕様、Gateway、セキュリティ設計 |
| **ScalarDB対応** | 分散トランザクションを考慮したデータアーキテクチャ設計 |
| **サイジング見積もり** | ScalarDB Pod数、K8s構成、コストを対話的に見積もり |
| **ナレッジグラフ** | 分析結果をグラフDBに格納し、高度な探索を実現 |
| **HTMLレポート** | 分析結果をMermaid図付き統合HTMLレポートに変換 |

---

## セットアップ

### 前提条件

1. **Claude Code CLI** がインストールされていること
   ```bash
   # インストール確認
   claude --version
   ```

2. **Python 3.9+**（ナレッジグラフ機能を使用する場合）
   ```bash
   python3 --version
   ```

### インストール手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/wfukatsu/refactoring-agent.git
cd refactoring-agent

# 2. 依存関係をインストール（オプション）
pip install ryugraph pandas markdown pymdown-extensions

# 3. Claude Code を起動
claude
```

### 推奨環境

- **対応言語**: Java, TypeScript, JavaScript, Python, Go, C#
- **推奨プロジェクトサイズ**: 1万〜50万行
- **設計書形式**: Markdown, Word (.docx), Excel (.xlsx), PDF

---

## クイックスタート

### 最も簡単な使い方

```bash
# Claude Code を起動して以下を入力
/refactor-system ./path/to/your/project
```

これだけで、8つのフェーズすべてが順次実行され、包括的なリファクタリング計画書が生成されます。

### 出力の確認

分析完了後、`reports/` ディレクトリに結果が出力されます：

```bash
# エグゼクティブサマリーを確認
cat reports/00_summary/executive_summary.md

# HTMLレポートをブラウザで開く
open reports/00_summary/full-report.html
```

---

## スキル一覧と使い方

### メインオーケストレーター

#### `/refactor-system` - 統合リファクタリング

すべてのフェーズを順次実行するメインコマンドです。

```bash
# 基本的な使い方
/refactor-system ./src

# オプション付き
/refactor-system ./src --output=./custom-output/
/refactor-system ./src --domain=Order,Customer
/refactor-system ./src --analyze-only
/refactor-system ./src --skip-mmi
```

| オプション | 説明 |
|-----------|------|
| `--output=PATH` | 出力先ディレクトリを変更 |
| `--domain=NAME` | 特定ドメインのみ分析 |
| `--analyze-only` | 分析のみ実行（設計書生成なし） |
| `--skip-mmi` | MMI評価をスキップ |
| `--skip-stories` | ドメインストーリーをスキップ |

---

### 個別スキル

各フェーズを個別に実行することも可能です。

#### `/analyze-system` - システム分析

ソースコードと設計書から基礎的なドメイン知識を抽出します。

```bash
/analyze-system ./src
```

**出力ファイル:**
- `reports/01_analysis/system-overview.md` - システム概要
- `reports/01_analysis/ubiquitous-language.md` - ユビキタス言語集
- `reports/01_analysis/actors-roles-permissions.md` - アクター・ロール・権限
- `reports/01_analysis/domain-code-mapping.md` - ドメイン-コード対応表

**抽出される情報:**

| カテゴリ | 抽出元 | 内容 |
|---------|-------|------|
| ユビキタス言語 | クラス名、メソッド名、定数、コメント | ビジネス用語とその定義 |
| アクター | 認証コード、ロール定義、ユースケース | 登場人物とその役割 |
| ドメイン-コード対応 | 設計書とソースコード | 概念とコードの紐付け |

---

#### `/evaluate-mmi` - MMI評価

モジュールの成熟度を4軸で定量評価します。

```bash
/evaluate-mmi ./src
```

**出力ファイル:**
- `reports/02_evaluation/mmi-overview.md` - 全体サマリー
- `reports/02_evaluation/mmi-by-module.md` - モジュール別詳細
- `reports/02_evaluation/mmi-improvement-plan.md` - 改善計画

**評価軸:**

| 軸 | 重み | 評価ポイント |
|---|-----|-------------|
| **Cohesion（凝集度）** | 30% | 単一責務性、機能の集中度 |
| **Coupling（結合度）** | 30% | 依存関係、疎結合性 |
| **Independence（独立性）** | 20% | デプロイ独立性、変更の局所化 |
| **Reusability（再利用性）** | 20% | 汎用性、他コンテキストでの適用可能性 |

**スコアの読み方:**

| スコア | レベル | 意味 |
|-------|-------|-----|
| 80-100 | 高成熟 | マイクロサービス化の準備完了 |
| 60-80 | 中成熟 | 一部改善でマイクロサービス化可能 |
| 40-60 | 低中成熟 | 大幅なリファクタリングが必要 |
| 0-40 | 未成熟 | モノリス分解の計画策定から |

---

#### `/map-domains` - ドメインマッピング

境界づけられたコンテキストとコンテキストマップを作成します。

```bash
/map-domains ./src
```

**出力ファイル:**
- `reports/03_design/domain-analysis.md` - ドメイン分析
- `reports/03_design/context-map.md` - コンテキストマップ
- `reports/03_design/system-mapping.md` - システムマッピング

**ドメイン分類体系:**

```
ビジネス構造軸
├── Pipeline Domain     → 順序的なデータ/処理フロー（注文処理など）
├── Blackboard Domain   → 共有データへの協調的アクセス（在庫管理など）
└── Dialogue Domain     → 双方向のインタラクション（チャットなど）

マイクロサービス境界軸
├── Process Domain      → ビジネスプロセスの実行
├── Master Domain       → マスタデータの管理
├── Integration Domain  → 外部システム連携
└── Supporting Domain   → 横断的機能の提供
```

---

#### `/design-microservices` - マイクロサービス設計

ターゲットアーキテクチャと移行計画を策定します。

```bash
/design-microservices ./src
```

**出力ファイル:**
- `reports/03_design/target-architecture.md` - ターゲットアーキテクチャ
- `reports/03_design/transformation-plan.md` - 変換計画
- `reports/03_design/operations-feedback.md` - 運用・フィードバック計画

---

#### `/design-scalardb` - ScalarDB設計

ScalarDB Cluster を使用した分散トランザクション設計を行います。

```bash
/design-scalardb ./src
```

**出力ファイル:**
- `reports/03_design/scalardb-architecture.md` - クラスター構成
- `reports/03_design/scalardb-schema.md` - スキーマ設計
- `reports/03_design/scalardb-transaction.md` - トランザクション設計
- `reports/03_design/scalardb-migration.md` - マイグレーション計画

**ScalarDB の主な機能:**

| 機能 | 説明 |
|-----|------|
| Consensus Commit | 単一ストレージでのACIDトランザクション |
| Two-Phase Commit | 複数ストレージ間の分散トランザクション |
| Multi-Storage | 異種DB間のアトミック操作 |

---

#### `/design-scalardb-analytics` - ScalarDB Analytics設計

HTAP（Hybrid Transactional/Analytical Processing）基盤を設計します。

```bash
/design-scalardb-analytics ./src
```

**出力ファイル:**
- `reports/03_design/scalardb-analytics-architecture.md`
- `reports/03_design/scalardb-analytics-queries.md`
- `reports/03_design/scalardb-analytics-catalog.md`

---

#### `/design-api` - API設計

マイクロサービス間のAPI仕様、Gateway、セキュリティを設計します。

```bash
/design-api ./src
```

**出力ファイル:**
- `reports/03_design/api-design-overview.md` - API設計概要
- `reports/03_design/api-gateway-design.md` - API Gateway設計
- `reports/03_design/api-security-design.md` - 認証・認可設計
- `reports/03_design/api-specifications/` - 仕様書ディレクトリ

**対応フォーマット:**

| フォーマット | 説明 |
|------------|------|
| OpenAPI 3.0 | REST API仕様（YAML） |
| GraphQL | GraphQLスキーマ |
| gRPC | Protocol Buffers定義 |
| AsyncAPI | イベント駆動API仕様 |

---

#### `/create-domain-story` - ドメインストーリーテリング

対話的にビジネスプロセスを引き出し、可視化します。

```bash
# 特定ドメインを指定して実行
/create-domain-story --domain=Order

# インタラクティブモード
/create-domain-story
```

**7段階のプロセス:**

1. **舞台設定** - スコープを決定
2. **物語開始** - 最初のアクターと行動を特定
3. **展開** - 時系列でアクティビティの連鎖を追跡
4. **確認** - 整理した内容をレビュー
5. **例外検討** - うまくいかないパターンを確認
6. **可視化** - Mermaid図を生成
7. **クロージング** - 調整確認と終了判断

**出力例:**
```
reports/04_stories/
├── order-story.md      # 注文ドメインのストーリー
├── inventory-story.md  # 在庫ドメインのストーリー
└── payment-story.md    # 決済ドメインのストーリー
```

---

#### `/estimate-cost` - コスト見積もり

インフラストラクチャとライセンスのコストを見積もります。

```bash
/estimate-cost ./reports
```

**出力ファイル:**
- `reports/05_estimate/cost-summary.md` - コストサマリー
- `reports/05_estimate/infrastructure-detail.md` - インフラ詳細
- `reports/05_estimate/license-requirements.md` - ライセンス要件
- `reports/05_estimate/cost-assumptions.md` - 前提条件

---

#### `/scalardb-sizing-estimator` - ScalarDBサイジング

ScalarDB Cluster環境のサイジングとコスト見積もりを対話形式で行います。

```bash
/scalardb-sizing-estimator
```

**対話式の質問:**
1. 環境構成（開発のみ/本番のみ/全環境セット）
2. 想定TPS（小規模〜500 / 中規模500-2000 / 大規模2000+）
3. 目標可用性（99.9% / 99.99% / 99%）
4. ScalarDB Analytics使用有無

**見積もり項目:**

| 項目 | 説明 |
|-----|------|
| Pod数計算 | 性能要件と可用性要件から算出 |
| Kubernetes構成 | Node数、Instance Type、Node Pool |
| バックエンドDB | Aurora PostgreSQL等のサイジング |
| コスト算出 | ライセンス + インフラ（月額/年額） |

**出力ファイル:**
- `reports/05_estimate/scalardb-sizing.md`

---

### ナレッジグラフスキル

#### `/build-graph` - グラフ構築

分析結果からRyuGraphデータベースを構築します。

```bash
# 前提: /analyze-system が完了していること
/build-graph ./src
```

**生成されるもの:**
- `knowledge.ryugraph/` - RyuGraphデータベース
- `reports/graph/data/*.csv` - 中間CSVファイル
- `reports/graph/schema.md` - グラフスキーマ
- `reports/graph/statistics.md` - 統計情報

---

#### `/query-graph` - グラフ探索

自然言語またはCypherでグラフを探索します。

```bash
# 自然言語クエリ
/query-graph 「注文」に関連するクラスを教えて
/query-graph 認証フローに関わるメソッドは？
/query-graph CustomerServiceが依存しているエンティティを探して

# Cypherクエリ
/query-graph MATCH (e:Entity)-[:HAS_TERM]->(t:UbiquitousTerm) RETURN e, t LIMIT 10
/query-graph MATCH (e:Entity)-[:BELONGS_TO]->(d:Domain) RETURN e.name, d.name
/query-graph MATCH (a:Actor)-[:HAS_ROLE]->(r:Role) RETURN a.name, r.name
```

---

#### `/visualize-graph` - グラフ可視化

グラフをMermaid/DOT/HTML形式で可視化します。

```bash
# 全体を可視化
/visualize-graph ./reports/graph/visualizations

# 特定ドメインのみ
/visualize-graph --domain=Audit
```

**出力ファイル:**
- `reports/graph/visualizations/graph.html` - インタラクティブD3.jsビューア
- `reports/graph/visualizations/graph.mmd` - Mermaid形式
- `reports/graph/visualizations/graph.dot` - DOT形式（Graphviz）

**HTMLビューアの機能:**
- ノードのドラッグ移動
- マウスホイールでズーム
- ノードホバーで詳細表示
- ノード検索
- 凡例表示

---

### ユーティリティスキル

#### `/compile-report` - レポートコンパイル

Markdownレポートを統合HTMLに変換します。

```bash
# 基本
/compile-report

# オプション付き
/compile-report --theme dark

# 結果を確認
open reports/00_summary/full-report.html
```

**機能:**

| 機能 | 説明 |
|-----|------|
| Markdown統合 | 各ディレクトリのMarkdownを自動検出・統合 |
| Mermaidレンダリング | Mermaid図をインライン埋め込み |
| D3.jsグラフ | ナレッジグラフをインタラクティブに可視化 |
| 目次生成 | サイドバー目次を自動生成 |
| テーマ対応 | ライト/ダークテーマ |

#### `/render-mermaid` - Mermaid図変換

Mermaid図をPNG/SVG画像に変換します。

```bash
/render-mermaid ./reports/
```

#### `/fix-mermaid` - Mermaid修正

Mermaid図のシンタックスエラーを自動修正します。

```bash
/fix-mermaid ./reports/
```

---

## 実行フロー

### 全体フロー図

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         /refactor-system                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 1: /analyze-system                                                │
│   → system-overview.md, ubiquitous-language.md,                        │
│     actors-roles-permissions.md, domain-code-mapping.md                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│ Phase 2: /evaluate-mmi       │    │ Parallel: /build-graph       │
│   → mmi-overview.md,         │    │   → knowledge.ryugraph/      │
│     mmi-by-module.md,        │    │     reports/graph/           │
│     mmi-improvement-plan.md  │    │                              │
└──────────────────────────────┘    └──────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 3: /map-domains                                                   │
│   → domain-analysis.md, context-map.md, system-mapping.md              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 4: /design-microservices                                          │
│   → target-architecture.md, transformation-plan.md,                    │
│     operations-feedback.md                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 5: /design-scalardb                                               │
│   → scalardb-architecture.md, scalardb-schema.md,                      │
│     scalardb-transaction.md, scalardb-migration.md                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                           ┌───────┴───────┐
                           │ 分析要件あり? │
                           └───────┬───────┘
                      Yes ─────────┼───────── No
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             │
┌──────────────────────────────┐                  │
│ Phase 5.5: /design-scalardb- │                  │
│            analytics         │                  │
│   → analytics-*.md           │                  │
└──────────────────────────────┘                  │
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 6: /create-domain-story                                           │
│   → [domain]-story.md (各ドメイン)                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 7: /estimate-cost                                                 │
│   → cost-summary.md, infrastructure-detail.md,                         │
│     license-requirements.md, cost-assumptions.md                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 8: Executive Summary Generation                                   │
│   → executive_summary.md                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ /compile-report                                                         │
│   → full-report.html (統合HTMLレポート)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 依存関係

```
/analyze-system ─────┬──────────────────────────────────┐
                     │                                  │
                     ▼                                  ▼
              /evaluate-mmi                      /build-graph
                     │                                  │
                     ▼                                  ▼
              /map-domains                       /query-graph
                     │                                  │
                     ▼                                  ▼
          /design-microservices              /visualize-graph
                     │
                     ▼
            /design-scalardb
                     │
                     ▼
       /design-scalardb-analytics (optional)
                     │
                     ▼
         /create-domain-story
                     │
                     ▼
            /estimate-cost
```

---

## 出力ファイルの読み方

### ディレクトリ構造

```
reports/
├── 00_summary/                      # エグゼクティブサマリー
│   ├── executive-summary.md         # 経営層向けサマリー
│   ├── project_metadata.json        # プロジェクトメタデータ
│   └── full-report.html             # 統合HTMLレポート
│
├── 01_analysis/                     # システム分析結果
│   ├── system-overview.md           # 技術スタック、アーキテクチャ
│   ├── ubiquitous-language.md       # ビジネス用語辞書
│   ├── actors-roles-permissions.md  # 権限マトリクス
│   └── domain-code-mapping.md       # 概念-コード対応表
│
├── 02_evaluation/                   # MMI評価結果
│   ├── mmi-overview.md              # 全体スコアと分布
│   ├── mmi-by-module.md             # モジュール別詳細
│   └── mmi-improvement-plan.md      # 改善ロードマップ
│
├── 03_design/                       # 設計ドキュメント
│   ├── domain-analysis.md           # ドメイン分析
│   ├── context-map.md               # コンテキストマップ
│   ├── target-architecture.md       # ターゲットアーキテクチャ
│   ├── transformation-plan.md       # 変換計画
│   ├── operations-feedback.md       # 運用計画
│   ├── api-design-overview.md       # API設計概要
│   ├── api-gateway-design.md        # API Gateway設計
│   ├── api-security-design.md       # APIセキュリティ設計
│   ├── api-specifications/          # API仕様書
│   │   ├── openapi/*.yaml           # REST API
│   │   ├── graphql/*.graphql        # GraphQLスキーマ
│   │   ├── grpc/*.proto             # gRPC
│   │   └── asyncapi/*.yaml          # AsyncAPI
│   ├── scalardb-architecture.md     # ScalarDBクラスター構成
│   ├── scalardb-schema-design.md    # ScalarDBスキーマ
│   ├── scalardb-transaction-design.md # トランザクション設計
│   └── scalardb-analytics-*.md      # Analytics設計（オプション）
│
├── 04_stories/                      # ドメインストーリー
│   └── [domain]-story.md            # ドメイン別ストーリー
│
├── 05_estimate/                     # コスト見積もり
│   ├── cost-summary.md              # コストサマリー
│   ├── scalardb-sizing.md           # ScalarDBサイジング見積もり
│   └── infrastructure-detail.md     # インフラ詳細
│
├── graph/                           # ナレッジグラフ
│   ├── data/                        # CSVデータ
│   │   ├── terms.csv
│   │   ├── domains.csv
│   │   ├── entities.csv
│   │   └── ...
│   ├── visualizations/              # 可視化ファイル（Mermaid/DOT/HTML）
│   │   ├── graph.html               # インタラクティブD3.jsグラフ
│   │   ├── graph.mmd                # Mermaid形式
│   │   └── graph.dot                # DOT形式
│   ├── schema.md                    # グラフスキーマ
│   └── statistics.md                # 統計情報
│
└── 99_appendix/                     # 付録
    └── ...
```

### 重要なファイルの解説

#### `executive_summary.md`

経営層向けのサマリーです。以下が含まれます：

- プロジェクト概要
- 主要な発見事項
- 推奨アクション
- リスクと軽減策
- 次のステップ

#### `ubiquitous-language.md`

ビジネス用語の辞書です。以下の形式で記載されます：

| 用語 | 日本語 | 定義 | 使用箇所 |
|-----|-------|-----|---------|
| Order | 注文 | 顧客からの商品購入リクエスト | OrderService, OrderController |

#### `mmi-by-module.md`

モジュール別の評価詳細です：

```markdown
## OrderModule

### スコア
| 軸 | スコア (0-5) | 評価 |
|---|------------|-----|
| Cohesion | 4 | 高い |
| Coupling | 3 | 中程度 |
| Independence | 3 | 中程度 |
| Reusability | 2 | 低い |

**MMI: 62/100 (中成熟)**

### 改善提案
1. CustomerServiceへの直接依存を解消
2. DBアクセスをリポジトリ層に集約
```

---

## ナレッジグラフの活用

### グラフスキーマ

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ナレッジグラフスキーマ                            │
└─────────────────────────────────────────────────────────────────────────┘

ノードタイプ:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ UbiquitousTerm   │  │     Domain       │  │     Entity       │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ name             │  │ name             │  │ name             │
│ name_ja          │  │ type             │  │ file_path        │
│ definition       │  │ description      │  │ type             │
│ domain           │  │                  │  │ line_number      │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│     Method       │  │      File        │  │      Actor       │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ name             │  │ path             │  │ name             │
│ signature        │  │ language         │  │ type             │
│ file_path        │  │ module           │  │ description      │
│ line_number      │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘

リレーションシップ:
Entity ──BELONGS_TO──> Domain
Entity ──DEFINED_IN──> File
Entity ──REFERENCES──> Entity
Entity ──HAS_TERM──> UbiquitousTerm
Method ──CALLS──> Method
Method ──DEFINED_IN──> File
Entity ──IMPLEMENTS──> Entity
Actor ──HAS_ROLE──> Role
```

### クエリ例

#### 基本的なクエリ

```bash
# 特定用語に関連するエンティティを検索
/query-graph MATCH (e:Entity)-[:HAS_TERM]->(t:UbiquitousTerm {name_ja: '注文'}) RETURN e

# 特定ドメインのすべてのエンティティ
/query-graph MATCH (e:Entity)-[:BELONGS_TO]->(d:Domain {name: 'Order'}) RETURN e

# 循環依存の検出
/query-graph MATCH (a:Entity)-[:REFERENCES]->(b:Entity)-[:REFERENCES]->(a) RETURN a, b
```

#### 高度なクエリ

```bash
# メソッドの呼び出しチェーン（3段階まで）
/query-graph MATCH path = (m:Method {name: 'processOrder'})-[:CALLS*1..3]->(target:Method) RETURN path

# 最も参照されているエンティティ
/query-graph MATCH (e:Entity)<-[:REFERENCES]-(other) RETURN e.name, count(other) ORDER BY count(other) DESC LIMIT 10

# 特定アクターの権限範囲
/query-graph MATCH (a:Actor {name: 'Admin'})-[:HAS_ROLE]->(r:Role) RETURN a, r
```

### Python APIでの利用

```python
from ryugraph import RyuGraph

# データベースに接続
graph = RyuGraph("./knowledge.ryugraph")

# クエリを実行
results = graph.query("""
    MATCH (e:Entity)-[:BELONGS_TO]->(d:Domain)
    RETURN e.name, d.name
""")

for row in results:
    print(f"Entity: {row['e.name']}, Domain: {row['d.name']}")
```

---

## カスタマイズオプション

### 出力先の変更

```bash
/refactor-system ./src --output=./my-analysis/
```

### 特定ドメインのみ分析

```bash
# カンマ区切りで複数指定可能
/refactor-system ./src --domain=Order,Customer,Payment
```

### フェーズのスキップ

```bash
# MMI評価をスキップ
/refactor-system ./src --skip-mmi

# ドメインストーリーをスキップ
/refactor-system ./src --skip-stories

# 分析のみ実行
/refactor-system ./src --analyze-only
```

### 手動でのパイプライン実行

各スキルを個別に実行することで、細かな制御が可能です：

```bash
# Step 1: システム分析
/analyze-system ./src

# Step 2: 結果を確認・調整
# reports/01_analysis/*.md を手動で編集

# Step 3: MMI評価
/evaluate-mmi ./src

# 以降、必要なスキルのみ実行
```

---

## トラブルシューティング

### よくある問題と解決策

#### 「設計書が見つかりません」

**原因:** 対象ディレクトリに .md, .docx, .xlsx, .pdf ファイルがない

**解決策:**
- 設計書がある場合は対象ディレクトリに配置
- 設計書がない場合はコードのみから分析（精度は低下）

```bash
# 警告を確認して続行
/analyze-system ./src
# → "設計書が見つかりません。コードから推論します。" と表示される
```

#### 「Serenaツールが応答しません」

**原因:** 言語サポートの問題、またはプロジェクト設定の不備

**解決策:**
1. `.serena/project.yml` を確認
2. 対応言語か確認（Java, TypeScript, Python, Go, C#）
3. Serenaを再起動

#### 「RyuGraphのインストールエラー」

**解決策:**
```bash
# Python 3.9以上を確認
python3 --version

# pip を更新
pip install --upgrade pip

# 再インストール
pip install ryugraph pandas
```

#### 「大規模コードベースで時間がかかる」

**解決策:**
```bash
# 特定ドメインに絞る
/refactor-system ./src --domain=Order

# 分析のみ実行
/refactor-system ./src --analyze-only

# 手動で段階的に実行
/analyze-system ./src/order
/analyze-system ./src/customer
```

---

## ベストプラクティス

### 1. 設計書を準備する

可能な限り以下を用意してください：

- 要件定義書
- ER図
- ユースケース図
- API仕様書

これにより分析精度が大幅に向上します。

### 2. 段階的に実行する

大規模プロジェクトでは、一度に全体を実行せず、段階的に実行することを推奨します：

```bash
# まず分析のみ
/analyze-system ./src

# 結果を確認
cat reports/01_analysis/ubiquitous-language.md

# 必要に応じて調整後、次のフェーズへ
/evaluate-mmi ./src
```

### 3. 結果をレビューする

自動生成された結果は必ず人間がレビューしてください。特に：

- ユビキタス言語の定義が正しいか
- ドメイン境界が適切か
- MMIスコアが実感と合っているか

### 4. ナレッジグラフを活用する

分析後は積極的にナレッジグラフを活用してください：

```bash
# 依存関係の確認
/query-graph OrderServiceの依存先を教えて

# 影響範囲の調査
/query-graph Customerエンティティを参照しているクラス一覧
```

### 5. 反復的に改善する

一度の分析で完璧な結果を期待せず、以下のサイクルで改善してください：

```
分析実行 → 結果レビュー → 入力調整 → 再分析 → ...
```

---

## 参考情報

### 外部ドキュメント

- [ScalarDB Documentation](https://scalardb.scalar-labs.com/docs/)
- [ScalarDB Analytics](https://scalardb.scalar-labs.com/docs/latest/scalardb-analytics/)
- [RyuGraph Documentation](https://ryugraph.io/docs/)

### 理論的背景

- [Modularity Maturity Index](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/modularity-maturity-index.md)
- [Domain-Driven Transformation](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/domain-driven-transformation.md)
- [Domain Storytelling](https://github.com/wfukatsu/Prompt-Templates/blob/main/system-design/domain-storytelling.md)

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0.0 | 2024 | 初版リリース |
| 1.1.0 | 2025-01 | ナレッジグラフ機能追加、ScalarDB Analytics対応 |
| 1.2.0 | 2026-01 | API設計、ScalarDBサイジング、グラフ可視化、HTMLレポート生成追加 |

---

*このドキュメントは Claude Code によって生成されました。*
