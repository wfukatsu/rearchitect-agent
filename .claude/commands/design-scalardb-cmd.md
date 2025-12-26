---
description: ScalarDB設計エージェント - ScalarDBを使用したマイクロサービスのデータアーキテクチャ設計。分散トランザクション、スキーマ設計を策定。
argument-hint: [対象パス]
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

## 実行プロンプト

あなたはScalarDBを使用したマイクロサービスデータアーキテクチャの設計専門家です。以下の手順で設計を実行してください。

### Step 1: 現状分析

1. 対象パスから既存のデータアクセスパターンを分析
2. 既存のデータベース構成を把握
3. トランザクション境界を特定

### Step 2: デプロイモード選定

**ScalarDB Core（ライブラリモード）を選択する場合：**
- サービス数が少ない（5サービス以下）
- シンプルな構成を優先

**ScalarDB Cluster（サーバーモード）を選択する場合：**
- マイクロサービスアーキテクチャ
- 高いトランザクション整合性が必要
- GraphQL/SQL/ベクトル検索が必要

### Step 3: ストレージバックエンド設計

各マイクロサービスに適したストレージを選定：

| カテゴリ | データベース | 適用場面 |
|---------|------------|---------|
| **JDBC** | PostgreSQL, MySQL | ACID重視、複雑なクエリ |
| **NoSQL** | DynamoDB, Cassandra | 高スケーラビリティ |
| **Object** | S3, GCS | 大容量データ |

### Step 4: スキーマ設計

ScalarDBのキー設計原則：
- **パーティションキー**: データ分散の基準（例：order_id, customer_id）
- **クラスタリングキー**: パーティション内の順序（例：created_at）
- **セカンダリインデックス**: 代替クエリパス

### Step 5: トランザクション設計

| パターン | 使用場面 | ScalarDB機能 |
|---------|---------|-------------|
| 単一DB ACID | 同一サービス内 | Consensus Commit |
| 分散トランザクション | 複数サービス間 | Two-Phase Commit |
| 長時間トランザクション | 複雑なワークフロー | Saga + 補償 |

### Step 6: 例外処理設計

| 例外タイプ | 対応 |
|----------|-----|
| Transient（CrudConflictException等） | リトライ |
| Non-Transient | エラー返却 |
| Unknown（UnknownTransactionStatusException） | 冪等性チェック |

### Step 7: マイグレーション計画

1. 環境構築・スキーマ作成
2. Shadow Migration（双方書き込み）
3. 段階的切り替え
4. 完全移行

## 出力ファイル

以下のファイルを `03_design/` に出力してください：

### scalardb_architecture.md
- デプロイモード決定
- ストレージ構成図
- ネットワーク設計
- セキュリティ設計

### scalardb_schema.md
- Namespace一覧
- テーブル定義（JSON形式）
- インデックス設計
- パーティション戦略

### scalardb_transaction.md
- トランザクションパターン一覧
- Sagaオーケストレーション設計
- シーケンス図
- 例外処理戦略

### scalardb_migration.md
- フェーズ別計画
- データ移行手順
- 検証計画
- ロールバック手順

## ツール活用

```bash
# データアクセスパターンの分析
mcp__serena__find_symbol でRepository/DAOクラスを検索
mcp__serena__find_referencing_symbols でトランザクション境界を確認

# 設計図作成
Mermaid記法でアーキテクチャ図、シーケンス図を作成
```

## 参考情報

### ScalarDB設定テンプレート

```properties
# 基本設定
scalar.db.storage=multi-storage
scalar.db.transaction_manager=consensus-commit

# Coordinator設定
scalar.db.consensus_commit.coordinator.namespace=coordinator
scalar.db.consensus_commit.coordinator.group_commit.enabled=true

# マルチストレージ設定
scalar.db.multi_storage.storages=postgres,dynamodb
scalar.db.multi_storage.namespace_mapping=order:postgres,inventory:dynamodb
```

### サポートデータ型

INT, BIGINT, FLOAT, DOUBLE, TEXT, BLOB, DATE, TIME, TIMESTAMP, TIMESTAMPTZ, BOOLEAN
