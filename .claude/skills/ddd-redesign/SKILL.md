---
name: ddd-redesign
description: DDD再設計エージェント - 境界コンテキスト・集約・値オブジェクトの再設計計画を生成。/ddd-redesign [対象パス] で呼び出し。
user_invocable: true
---

# DDD Redesign Agent

DDD評価結果に基づいて、システムの再設計計画を策定するエージェントです。

## 概要

このエージェントは以下を実行します：

1. **前提条件の検証** - 必要な入力ファイルの存在確認
2. **評価結果の統合** - DDD評価とMMI評価の結果を統合分析
3. **ドメイン分類** - ビジネス構造軸とサービス境界軸での分類
4. **戦略的設計の改善** - 境界コンテキストの再定義、コンテキストマップの再設計
5. **戦術的設計の改善** - 集約、エンティティ、値オブジェクトの再設計
6. **ユビキタス言語の整備** - 用語の統一と文書化
7. **移行計画の策定** - 段階的な移行ロードマップの作成

## 前提条件

### 必須入力ファイル

以下のファイルが存在すること：
- `reports/02_evaluation/ddd-strategic-evaluation.md` ← /ddd-evaluation で生成
- `reports/02_evaluation/ddd-tactical-evaluation.md` ← /ddd-evaluation で生成
- `reports/02_evaluation/ddd-improvement-plan.md` ← /ddd-evaluation で生成

### 推奨入力ファイル

以下のファイルが存在すれば参照：
- `reports/01_analysis/ubiquitous-language.md` ← /analyze-system で生成
- `reports/01_analysis/domain-code-mapping.md` ← /analyze-system で生成
- `reports/02_evaluation/mmi-overview.md` ← /evaluate-mmi で生成
- `reports/02_evaluation/mmi-improvement-plan.md` ← /evaluate-mmi で生成
- `reports/02_evaluation/integrated-evaluation.md` ← /integrate-evaluations で生成

## 出力先

結果は `reports/03_design/` に出力します。
中間状態は `work/{project}/design/ddd-redesign/` に記録します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

```
reports/03_design/
├── domain-analysis.md              # Step 3完了時（旧map-domainsの出力を統合）
├── bounded-contexts-redesign.md    # Step 4完了時
├── context-map.md                  # Step 5完了時（旧map-domainsの出力を統合）
├── aggregate-redesign.md           # Step 6完了時
├── ubiquitous-language-refined.md  # Step 7完了時
├── system-mapping.md               # Step 8完了時（旧map-domainsの出力を統合）
└── ddd-migration-roadmap.md        # Step 9完了時

work/{project}/design/ddd-redesign/
├── prerequisites-check.md          # 前提条件チェック結果
├── context-comparison.md           # 現行vs新設計の比較
├── aggregate-mapping.md            # 集約マッピング
└── redesign-progress.md            # 進捗状況
```

## 実行プロンプト

あなたはドメイン駆動設計（DDD）の再設計専門家エージェントです。以下の手順でDDD再設計を実行してください。

### Step 0: 前提条件の検証

**重要**: 実行前に必ず前提条件を確認してください。

```
必須ファイルの確認:
├── reports/02_evaluation/ddd-strategic-evaluation.md  [必須]
├── reports/02_evaluation/ddd-tactical-evaluation.md   [必須]
├── reports/02_evaluation/ddd-improvement-plan.md      [必須]
└── 上記すべてが存在すること

推奨ファイルの確認:
├── reports/01_analysis/ubiquitous-language.md         [推奨]
├── reports/01_analysis/domain-code-mapping.md         [推奨]
├── reports/02_evaluation/mmi-overview.md              [推奨]
├── reports/02_evaluation/mmi-improvement-plan.md      [推奨]
└── reports/02_evaluation/integrated-evaluation.md     [推奨]
```

**エラーハンドリング:**
- 必須ファイルが存在しない場合:
  ```
  ⚠️ 前提条件エラー: 以下のファイルが見つかりません
  - reports/02_evaluation/ddd-strategic-evaluation.md

  推奨アクション:
  1. /ddd-evaluation を実行してください
  2. 必要なファイルが生成されてから再実行してください
  ```
- 推奨ファイルが存在しない場合 → 警告を出して続行

**このステップ完了時に出力**: `work/{project}/design/ddd-redesign/prerequisites-check.md`

### Step 1: 評価結果の確認と統合

既存の評価結果を読み込み、課題を整理：

```
読み込み対象:
├── [必須] reports/02_evaluation/ddd-strategic-evaluation.md
├── [必須] reports/02_evaluation/ddd-tactical-evaluation.md
├── [必須] reports/02_evaluation/ddd-improvement-plan.md
├── [推奨] reports/02_evaluation/mmi-overview.md
├── [推奨] reports/02_evaluation/mmi-improvement-plan.md
└── [推奨] reports/01_analysis/ubiquitous-language.md
```

**統合分析の観点:**

1. **DDD評価からの課題**
   - 戦略的設計の問題（境界不明確、コンテキスト重複等）
   - 戦術的設計の問題（貧血モデル、集約過大等）

2. **MMI評価からの課題**（存在する場合）
   - 凝集度の低いモジュール → 境界コンテキスト再検討の候補
   - 結合度の高いモジュール → ACL導入の候補
   - 独立性の低いモジュール → サービス分離の候補

3. **課題の優先順位付け**
   - **Critical**: システム全体に影響、即座に対応必要
   - **High**: 主要機能に影響、早期対応推奨
   - **Medium**: 一部機能に影響、計画的に対応
   - **Low**: 改善推奨だが影響は限定的

### Step 2: ドメイン分類フレームワーク

各ドメインをビジネス構造軸とサービス境界軸で分類します。

**2.1 ビジネス構造軸（Domain Type）**

| タイプ | 特徴 | 判定基準 | 例 |
|-------|-----|---------|-----|
| **Pipeline Domain** | 順序的なデータ/処理フロー | 入力→処理→出力の明確なフロー | 注文処理、ワークフロー |
| **Blackboard Domain** | 共有データへの協調的アクセス | 複数エージェントが共有状態を更新 | 在庫管理、予約システム |
| **Dialogue Domain** | 双方向のインタラクション | リアルタイム通信、イベント駆動 | チャット、通知システム |
| **Hybrid** | 複数タイプの組み合わせ | 上記の複合 | ECサイト全体 |

**2.2 サービス境界軸（Service Category）**

| カテゴリ | 責務 | 判定基準 | 特徴 |
|---------|-----|---------|------|
| **Process Domain** | ビジネスプロセス実行 | 状態遷移、ワークフロー管理 | ステートフル、サガ管理 |
| **Master Domain** | マスタデータ管理 | CRUD操作、参照整合性 | データ整合性重視 |
| **Integration Domain** | 外部システム連携 | プロトコル変換、API呼び出し | アダプタ、変換処理 |
| **Supporting Domain** | 横断的機能提供 | 複数ドメインから利用 | 認証、ログ、通知 |

### Step 3: ドメイン分析

各ドメインの詳細分析を実施：

```
分析項目:
├── ドメイン名と概要
├── ビジネス構造タイプ（Pipeline/Blackboard/Dialogue/Hybrid）
├── サービスカテゴリ（Process/Master/Integration/Supporting）
├── Core/Supporting/Generic の分類
├── 主要なビジネスケイパビリティ
├── 含まれるエンティティ・集約
└── 他ドメインとの依存関係
```

**このステップ完了時に出力**: `reports/03_design/domain-analysis.md`

### Step 4: 境界コンテキストの再設計

**4.1 コンテキスト分割の検討**

```
分割基準:
├── ビジネスケイパビリティ
│   ├── 独立した価値提供単位
│   ├── ドメインエキスパートの責任範囲
│   └── ビジネスプロセスの境界
├── チーム構造（コンウェイの法則）
│   ├── 既存チーム境界
│   ├── 理想的なチーム構成
│   └── コミュニケーションパターン
├── 技術的制約
│   ├── データ整合性要件
│   ├── パフォーマンス要件
│   └── セキュリティ境界
├── 変更頻度
│   ├── 高頻度変更領域
│   ├── 安定領域
│   └── 規制対象領域
└── MMI評価結果（存在する場合）
    ├── 凝集度スコアの低いモジュール
    ├── 結合度スコアの高いモジュール
    └── 独立性スコアの低いモジュール
```

**4.2 コンテキスト定義テンプレート**

```yaml
Context:
  name: "Sales Context"
  type: "Core Domain"
  domain_type: "Pipeline"           # ビジネス構造軸
  service_category: "Process"       # サービス境界軸
  description: "販売・受注に関するビジネスロジック"
  responsibilities:
    - 注文の受付と管理
    - 顧客との契約管理
    - 価格計算と見積もり
  ubiquitous_language:
    - Order: 顧客からの購入要求
    - Quote: 見積もり
    - Contract: 取引契約
  boundaries:
    includes:
      - order/
      - pricing/
      - contract/
    excludes:
      - inventory/
      - shipping/
  aggregates:
    - Order
    - Quote
    - Contract
  dependencies:
    upstream:
      - Inventory Context (Customer-Supplier)
    downstream:
      - Shipping Context (Published Language)
  mmi_metrics:  # MMI評価からの参照（存在する場合）
    cohesion: 75
    coupling: 60
    independence: 70
```

**このステップ完了時に出力**: `reports/03_design/bounded-contexts-redesign.md`

### Step 5: コンテキストマップの再設計

**5.1 コンテキスト間関係パターン**

| パターン | 条件 | 適用場面 |
|---------|------|---------|
| **Partnership** | 両チームが対等、共同開発可能 | 密接に連携するコアドメイン間 |
| **Shared Kernel** | 変更管理可能、調整コスト許容範囲 | 共通ドメインモデルが必要 |
| **Customer-Supplier** | 依存関係明確、供給者がAPI管理 | 上流が下流の要求に応じる |
| **Conformist** | 上流に影響力なし | 外部システム、変更困難なレガシー |
| **Anti-Corruption Layer** | 上流モデルが自コンテキストに不適 | レガシー連携、外部API |
| **Open Host Service** | 多数の下流、標準化アクセス必要 | プラットフォームサービス |
| **Published Language** | 共通交換フォーマット必要 | イベント駆動、非同期連携 |
| **Separate Ways** | 連携不要 | 独立したコンテキスト |

**5.2 統合パターンの設計**

```
統合方式の選択:
├── 同期（RPC/REST）
│   ├── 用途: 即時応答が必要
│   ├── 注意: 結合度が高くなる
│   └── ACL配置: 呼び出し側
├── 非同期（メッセージ/イベント）
│   ├── 用途: 疎結合、イベント駆動
│   ├── 注意: 結果整合性の考慮
│   └── 変換層: メッセージハンドラ
└── 共有データベース（推奨しない）
    ├── 用途: 移行過渡期のみ
    ├── 注意: 高結合、スキーマ変更困難
    └── 目標: 早期に分離
```

**このステップ完了時に出力**: `reports/03_design/context-map.md`

### Step 6: 集約の再設計

**6.1 集約設計の原則**

```
設計原則:
├── 真の不変条件を保護
│   ├── ビジネスルールの特定
│   ├── トランザクション境界の明確化
│   └── 整合性要件の分析
├── 小さな集約を優先
│   ├── 1ルート + 少数のエンティティ/VO
│   ├── 参照はIDで行う
│   └── 結果整合性の活用
├── 集約間の参照
│   ├── IDによる参照のみ
│   ├── オブジェクト参照は避ける
│   └── 遅延ロードに注意
└── 集約ルートの責務
    ├── 不変条件の強制
    ├── 内部への唯一のアクセスポイント
    └── ライフサイクル管理
```

**6.2 集約定義テンプレート**

```yaml
Aggregate:
  name: Order
  context: Sales Context
  root: Order
  entities:
    - OrderItem
  value_objects:
    - Money
    - OrderStatus
    - ShippingAddress
  invariants:
    - "注文合計は0より大きい"
    - "キャンセル済み注文は変更不可"
    - "注文項目は1つ以上必要"
  domain_events:
    - OrderPlaced
    - OrderConfirmed
    - OrderCancelled
  repository:
    interface: OrderRepository
    methods:
      - findById(OrderId): Order
      - save(Order): void
      - nextIdentity(): OrderId
  current_issues:  # DDD評価からの問題点
    - "OrderItemがルートから独立してアクセスされている"
    - "Moneyがプリミティブで表現されている"
  recommended_changes:
    - "OrderItemへのアクセスをOrderルート経由に変更"
    - "MoneyをValue Objectとして実装"
```

**このステップ完了時に出力**: `reports/03_design/aggregate-redesign.md`

### Step 7: ユビキタス言語の整備

**7.1 用語の統一**

```
整備内容:
├── 用語定義の明確化
│   ├── 日本語名
│   ├── 英語名（コード上の名称）
│   ├── 定義
│   └── 使用例
├── コンテキスト別の用語
│   ├── 同じ用語の異なる意味
│   ├── コンテキスト固有の用語
│   └── 共通用語（Shared Kernel）
└── 禁止用語・非推奨用語
    ├── 曖昧な用語
    ├── 技術用語の混入
    └── 古い用語
```

**このステップ完了時に出力**: `reports/03_design/ubiquitous-language-refined.md`

### Step 8: システムマッピング

現行システムから新設計へのマッピングを作成：

```
マッピング内容:
├── 現行モジュール → 新コンテキスト対応表
├── 現行テーブル → 新集約対応表
├── トランザクション境界の変更点
├── データ移行計画の概要
└── 依存関係の変更点
```

**このステップ完了時に出力**: `reports/03_design/system-mapping.md`

### Step 9: 移行ロードマップの策定

**9.1 フェーズ分割**

```
Phase 0: 準備
├── チーム編成とトレーニング
├── 開発環境の整備
├── 既存コードの安定化
└── 監視・ログの強化

Phase 1: 基盤構築
├── 境界コンテキストの物理分離準備
├── 共通ライブラリの整備
├── ACL/変換層の実装
└── CI/CDパイプラインの整備

Phase 2: コア集約の再設計
├── 最重要集約から着手
├── リッチドメインモデルへの移行
├── 値オブジェクトの導入
└── 単体テストの充実

Phase 3: コンテキスト分離
├── サービス分離
├── データベース分離
├── イベント駆動の導入
└── 統合テストの充実

Phase 4: 最適化（継続的）
├── パフォーマンスチューニング
├── 監視・アラートの最適化
├── ドキュメント整備
└── チーム間プロセスの改善
```

**9.2 リスク管理**

```
リスク項目:
├── 技術的リスク
│   ├── データ移行の失敗
│   ├── パフォーマンス劣化
│   └── 統合テストの不足
├── 組織的リスク
│   ├── スキル不足
│   ├── チーム間コミュニケーション
│   └── ステークホルダーの理解
└── ビジネスリスク
    ├── 機能追加の遅延
    ├── 運用コストの増加
    └── 障害時の影響範囲
```

**このステップ完了時に出力**: `reports/03_design/ddd-migration-roadmap.md`

### Step 10: Mermaid図の検証

出力したファイルのMermaid図を検証し、エラーがあれば修正：

```bash
/fix-mermaid ./reports/03_design
```

## エラーハンドリング

| エラー | 対応 |
|-------|------|
| 必須ファイルが存在しない | `/ddd-evaluation` の実行を促す |
| MMI評価結果がない | 警告を出して続行（MMI関連項目をスキップ） |
| コンテキスト分割が困難 | モジュラーモノリスを提案 |
| 集約境界が不明確 | イベントストーミングの実施を推奨 |

## 関連スキル

| スキル | 関係 |
|-------|-----|
| `/ddd-evaluation` | **必須前提** - 再設計の入力となる評価 |
| `/evaluate-mmi` | **推奨前提** - モジュール成熟度の定量評価 |
| `/integrate-evaluations` | **推奨前提** - 評価結果の統合 |
| `/analyze-system` | **参照** - ユビキタス言語の初期抽出 |
| `/design-microservices` | **後続** - マイクロサービスアーキテクチャ設計 |
| `/design-scalardb` | **後続** - データアーキテクチャ設計 |

## 注意事項

このスキルは以下の機能を統合しています：
- 旧 `/map-domains` のドメイン分類機能
- 旧 `/map-domains` のコンテキストマップ作成機能
- 旧 `/map-domains` のシステムマッピング機能

`/map-domains` は簡易版として残っていますが、完全なDDD再設計を行う場合はこの `/ddd-redesign` を使用してください。
