---
name: design-scalardb
description: ScalarDB設計エージェント - ScalarDBを使用したマイクロサービスのデータアーキテクチャ設計。分散トランザクション、スキーマ設計、ポリグロット永続化を策定。/design-scalardb [対象パス] で呼び出し。
user_invocable: true
---

# ScalarDB Design Agent

ScalarDBを使用したマイクロサービスのデータアーキテクチャを設計するエージェントです。

## 概要

このエージェントは、既存システムの分析結果をもとに、ScalarDBを活用した以下の設計を策定します：

1. **ScalarDBアーキテクチャ設計** - デプロイモード、ストレージバックエンド選定
2. **スキーマ設計** - テーブル設計、パーティションキー、クラスタリングキー
3. **トランザクション設計** - 分散トランザクション戦略、Sagaパターン
4. **マイグレーション計画** - 既存DBからの移行戦略

## 前提条件

以下の中間ファイルが存在すること：
- `01_analysis/` 配下の分析結果
- `03_design/target_architecture.md`

## ScalarDB概要

ScalarDBは異種データベース間で分散トランザクションを実現するHTAPエンジンです。

### 主要機能

| 機能 | 説明 |
|-----|------|
| **Consensus Commit** | 単一ストレージでのACIDトランザクション |
| **Two-Phase Commit** | 複数ストレージ間の分散トランザクション |
| **Multi-Storage Transaction** | 異種DB間のアトミック操作 |
| **ScalarDB Cluster** | gRPCベースの集中型トランザクションコーディネーター |

### サポートストレージ

| カテゴリ | データベース |
|---------|------------|
| **JDBC** | MySQL, PostgreSQL, Oracle, SQL Server, Db2 |
| **NoSQL** | Cassandra, DynamoDB, Cosmos DB, YugabyteDB |
| **Object Storage** | S3, Azure Blob, GCS |

## 実行プロンプト

あなたはScalarDBを使用したマイクロサービスデータアーキテクチャの設計専門家です。以下の手順で設計を実行してください。

### Step 1: 現状分析

現在のデータアーキテクチャを分析：

```markdown
## 現状分析

### データソース一覧
| データソース | 種別 | 用途 | データ量 | トランザクション要件 |
|-------------|-----|------|---------|-------------------|

### クロスサービストランザクション
| トランザクション名 | 関連サービス | 整合性要件 | 現状の実装 |
|------------------|-------------|-----------|-----------|

### 課題
- [課題1]
- [課題2]
```

### Step 2: デプロイモード選定

#### ScalarDB Core（ライブラリモード）

```yaml
# 適用条件
- サービス数が少ない（5サービス以下）
- トランザクション頻度が低い
- シンプルな構成を優先

# 構成
Application --> ScalarDB Core --> Database
```

#### ScalarDB Cluster（サーバーモード）

```yaml
# 適用条件
- マイクロサービスアーキテクチャ
- 高いトランザクション整合性が必要
- 複数サービスから共通のトランザクションコーディネーターが必要

# 構成
Application --> gRPC --> ScalarDB Cluster --> Multiple Databases
```

**選定マトリクス：**

| 要件 | Core | Cluster |
|-----|------|---------|
| シンプルな構成 | ○ | △ |
| 高可用性 | △ | ○ |
| マルチテナント | × | ○ |
| GraphQL/SQL対応 | × | ○ |
| ベクトル検索 | × | ○ |

### Step 3: ストレージバックエンド設計

各マイクロサービスに適したストレージを選定：

```markdown
## ストレージ選定

### サービス別ストレージマッピング
| サービス | 主ストレージ | 選定理由 | ScalarDB設定 |
|---------|------------|---------|--------------|
| Order Service | PostgreSQL | トランザクション重視 | JDBC |
| Inventory Service | DynamoDB | スケーラビリティ | DynamoDB Native |
| Analytics Service | Cassandra | 書き込み性能 | Cassandra Native |

### マルチストレージ構成
```mermaid
graph TB
    subgraph ScalarDB Cluster
        Coordinator[Transaction Coordinator]
    end

    subgraph Services
        OrderSvc[Order Service]
        InvSvc[Inventory Service]
        PaySvc[Payment Service]
    end

    subgraph Storage
        PG[(PostgreSQL)]
        DDB[(DynamoDB)]
        Cassandra[(Cassandra)]
    end

    OrderSvc --> Coordinator
    InvSvc --> Coordinator
    PaySvc --> Coordinator

    Coordinator --> PG
    Coordinator --> DDB
    Coordinator --> Cassandra
```
```

### Step 4: スキーマ設計

ScalarDBのスキーマ設計原則に従ってテーブルを設計：

```markdown
## スキーマ設計

### 命名規則
- Namespace: [service_name]
- Table: [entity_name]
- パーティションキー: ビジネスID（例：order_id, customer_id）
- クラスタリングキー: 時系列やバージョン

### テーブル定義

#### [Namespace].[Table]

| カラム名 | データ型 | キー種別 | 説明 |
|---------|---------|---------|------|
| id | TEXT | PARTITION | 主キー |
| created_at | TIMESTAMP | CLUSTERING | 作成日時 |
| status | TEXT | - | ステータス |
| data | TEXT | - | JSONデータ |

**スキーマJSON:**
```json
{
  "namespace": "order_service",
  "table": "orders",
  "partition_key": ["order_id"],
  "clustering_key": ["created_at"],
  "columns": {
    "order_id": "TEXT",
    "created_at": "TIMESTAMP",
    "customer_id": "TEXT",
    "status": "TEXT",
    "total_amount": "BIGINT"
  },
  "secondary_index": ["customer_id"]
}
```
```

### Step 5: トランザクション設計

#### 単一ストレージトランザクション（Consensus Commit）

```java
// 設定
scalar.db.transaction_manager=consensus-commit
scalar.db.storage=jdbc
scalar.db.contact_points=jdbc:postgresql://localhost:5432/mydb

// 使用パターン
DistributedTransactionManager manager = ...;
DistributedTransaction tx = manager.start();
try {
    // Get
    Optional<Result> result = tx.get(Get.newBuilder()
        .namespace("order_service")
        .table("orders")
        .partitionKey(Key.ofText("order_id", orderId))
        .build());

    // Put
    tx.put(Put.newBuilder()
        .namespace("order_service")
        .table("orders")
        .partitionKey(Key.ofText("order_id", orderId))
        .textValue("status", "CONFIRMED")
        .build());

    tx.commit();
} catch (Exception e) {
    tx.rollback();
    throw e;
}
```

#### マルチストレージトランザクション（Two-Phase Commit）

```java
// 設定
scalar.db.transaction_manager=consensus-commit
scalar.db.multi_storage.storages=postgres,dynamodb

// PostgreSQL設定
scalar.db.multi_storage.storages.postgres.storage=jdbc
scalar.db.multi_storage.storages.postgres.contact_points=jdbc:postgresql://...

// DynamoDB設定
scalar.db.multi_storage.storages.dynamodb.storage=dynamo
scalar.db.multi_storage.storages.dynamodb.contact_points=dynamodb.ap-northeast-1.amazonaws.com

// Namespace-Storage マッピング
scalar.db.multi_storage.namespace_mapping=order_service:postgres,inventory_service:dynamodb
```

#### Sagaパターン（長時間トランザクション）

```markdown
## Sagaオーケストレーション

### 注文作成Saga
1. Order Service: 注文を作成（PENDING）
2. Inventory Service: 在庫を予約
3. Payment Service: 決済を実行
4. Order Service: 注文を確定（CONFIRMED）

### 補償トランザクション
| ステップ | 正常処理 | 補償処理 |
|---------|---------|---------|
| 在庫予約 | reserveInventory() | releaseInventory() |
| 決済実行 | processPayment() | refundPayment() |
| 注文確定 | confirmOrder() | cancelOrder() |
```

```mermaid
sequenceDiagram
    participant Client
    participant OrderSvc as Order Service
    participant InvSvc as Inventory Service
    participant PaySvc as Payment Service
    participant ScalarDB as ScalarDB Cluster

    Client->>OrderSvc: 注文作成
    OrderSvc->>ScalarDB: Begin 2PC
    ScalarDB->>OrderSvc: TX Started

    OrderSvc->>ScalarDB: Insert Order (PENDING)
    OrderSvc->>InvSvc: Reserve Inventory
    InvSvc->>ScalarDB: Update Inventory

    OrderSvc->>PaySvc: Process Payment
    PaySvc->>ScalarDB: Insert Payment

    OrderSvc->>ScalarDB: Prepare
    ScalarDB-->>OrderSvc: Prepared

    OrderSvc->>ScalarDB: Commit
    ScalarDB-->>OrderSvc: Committed

    OrderSvc->>Client: 注文完了
```

### Step 6: 例外処理設計

ScalarDBの例外カテゴリに基づく処理戦略：

| 例外タイプ | 例外クラス | 対応戦略 |
|----------|----------|---------|
| **Transient** | CrudConflictException | リトライ（指数バックオフ） |
| **Transient** | CommitConflictException | リトライ（指数バックオフ） |
| **Non-Transient** | CrudException | 根本原因調査、エラー返却 |
| **Unknown** | UnknownTransactionStatusException | 冪等性チェック後リトライ |

```java
// リトライパターン
int maxRetries = 3;
for (int i = 0; i < maxRetries; i++) {
    try {
        executeTransaction();
        break;
    } catch (CrudConflictException | CommitConflictException e) {
        if (i == maxRetries - 1) throw e;
        Thread.sleep((long) Math.pow(2, i) * 100);
    } catch (UnknownTransactionStatusException e) {
        // 冪等性キーでコミット状態を確認
        if (isAlreadyCommitted(idempotencyKey)) {
            return getExistingResult(idempotencyKey);
        }
        throw e;
    }
}
```

### Step 7: パフォーマンス最適化

#### Group Commit（書き込み最適化）

```properties
# 有効化
scalar.db.consensus_commit.coordinator.group_commit.enabled=true

# スロットサイズ（並列書き込み数）
scalar.db.consensus_commit.coordinator.group_commit.slot_capacity=20

# 遅延時間（ミリ秒）
scalar.db.consensus_commit.coordinator.group_commit.group_size_fix_timeout_millis=20
```

#### Implicit Pre-Read

```java
// 存在チェックを自動化
Put put = Put.newBuilder()
    .namespace("order_service")
    .table("orders")
    .partitionKey(Key.ofText("order_id", orderId))
    .textValue("status", "CONFIRMED")
    .enableImplicitPreRead()  // 自動で存在チェック
    .build();
```

### Step 8: マイグレーション計画

```markdown
## マイグレーション計画

### Phase 1: 準備
- ScalarDB Cluster環境構築
- Coordinatorテーブル作成
- スキーマ定義とテーブル作成

### Phase 2: Shadow Migration
- 既存DBとScalarDB双方に書き込み
- データ整合性検証
- パフォーマンス計測

### Phase 3: 段階的切り替え
| サービス | 切り替え順 | 前提条件 | ロールバック計画 |
|---------|----------|---------|----------------|
| Master Data | 1 | - | 旧DB復元 |
| Order Service | 2 | Master完了 | フラグ切り替え |
| Payment Service | 3 | Order完了 | フラグ切り替え |

### Phase 4: 完全移行
- 旧DB参照の削除
- モニタリング強化
- ドキュメント更新
```

## 出力フォーマット

### scalardb_architecture.md

ScalarDBアーキテクチャ設計：
- デプロイモード
- ストレージ構成
- ネットワーク設計
- セキュリティ設計

### scalardb_schema.md

スキーマ設計：
- Namespace一覧
- テーブル定義
- インデックス設計
- パーティション戦略

### scalardb_transaction.md

トランザクション設計：
- トランザクションパターン
- Saga設計
- 例外処理戦略
- 冪等性設計

### scalardb_migration.md

マイグレーション計画：
- フェーズ別計画
- データ移行手順
- 検証計画
- ロールバック手順

## ツール活用ガイドライン

### 設計図作成

- Mermaid記法を使用
- アーキテクチャ図、シーケンス図を作成
- ER図でスキーマを可視化

### コード確認

```bash
# 既存のデータアクセスパターンを確認
mcp__serena__find_symbol で Repository/DAO クラスを検索
mcp__serena__find_referencing_symbols でトランザクション境界を確認
```

### 設定ファイルテンプレート

```properties
# scalardb.properties テンプレート
scalar.db.storage=multi-storage
scalar.db.transaction_manager=consensus-commit

# Coordinator設定
scalar.db.consensus_commit.coordinator.namespace=coordinator
scalar.db.consensus_commit.coordinator.group_commit.enabled=true

# マルチストレージ設定
scalar.db.multi_storage.storages=postgres,dynamodb,cassandra
scalar.db.multi_storage.namespace_mapping=...
```

## アンチパターン

### 避けるべき設計

| アンチパターン | 問題 | 推奨 |
|--------------|-----|-----|
| クロスパーティションスキャン多用 | パフォーマンス低下 | セカンダリインデックス活用 |
| 大きなトランザクション | ロック競合 | トランザクション分割 |
| Group Commit + カスタムTX ID | 未サポート | 自動生成ID使用 |
| 非JDBC DBでSERIALIZABLE前提 | SNAPSHOTになる可能性 | 整合性レベル確認 |

## 参考資料

- [ScalarDB Documentation](https://scalardb.scalar-labs.com/docs/)
- [ScalarDB GitHub](https://github.com/scalar-labs/scalardb)
- [ScalarDB Samples](https://github.com/scalar-labs/scalardb-samples)
