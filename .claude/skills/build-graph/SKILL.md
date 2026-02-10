---
name: build-graph
description: GraphDB構築エージェント - ユビキタス言語とコード解析結果からRyuGraphデータベースを構築。/build-graph [対象パス] で呼び出し。
user_invocable: true
---

# GraphDB構築エージェント

既存のシステム分析結果とソースコードを解析し、RyuGraph GraphDBにユビキタス言語ベースのナレッジグラフを構築するエージェントです。

## 目的

このエージェントは以下を実行します：

1. **分析結果の収集** - `/analyze-system` の出力（ユビキタス言語、ドメイン-コード対応表等）を収集
2. **コード解析** - Serenaツールでソースコードの構造を解析
3. **グラフ構築** - RyuGraphにノードとリレーションシップを登録
4. **メタデータ保存** - グラフのスキーマ情報と統計を保存

## 前提条件

**環境:**
- Python 3.9+
- ryugraph パッケージ (`pip install ryugraph`)

**推奨（/analyze-system の出力）:**
- `reports/01_analysis/ubiquitous-language.md` - ユビキタス言語
- `reports/01_analysis/domain-code-mapping.md` - ドメイン-コード対応
- `reports/01_analysis/actors-roles-permissions.md` - アクター・ロール
- `reports/01_analysis/system-overview.md` - システム概要

**必須:**
- 対象コードベースへのアクセス

## グラフスキーマ

### ノードテーブル

| テーブル | 説明 | プロパティ |
|---------|------|-----------|
| `UbiquitousTerm` | ユビキタス言語の用語 | name (PK), name_ja, definition, domain |
| `Domain` | ビジネスドメイン | name (PK), type, description |
| `Entity` | クラス/インターフェース | name (PK), file_path, type, line_number |
| `Method` | メソッド/関数 | name (PK), signature, file_path, line_number |
| `File` | ソースファイル | path (PK), language, module |
| `Actor` | アクター（人/システム） | name (PK), type, description |
| `Role` | ロール/権限 | name (PK), permissions |
| `BusinessProcess` | ビジネスプロセス | name (PK), name_ja, description, domain, trigger_event |
| `Activity` | プロセス内のアクティビティ | name (PK), name_ja, description, sequence_order, is_decision |
| `SystemProcess` | システムプロセス | name (PK), type, description, is_async, timeout_ms |

### プロセスノードの詳細

#### BusinessProcess（ビジネスプロセス）
業務フローを表現。例：注文処理、承認フロー、返品処理など。

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| name | string (PK) | 一意識別子（例: OrderProcessing） |
| name_ja | string | 日本語名（例: 注文処理） |
| description | string | プロセスの説明 |
| domain | string | 所属ドメイン |
| trigger_event | string | トリガーイベント（例: ORDER_SUBMITTED） |

#### Activity（アクティビティ）
プロセス内の個々のステップ。分岐点（ゲートウェイ）も含む。

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| name | string (PK) | 一意識別子（例: ValidateOrder） |
| name_ja | string | 日本語名（例: 注文検証） |
| description | string | アクティビティの説明 |
| sequence_order | int | プロセス内の実行順序 |
| is_decision | boolean | 分岐点かどうか |

#### SystemProcess（システムプロセス）
バッチ処理、Saga、データ同期などの技術的プロセス。

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| name | string (PK) | 一意識別子（例: OrderSaga） |
| type | string | タイプ（batch/saga/sync/event_handler） |
| description | string | プロセスの説明 |
| is_async | boolean | 非同期処理かどうか |
| timeout_ms | int | タイムアウト（ミリ秒） |

### リレーションテーブル

| テーブル | FROM → TO | 説明 |
|---------|-----------|------|
| `BELONGS_TO` | Entity → Domain | ドメインへの所属 |
| `DEFINED_IN` | Entity/Method → File | ファイルでの定義 |
| `REFERENCES` | Entity/Method → Entity | 参照関係 |
| `CALLS` | Method → Method | 呼び出し関係 |
| `IMPLEMENTS` | Entity → Entity | 実装/継承関係 |
| `HAS_TERM` | Entity/Method → UbiquitousTerm | 用語との関連 |
| `HAS_ROLE` | Actor → Role | ロールの保持 |
| `HAS_ACTIVITY` | BusinessProcess/SystemProcess → Activity | プロセスがアクティビティを持つ |
| `NEXT_ACTIVITY` | Activity → Activity | 次のアクティビティへの遷移 |
| `PERFORMS` | Actor → Activity | アクターがアクティビティを実行 |
| `TRIGGERS` | Activity → SystemProcess | アクティビティがシステムプロセスをトリガー |
| `INVOKES` | Activity/SystemProcess → Method | メソッドの呼び出し |
| `PARTICIPATES_IN` | Entity → BusinessProcess | エンティティがプロセスに参加 |
| `COMPENSATES` | SystemProcess → SystemProcess | Saga補償トランザクション |

### プロセスリレーションの詳細

| リレーション | プロパティ | 説明 |
|-------------|-----------|------|
| `NEXT_ACTIVITY` | condition | 遷移条件（分岐時に使用） |
| `PERFORMS` | - | アクターがどのアクティビティを実行するか |
| `TRIGGERS` | event_name | トリガーするイベント名 |
| `INVOKES` | - | どのメソッドを呼び出すか |
| `COMPENSATES` | - | どのSagaステップを補償するか |

## 実行プロンプト

あなたはGraphDBを構築する専門家エージェントです。以下の手順でRyuGraphデータベースを構築してください。

### Step 0: 前提条件の検証

**重要**: 実行前に必ず前提条件を確認してください。

```
推奨ファイルの確認:
├── reports/01_analysis/ubiquitous-language.md      [推奨] ← /analyze-system
├── reports/01_analysis/domain-code-mapping.md      [推奨] ← /analyze-system
├── reports/01_analysis/actors-roles-permissions.md [推奨] ← /analyze-system
└── reports/01_analysis/system-overview.md          [推奨] ← /analyze-system

必須:
└── 対象コードベースへのアクセス                    [必須]
```

**エラーハンドリング:**
- 推奨ファイルが存在しない場合 → 警告を表示してコードベースから直接構築
- 対象コードベースにアクセスできない場合 → エラー終了

### Step 1: 入力情報の確認

まず、対象ディレクトリと分析結果の有無を確認します。

```bash
# 引数から対象パスを取得
TARGET_PATH=$1  # 例: ./src

# 分析結果の存在確認
ls ${TARGET_PATH}/reports/01_analysis/
```

### Step 2: 分析結果の読み込み

分析結果が存在する場合、以下のファイルを読み込みます：

```
reports/01_analysis/
├── ubiquitous-language.md      # ユビキタス言語
├── domain-code-mapping.md      # ドメイン-コード対応
├── actors-roles-permissions.md # アクター・ロール
└── system-overview.md          # システム概要
```

**重要:** Markdownのテーブルをパースして構造化データに変換します。

### Step 3: コードベースの解析

Serenaツールを使用してコード構造を取得：

```
# シンボル概要を取得
mcp__serena__get_symbols_overview で主要ファイルを解析

# クラス/メソッドの詳細を取得
mcp__serena__find_symbol で重要なシンボルを検索

# 参照関係を取得
mcp__serena__find_referencing_symbols で依存関係を分析
```

### Step 4: グラフデータの生成

収集した情報からグラフデータを生成します。

**ノードデータ（CSVファイル）:**

```csv
# terms.csv
name,name_ja,definition,domain
Order,注文,顧客が商品を購入する単位,コアドメイン
Customer,顧客,システムの利用者,コアドメイン

# entities.csv
name,file_path,type,line_number
Order,src/domain/order.ts,class,10
Customer,src/domain/customer.ts,class,5

# methods.csv
name,signature,file_path,line_number
createOrder,createOrder(items: Item[]): Order,src/service/order.ts,25

# business_processes.csv
name,name_ja,description,domain,trigger_event
OrderProcessing,注文処理,顧客からの注文を処理する業務フロー,OrderManagement,ORDER_SUBMITTED
ApprovalWorkflow,承認ワークフロー,高額注文の承認フロー,OrderManagement,HIGH_VALUE_ORDER_CREATED
ReturnProcessing,返品処理,商品返品を処理する業務フロー,OrderManagement,RETURN_REQUESTED

# activities.csv
name,name_ja,description,sequence_order,is_decision
ValidateOrder,注文検証,注文内容の妥当性を確認,1,false
CheckInventory,在庫確認,在庫の有無を確認,2,false
IsHighValue,高額判定,注文金額が閾値を超えるか判定,3,true
ProcessPayment,決済処理,支払い処理を実行,4,false
SendConfirmation,確認送信,注文確認メールを送信,5,false

# system_processes.csv
name,type,description,is_async,timeout_ms
OrderSaga,saga,注文処理のSagaオーケストレーション,true,30000
InventorySync,sync,在庫データの同期処理,true,60000
PaymentEventHandler,event_handler,決済イベントの処理,true,10000
DailyReportBatch,batch,日次レポート生成バッチ,true,3600000
```

**リレーションデータ（CSVファイル）:**

```csv
# belongs_to.csv
entity,domain
Order,OrderManagement
Customer,CustomerManagement

# has_term.csv
entity,term
Order,Order
CustomerService,Customer

# has_activity.csv
process,activity
OrderProcessing,ValidateOrder
OrderProcessing,CheckInventory
OrderProcessing,IsHighValue
OrderProcessing,ProcessPayment
OrderProcessing,SendConfirmation
OrderSaga,ValidateOrder
OrderSaga,CheckInventory
OrderSaga,ProcessPayment

# next_activity.csv
from_activity,to_activity,condition
ValidateOrder,CheckInventory,
CheckInventory,IsHighValue,
IsHighValue,ProcessPayment,amount < 100000
IsHighValue,ApprovalRequired,amount >= 100000
ProcessPayment,SendConfirmation,

# performs.csv
actor,activity
Customer,SubmitOrder
SalesRep,ApproveOrder
System,ProcessPayment
System,SendConfirmation

# triggers.csv
activity,system_process,event_name
ProcessPayment,PaymentEventHandler,PAYMENT_COMPLETED
ValidateOrder,InventorySync,INVENTORY_CHECK_REQUESTED

# invokes.csv
source,method
ValidateOrder,OrderValidator.validate
CheckInventory,InventoryService.checkStock
ProcessPayment,PaymentService.processPayment
OrderSaga,OrderSagaOrchestrator.execute

# participates_in.csv
entity,process
Order,OrderProcessing
OrderItem,OrderProcessing
Payment,OrderProcessing
Inventory,OrderProcessing

# compensates.csv
saga_step,compensating_step
ProcessPayment,RefundPayment
ReserveInventory,ReleaseInventory
CreateOrder,CancelOrder
```

### Step 5: RyuGraphデータベースの構築

Pythonスクリプトを実行してグラフを構築：

```bash
python scripts/build_graph.py \
  --data-dir ${TARGET_PATH}/reports/graph/data \
  --db-path ${TARGET_PATH}/knowledge.ryugraph
```

### Step 6: 検証クエリの実行

構築したグラフの整合性を確認：

```cypher
# ノード数の確認
MATCH (n) RETURN labels(n), count(*);

# リレーション数の確認
MATCH ()-[r]->() RETURN type(r), count(*);

# サンプルクエリ
MATCH (e:Entity)-[:HAS_TERM]->(t:UbiquitousTerm)
RETURN e.name, t.name_ja LIMIT 10;
```

## 出力

### ファイル構成

```
<対象プロジェクト>/
├── knowledge.ryugraph/          # RyuGraphデータベース
└── reports/
    └── graph/
        ├── data/                # 中間CSVファイル
        │   ├── terms.csv
        │   ├── domains.csv
        │   ├── entities.csv
        │   ├── methods.csv
        │   ├── files.csv
        │   ├── actors.csv
        │   ├── roles.csv
        │   ├── business_processes.csv   # ビジネスプロセス
        │   ├── activities.csv           # アクティビティ
        │   ├── system_processes.csv     # システムプロセス
        │   ├── belongs_to.csv
        │   ├── defined_in.csv
        │   ├── references.csv
        │   ├── calls.csv
        │   ├── implements.csv
        │   ├── has_term.csv
        │   ├── has_role.csv
        │   ├── has_activity.csv         # プロセス→アクティビティ
        │   ├── next_activity.csv        # アクティビティ遷移
        │   ├── performs.csv             # アクター→アクティビティ
        │   ├── triggers.csv             # アクティビティ→システムプロセス
        │   ├── invokes.csv              # プロセス/アクティビティ→メソッド
        │   ├── participates_in.csv      # エンティティ→プロセス
        │   └── compensates.csv          # Saga補償関係
        ├── schema.md            # グラフスキーマ説明
        └── statistics.md        # グラフ統計情報
```

### statistics.md の形式

```markdown
# GraphDB統計情報

## 生成日時
2024-XX-XX HH:MM:SS

## ノード統計

| ノードタイプ | 件数 |
|------------|------|
| UbiquitousTerm | 45 |
| Domain | 6 |
| Entity | 120 |
| Method | 350 |
| File | 80 |
| Actor | 5 |
| Role | 8 |
| BusinessProcess | 12 |
| Activity | 48 |
| SystemProcess | 8 |

## リレーション統計

| リレーションタイプ | 件数 |
|------------------|------|
| BELONGS_TO | 120 |
| DEFINED_IN | 470 |
| REFERENCES | 890 |
| CALLS | 1200 |
| IMPLEMENTS | 45 |
| HAS_TERM | 280 |
| HAS_ROLE | 12 |
| HAS_ACTIVITY | 48 |
| NEXT_ACTIVITY | 42 |
| PERFORMS | 35 |
| TRIGGERS | 15 |
| INVOKES | 60 |
| PARTICIPATES_IN | 85 |
| COMPENSATES | 8 |

## プロセス統計

| プロセスタイプ | 件数 | アクティビティ数 |
|--------------|------|----------------|
| BusinessProcess | 12 | 48 |
| SystemProcess (saga) | 3 | 12 |
| SystemProcess (batch) | 2 | 4 |
| SystemProcess (sync) | 2 | 6 |
| SystemProcess (event_handler) | 1 | 2 |

## データソース

- 分析結果: あり
- コード解析: あり
- 対象ファイル数: 80
- プロセス定義ファイル: あり
```

## ツール使用ガイドライン

### 優先順位

1. **分析結果の読み込み** - Readツールでマークダウンを解析
2. **Serenaツール** - コードのシンボリック解析
3. **Bashツール** - Pythonスクリプトの実行

### 注意事項

- 大規模プロジェクトでは、主要なディレクトリのみを解析対象にする
- 外部ライブラリ（node_modules, vendor等）は除外する
- メソッド/関数の呼び出し関係は、静的解析の限界があることを警告する

## エラーハンドリング

- ryugraphがインストールされていない → `pip install ryugraph` を提案
- 分析結果がない → コードのみから構築（精度低下を警告）
- 対象言語非対応 → 手動でCSVを作成するよう案内
