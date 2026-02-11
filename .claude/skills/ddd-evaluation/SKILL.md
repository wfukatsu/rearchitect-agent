---
name: ddd-evaluation
description: DDD評価エージェント - 戦略的設計・戦術的設計の両面からDDD原則への適合度を評価し改善点を特定。/ddd-evaluation [対象パス] で呼び出し。
user_invocable: true
---

# DDD Evaluation Agent

ドメイン駆動設計（DDD）の視点から既存システムを評価し、改善点を特定するエージェントです。

## 概要

このエージェントは以下を実行します：

1. **戦略的設計の評価** - 境界コンテキスト、ユビキタス言語、コンテキストマップの分析
2. **戦術的設計の評価** - エンティティ、値オブジェクト、集約、リポジトリの分析
3. **パターン適用状況** - DDDパターンの適用度と品質を評価
4. **改善提案** - 具体的な改善アクションを提案

## 前提条件

- 対象システムのソースコードにアクセス可能であること
- 以下の中間ファイルが存在すること（推奨）：
  - `reports/01_analysis/ubiquitous-language.md` ← /analyze-system で生成
  - `reports/before/{project}/ddd-readiness.md` ← /system-investigation で生成

## 出力先

結果は `reports/02_evaluation/` に出力します。
中間状態は `work/{project}/investigation/ddd-evaluation/` に記録します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

```
reports/02_evaluation/
├── ddd-strategic-evaluation.md  # Step 1完了時
├── ddd-tactical-evaluation.md   # Step 2完了時
├── ddd-pattern-analysis.md      # Step 3完了時
└── ddd-improvement-plan.md      # Step 4完了時

work/{project}/investigation/ddd-evaluation/
├── context-candidates.md        # コンテキスト候補
├── aggregate-candidates.md      # 集約候補
└── evaluation-progress.md       # 進捗状況
```

## 実行プロンプト

あなたはドメイン駆動設計（DDD）の専門家エージェントです。以下の手順でDDD評価を実行してください。

### Step 0: 前提条件の検証

**重要**: 実行前に必ず前提条件を確認してください。

```
推奨ファイルの確認:
├── reports/01_analysis/ubiquitous-language.md      [推奨] ← /analyze-system
├── reports/01_analysis/domain-code-mapping.md      [推奨] ← /analyze-system
└── reports/before/{project}/ddd-readiness.md       [推奨] ← /system-investigation

必須:
└── 対象コードベースへのアクセス                    [必須]
```

**エラーハンドリング:**
- 推奨ファイルが存在しない場合 → 警告を表示してコードベースから直接分析
- 対象コードベースにアクセスできない場合 → エラー終了

### Step 1: 戦略的設計の評価

**1.1 境界コンテキストの分析**

```
評価項目:
├── コンテキスト境界の明確さ
│   ├── モジュール/パッケージによる分離
│   ├── 名前空間による分離
│   └── 責務の分離度
├── コンテキスト間の関係
│   ├── 依存の方向性
│   ├── 共有カーネルの有無
│   └── 腐敗防止層の有無
└── コンテキストの独立性
    ├── デプロイ独立性
    ├── データ独立性
    └── チーム独立性
```

**1.2 ユビキタス言語の分析**

```
評価項目:
├── 用語の一貫性
│   ├── コード内での命名
│   ├── コメント/ドキュメント
│   └── テストケース名
├── ドメインエキスパートとの整合性
│   ├── ビジネス用語の使用
│   ├── 技術用語の混入度
│   └── 略語の使用状況
└── コンテキスト間での用語の分離
    ├── 同一用語の異なる意味
    ├── ポリセミ（多義語）の検出
    └── コンテキスト固有の語彙
```

**1.3 コンテキストマップの分析**

```
関係パターンの検出:
├── Partnership（協力関係）
├── Shared Kernel（共有カーネル）
├── Customer-Supplier（顧客-供給者）
├── Conformist（順応者）
├── Anti-Corruption Layer（腐敗防止層）
├── Open Host Service（公開ホストサービス）
├── Published Language（公表された言語）
└── Separate Ways（別々の道）
```

**このステップ完了時に出力**: `reports/02_evaluation/ddd-strategic-evaluation.md`

### Step 2: 戦術的設計の評価

**2.1 エンティティの分析**

```
評価項目:
├── 識別子の設計
│   ├── ID生成戦略
│   ├── 自然キー vs サロゲートキー
│   └── ID型の適切さ
├── ライフサイクル管理
│   ├── 生成パターン
│   ├── 状態遷移
│   └── 不変条件
└── 振る舞いの充実度
    ├── ビジネスロジックの配置
    ├── 貧血ドメインモデルの検出
    └── Tell, Don't Askの適用
```

**2.2 値オブジェクトの分析**

```
評価項目:
├── 不変性の確保
│   ├── イミュータブル設計
│   ├── 副作用のない操作
│   └── コンストラクタでの検証
├── 等価性の実装
│   ├── equals/hashCode
│   ├── 構造的同一性
│   └── 型安全性
└── 値オブジェクト候補の検出
    ├── プリミティブ執着の検出
    ├── 複合値の検出
    └── 型エイリアスの検出
```

**2.3 集約の分析**

```
評価項目:
├── 集約ルートの特定
│   ├── ルートの責務
│   ├── 不変条件の保護
│   └── トランザクション境界
├── 集約サイズの適切さ
│   ├── 小さすぎる集約
│   ├── 大きすぎる集約
│   └── 参照vs値の判断
└── 集約間の参照
    ├── IDによる参照
    ├── オブジェクト参照の回避
    └── 整合性境界
```

**2.4 リポジトリの分析**

```
評価項目:
├── インターフェース設計
│   ├── コレクション指向 vs 永続化指向
│   ├── クエリメソッドの設計
│   └── 仕様パターンの適用
├── 実装の品質
│   ├── インフラ層への分離
│   ├── テスト容易性
│   └── トランザクション管理
└── 集約単位の永続化
    ├── 集約全体の保存
    ├── 遅延ロード戦略
    └── キャッシュ戦略
```

**2.5 ドメインサービスの分析**

```
評価項目:
├── サービスの責務
│   ├── ステートレス性
│   ├── ドメインロジックの配置
│   └── 複数集約の協調
├── サービスの粒度
│   ├── 単一責任
│   ├── インターフェースの明確さ
│   └── 依存の最小化
└── アプリケーションサービスとの区別
    ├── ユースケース層との分離
    ├── トランザクション管理
    └── セキュリティ/認可
```

**このステップ完了時に出力**: `reports/02_evaluation/ddd-tactical-evaluation.md`

### Step 3: パターン適用状況の分析

**検出対象パターン:**

```
戦術的パターン:
├── Factory（ファクトリ）
├── Repository（リポジトリ）
├── Domain Event（ドメインイベント）
├── Domain Service（ドメインサービス）
├── Application Service（アプリケーションサービス）
├── Specification（仕様）
└── Policy（ポリシー）

アーキテクチャパターン:
├── Layered Architecture（レイヤードアーキテクチャ）
├── Hexagonal Architecture（ヘキサゴナルアーキテクチャ）
├── Clean Architecture（クリーンアーキテクチャ）
├── CQRS
└── Event Sourcing
```

**このステップ完了時に出力**: `reports/02_evaluation/ddd-pattern-analysis.md`

### Step 4: 改善計画の策定

分析結果に基づいて改善計画を策定：

```
改善計画の構造:
├── 短期改善（1-2週間）
│   ├── クイックウィン
│   ├── 命名の統一
│   └── 明らかな問題の修正
├── 中期改善（1-3ヶ月）
│   ├── 集約の再設計
│   ├── コンテキスト境界の明確化
│   └── リポジトリの改善
└── 長期改善（3ヶ月以上）
    ├── アーキテクチャ変更
    ├── コンテキスト分割
    └── イベント駆動化
```

**このステップ完了時に出力**: `reports/02_evaluation/ddd-improvement-plan.md`

### Step 5: Mermaid図の検証

出力したファイルのMermaid図を検証し、エラーがあれば修正：

```bash
/fix-mermaid ./reports/02_evaluation
```

## スコア算出ルール

スコアは `.claude/rules/evaluation-frameworks.md` の「2. DDD評価フレームワーク」に定義された計算式に従って算出する。

**総合DDDスコア:**
```
DDD Score = Strategic × 0.30 + Tactical × 0.45 + Architecture × 0.25
```

**各カテゴリの算出:**
```
Strategic     = UbiquitousLanguage × 0.33 + BoundedContext × 0.34 + SubdomainClassification × 0.33
Tactical      = ValueObject × 0.20 + Entity × 0.20 + Aggregate × 0.20 + Repository × 0.15 + DomainService × 0.10 + DomainEvent × 0.15
Architecture  = LayerSeparation × 0.40 + DependencyDirection × 0.35 + PortsAndAdapters × 0.25
```

**各サブ項目**: 0-100で採点（詳細基準は `evaluation-frameworks.md` §2.3 参照）

**成熟度グレード**: A(80-100), B(70-79), C(60-69), D(50-59), E(0-49)

## 出力フォーマット

### ddd-strategic-evaluation.md

```markdown
# DDD戦略的設計評価

## 評価サマリー

| 評価項目 | スコア | グレード |
|---------|--------|---------|
| ユビキタス言語 | [0-100] | [A-E] |
| 境界コンテキスト | [0-100] | [A-E] |
| サブドメイン分類 | [0-100] | [A-E] |
| **戦略的設計スコア** | **[加重平均]** | **[A-E]** |

## 境界コンテキスト分析

### 検出されたコンテキスト

\`\`\`mermaid
graph TD
    subgraph "Sales Context"
        Order
        Customer
    end
    subgraph "Inventory Context"
        Product
        Stock
    end
    subgraph "Shipping Context"
        Shipment
        Delivery
    end
    Order --> Product
    Shipment --> Order
\`\`\`

### コンテキスト評価

| コンテキスト | 境界明確度 | 独立性 | 課題 |
|-------------|-----------|--------|------|
| Sales | 70% | Medium | 在庫への直接依存 |
| Inventory | 80% | High | - |
| Shipping | 50% | Low | 複数コンテキストへ依存 |

## ユビキタス言語分析

### 用語の一貫性

| 用語 | 使用箇所 | 一貫性 | 問題点 |
|-----|---------|--------|--------|
| Order | 15ファイル | 90% | 一部で「注文」と混在 |
| User/Customer | 20ファイル | 40% | 用語が統一されていない |

## コンテキストマップ

\`\`\`mermaid
graph LR
    Sales -->|Customer-Supplier| Inventory
    Sales -->|Partnership| Payment
    Shipping -->|Conformist| Sales
    Notification -->|ACL| Sales
\`\`\`
```

### ddd-tactical-evaluation.md

```markdown
# DDD戦術的設計評価

## 評価サマリー

| 要素 | 検出数 | スコア (0-100) | 重み | 加重スコア | グレード |
|-----|--------|:-------------:|:----:|:---------:|:-------:|
| 値オブジェクト | [N] | [X] | 20% | [X×0.20] | [A-E] |
| エンティティ | [N] | [X] | 20% | [X×0.20] | [A-E] |
| 集約 | [N] | [X] | 20% | [X×0.20] | [A-E] |
| リポジトリ | [N] | [X] | 15% | [X×0.15] | [A-E] |
| ドメインサービス | [N] | [X] | 10% | [X×0.10] | [A-E] |
| ドメインイベント | [N] | [X] | 15% | [X×0.15] | [A-E] |
| **戦術的設計スコア** | | | | **[合計]** | **[A-E]** |

## エンティティ分析

### 検出されたエンティティ

| エンティティ | 場所 | ID設計 | 振る舞い | 評価 |
|-------------|------|--------|---------|------|
| User | domain/user.ts | UUID | 貧血 | C |
| Order | domain/order.ts | 連番 | リッチ | B |
| Product | domain/product.ts | SKU | 貧血 | C |

### 貧血ドメインモデルの検出

- `User` - 15個のgetter/setterのみ、ビジネスロジックなし
- `Product` - 価格計算がサービス層に漏出

## 値オブジェクト分析

### 値オブジェクト候補

| 候補 | 現在の実装 | 推奨 |
|-----|-----------|------|
| Email | string | EmailValueObject |
| Money | number | MoneyValueObject |
| Address | 複数フィールド | AddressValueObject |

## 集約分析

### 集約ルート一覧

| 集約ルート | メンバー | サイズ評価 | 問題点 |
|-----------|---------|-----------|--------|
| Order | OrderItem, Payment | 適切 | - |
| User | Profile, Settings, Orders | 大きすぎ | Ordersを分離推奨 |
```

## ツール活用ガイドライン

### 優先順位

1. **Serenaツール** - シンボリック解析に最適
2. **Glob/Grep** - パターンマッチング
3. **Read** - 詳細確認

### Serena活用パターン

```
# エンティティの検出
mcp__serena__search_for_pattern(substring_pattern="@Entity|class.*Entity", restrict_search_to_code_files=true)

# リポジトリの検出
mcp__serena__find_symbol(name_path_pattern="Repository", substring_matching=true, depth=1)

# 集約ルートの検出
mcp__serena__search_for_pattern(substring_pattern="@AggregateRoot|AggregateRoot", restrict_search_to_code_files=true)

# ドメインイベントの検出
mcp__serena__search_for_pattern(substring_pattern="DomainEvent|Event$", restrict_search_to_code_files=true)
```

## エラーハンドリング

- **前提ファイルが存在しない場合** → コードベースから直接分析
- **DDDパターンが検出されない場合** → 「未適用」として報告し、推奨事項を提示
- **大規模コードベースの場合** → 主要モジュールに絞って分析

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/system-investigation` | 事前調査（DDD適合性の初期評価） |
| `/analyze-system` | ユビキタス言語の詳細抽出 |
| `/ddd-redesign` | 評価結果に基づく再設計計画 |
| `/map-domains` | 境界コンテキストの詳細設計 |
