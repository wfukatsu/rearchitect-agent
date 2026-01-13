# ScalarDB Analytics サイジング詳細リファレンス

## 1. 概要

### 1.1 製品の種類

| バージョン | 説明 | ステータス |
|-----------|------|----------|
| **ScalarDB Analytics with Spark** | Apache Sparkをクエリエンジンとして使用 | **現行版（推奨）** |
| ScalarDB Analytics with PostgreSQL | PostgreSQL FDWを使用 | アーカイブ済（2025年7月） |

**注意**: 本リファレンスでは現行版 **ScalarDB Analytics with Spark** を中心に解説。

### 1.2 主要コンポーネント

| コンポーネント | 説明 | デプロイ先 |
|--------------|------|----------|
| **ScalarDB Analytics Server** | カタログ管理、メタデータ保存、メータリング | Kubernetes |
| **Spark Plugin** | Sparkカタログ実装、データソースコネクタ | EMR/Databricks |
| **ScalarDB Analytics CLI** | カタログ管理用コマンドラインツール | ローカル/コンテナ |
| **Metadata Database** | カタログメタデータ保存用DB | マネージドDB |

### 1.3 ポート

| ポート | 用途 |
|-------|------|
| 11051 | Catalog Server (gRPC) |
| 11052 | Metering Service |

---

## 2. サポートデータソース

### 2.1 ScalarDB管理データベース

| カテゴリ | データベース |
|---------|------------|
| RDBMS | PostgreSQL, MySQL, Oracle, SQL Server, MariaDB |
| クラウドRDBMS | Aurora MySQL/PostgreSQL, AlloyDB |
| NoSQL | DynamoDB, Cosmos DB for NoSQL, Cassandra |

### 2.2 外部データソース（直接接続）

| カテゴリ | データベース | バージョン |
|---------|------------|----------|
| RDBMS | Oracle Database | 23ai, 21c, 19c |
| RDBMS | MySQL | 8.0, 8.4 |
| RDBMS | PostgreSQL | 16, 17, 18 |
| RDBMS | SQL Server | 2017, 2019, 2022 |
| NoSQL | Amazon DynamoDB | - |
| Analytics | Databricks | SQL Warehouses, Compute |
| Analytics | Snowflake | - |

---

## 3. システム要件

### 3.1 ScalarDB Analytics Server

| 項目 | 要件 |
|-----|------|
| **Java** | Oracle JDK / OpenJDK 11, 17, 21 (LTS) |
| **Kubernetes** | 1.31〜1.34（EKS/AKS） |
| **Helm** | 3.5+ |
| **商用ライセンス制限** | 2 vCPU / 4 GiB メモリ |

### 3.2 Spark環境

| 項目 | 要件 |
|-----|------|
| **Apache Spark** | 3.4 または 3.5 |
| **Scala** | 2.12 または 2.13 |
| **Java** | 8, 11, 17, 21 (LTS) |

### 3.3 クラウドサービス対応

| サービス | Spark Driver | Spark Connect | JDBC |
|---------|--------------|---------------|------|
| Amazon EMR (EC2) | ✅ | ✅ | ❌ |
| Databricks | ✅ | ❌ | ✅ |

---

## 4. ScalarDB Analytics Server サイジング

### 4.1 環境別推奨構成

| 環境 | レプリカ数 | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----|-----------|-------------|----------------|-----------|--------------|
| 開発 | 1 | 500m | 1Gi | 1000m | 2Gi |
| ステージング | 2 | 1000m | 2Gi | 2000m | 4Gi |
| 本番 | 3+ | 1000m | 2Gi | 2000m | 4Gi |

### 4.2 Metadata Databaseサイジング

| 規模 | カタログ数 | データソース数 | 推奨DBサイズ |
|-----|----------|--------------|-------------|
| 小規模 | 1-5 | 〜10 | db.t3.small相当 |
| 中規模 | 5-20 | 〜50 | db.t3.medium相当 |
| 大規模 | 20+ | 100+ | db.r6g.large相当 |

---

## 5. Amazon EMR サイジング

### 5.1 EMRクラスター構成

| ノードタイプ | 役割 | 推奨インスタンス |
|------------|------|----------------|
| Primary | クラスター管理 | m5.xlarge |
| Core | データ処理・HDFS | r5.xlarge〜r5.4xlarge |
| Task | 追加処理能力 | r5.xlarge〜r5.4xlarge |

### 5.2 ワークロード別推奨インスタンス

| ワークロード | 推奨インスタンス | vCPU | メモリ |
|------------|----------------|------|-------|
| 軽量分析 | r5.xlarge | 4 | 32 GiB |
| 標準分析 | r5.2xlarge | 8 | 64 GiB |
| 大規模分析 | r5.4xlarge | 16 | 128 GiB |
| メモリ集約型 | r5.8xlarge | 32 | 256 GiB |

### 5.3 EMRクラスターサイズ目安

| データ量 | 同時クエリ数 | Core Node数 | インスタンスタイプ |
|---------|------------|-------------|------------------|
| 〜100 GB | 1-5 | 2-3 | r5.xlarge |
| 〜1 TB | 5-10 | 5-10 | r5.2xlarge |
| 〜10 TB | 10-20 | 10-20 | r5.4xlarge |
| 10 TB+ | 20+ | 20+ | r5.8xlarge |

### 5.4 EMR Spark設定

```json
{
  "Classification": "spark-defaults",
  "Properties": {
    "spark.jars.packages": "com.scalar-labs:scalardb-analytics-spark-all-3.5_2.13:<VERSION>",
    "spark.sql.catalog.<CATALOG_NAME>": "com.scalar.db.analytics.spark.ScalarDbAnalyticsCatalog",
    "spark.sql.catalog.<CATALOG_NAME>.catalogServerHost": "<CATALOG_SERVER_HOST>",
    "spark.sql.catalog.<CATALOG_NAME>.catalogPort": "11051",
    "spark.sql.catalog.<CATALOG_NAME>.meteringPort": "11052"
  }
}
```

### 5.5 Spark Connect設定

Spark Connectを使用する場合、Primary Nodeでポート15001を開放：
```
Remote URL: sc://<PRIMARY_NODE_PUBLIC_HOSTNAME>:15001
```

---

## 6. Databricks サイジング

### 6.1 クラスター設定要件

| 項目 | 設定 |
|-----|------|
| Access Mode | **No isolation shared**（必須） |
| Runtime | Spark 3.4以上をサポートするバージョン |
| Cluster Type | All-purpose または Jobs compute |

### 6.2 ワークロード別推奨構成（Azure）

| ワークロード | Worker Type | Workers | Driver |
|------------|-------------|---------|--------|
| 軽量分析 | Standard_DS3_v2 | 2-4 | Standard_DS3_v2 |
| 標準分析 | Standard_E8s_v5 | 4-8 | Standard_E8s_v5 |
| 大規模分析 | Standard_E16s_v5 | 8-16 | Standard_E16s_v5 |
| メモリ集約型 | Standard_E32s_v5 | 16+ | Standard_E16s_v5 |

### 6.3 ワークロード別推奨構成（AWS）

| ワークロード | Worker Type | vCPU | メモリ |
|------------|-------------|------|-------|
| 軽量分析 | r5.xlarge | 4 | 32 GiB |
| 標準分析 | r5.2xlarge | 8 | 64 GiB |
| メモリ集約型 | r5.4xlarge | 16 | 128 GiB |

### 6.4 Databricks Spark設定

```
spark.jars.packages com.scalar-labs:scalardb-analytics-spark-all-3.5_2.13:<VERSION>
spark.sql.catalog.<CATALOG_NAME> com.scalar.db.analytics.spark.ScalarDbAnalyticsCatalog
spark.sql.catalog.<CATALOG_NAME>.catalogServerHost <CATALOG_SERVER_HOST>
spark.sql.catalog.<CATALOG_NAME>.catalogPort 11051
spark.sql.catalog.<CATALOG_NAME>.meteringPort 11052
```

---

## 7. パフォーマンスチューニング

### 7.1 Spark設定推奨

| パラメータ | 推奨値 | 説明 |
|-----------|-------|------|
| `spark.sql.adaptive.enabled` | true | Adaptive Query Execution有効化 |
| `spark.sql.adaptive.coalescePartitions.enabled` | true | パーティション自動調整 |
| `spark.sql.adaptive.skewJoin.enabled` | true | Skew Join最適化 |
| `spark.executor.memory` | 18g | Executorメモリ |
| `spark.executor.cores` | 4 | Executorコア数 |

### 7.2 メモリ設定目安

```
Executorメモリ ≈ (ノードメモリ - OSオーバーヘッド) / Executor数

例: r5.2xlarge (64 GiB) で 3 Executor の場合
    (64 - 4) / 3 ≈ 20 GiB/Executor
```

### 7.3 パーティション数の目安

```
推奨パーティション数 = 総コア数 × 2〜3

例: 5ノード × 8コア = 40コア
    → 80〜120 パーティション
```

### 7.4 ボトルネック対策

| 問題 | 対策 |
|-----|------|
| メモリ不足 | Executorメモリ増加、ノードサイズ拡大 |
| シャッフル遅延 | パーティション数調整、メモリ最適化インスタンス |
| データスキュー | Adaptive Query Execution有効化 |
| ネットワーク遅延 | 同一リージョン/AZ配置 |

---

## 8. 構成例

### 8.1 開発環境

```yaml
# ScalarDB Analytics Server
server:
  replicas: 1
  resources:
    requests: {cpu: 500m, memory: 1Gi}
    limits: {cpu: 1000m, memory: 2Gi}

# Metadata Database
metadataDb:
  type: PostgreSQL
  instance: db.t3.micro

# EMR Cluster
emr:
  primaryNode: {instanceType: m5.xlarge, count: 1}
  coreNodes: {instanceType: r5.xlarge, count: 2}
```

### 8.2 ステージング環境

```yaml
# ScalarDB Analytics Server
server:
  replicas: 2
  resources:
    requests: {cpu: 1000m, memory: 2Gi}
    limits: {cpu: 2000m, memory: 4Gi}

# Metadata Database
metadataDb:
  type: PostgreSQL
  instance: db.t3.small

# EMR Cluster
emr:
  primaryNode: {instanceType: m5.xlarge, count: 1}
  coreNodes: {instanceType: r5.2xlarge, count: 5}
```

### 8.3 本番環境

```yaml
# ScalarDB Analytics Server
server:
  replicas: 3
  resources:
    requests: {cpu: 1000m, memory: 2Gi}
    limits: {cpu: 2000m, memory: 4Gi}
  podAntiAffinity: required
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule

# Metadata Database
metadataDb:
  type: PostgreSQL
  instance: db.r6g.large
  multiAz: true

# EMR Cluster
emr:
  primaryNode: {instanceType: m5.xlarge, count: 1}
  coreNodes: {instanceType: r5.4xlarge, count: 10}
  taskNodes: {instanceType: r5.2xlarge, count: 0-20}  # オートスケーリング
```

### 8.4 Databricks本番環境

```yaml
# ScalarDB Analytics Server
server:
  replicas: 3
  resources:
    requests: {cpu: 1000m, memory: 2Gi}
    limits: {cpu: 2000m, memory: 4Gi}

# Metadata Database
metadataDb:
  type: PostgreSQL
  instance: db.r6g.large

# Databricks Cluster
databricks:
  clusterMode: "No isolation shared"
  runtime: "14.3 LTS"  # Spark 3.5対応
  driver: {instanceType: Standard_E8s_v5}
  workers:
    instanceType: Standard_E16s_v5
    minWorkers: 4
    maxWorkers: 20
  autoscale: true
```

---

## 9. コスト最適化

### 9.1 EMRコスト削減オプション

| オプション | 削減率 | 適用対象 |
|-----------|-------|---------|
| Spot Instances（Task Node） | 〜70% | バッチ分析 |
| Reserved Instances | 〜40% | 常時稼働クラスター |
| EMR Serverless | 可変 | 断続的なワークロード |

### 9.2 Databricksコスト削減

| オプション | 説明 |
|-----------|------|
| Auto-termination | アイドル時の自動停止 |
| Autoscaling | ワークロードに応じたスケール |
| Spot Instances | Worker Nodeへの適用 |
| Serverless | 使用量ベースの課金 |

### 9.3 推奨アプローチ

| ワークロードタイプ | 推奨構成 |
|------------------|---------|
| アドホック分析 | オートスケーリング + Spot |
| 定期バッチ | Job Cluster + Spot |
| インタラクティブ | All-purpose + Reserved |
| 24/7運用 | Reserved + 固定クラスター |

---

## 10. 監視

### 10.1 ScalarDB Analytics Server監視項目

| メトリクス | 閾値目安 | アクション |
|-----------|---------|----------|
| CPU使用率 | > 70% | レプリカ追加検討 |
| メモリ使用率 | > 80% | メモリリーク確認 |
| gRPCレイテンシ（P99） | > 500ms | ボトルネック調査 |
| エラー率 | > 1% | ログ調査 |

### 10.2 EMR/Databricks監視項目

| メトリクス | 説明 |
|-----------|------|
| クエリ実行時間 | 長時間クエリの検出 |
| シャッフルスピル | メモリ不足の指標 |
| Task失敗率 | クラスター健全性 |
| Executor使用率 | リソース効率 |

---

## 11. サイジングクイックリファレンス

| 環境 | Analytics Server | EMR Core Nodes | Databricks Workers |
|-----|-----------------|----------------|-------------------|
| 開発 | 1 Pod (0.5 CPU/1GB) | 2 × r5.xlarge | 2 × Standard_DS3_v2 |
| ステージング | 2 Pod (1 CPU/2GB) | 5 × r5.2xlarge | 4 × Standard_E8s_v5 |
| 本番 | 3+ Pod (1 CPU/2GB) | 10+ × r5.4xlarge | 8+ × Standard_E16s_v5 |

---

## 12. 重要な注意点

1. **Sparkバージョン**: 3.4または3.5が必須
2. **Scalaバージョン**: 2.12または2.13（Sparkと一致させる）
3. **Databricks Access Mode**: "No isolation shared"が必須
4. **商用ライセンス**: 2vCPU/4GBの制限あり
5. **Read Only**: ScalarDB AnalyticsはRead専用（書き込み不可）

---

## 参照リンク

- [ScalarDB Analytics Design](https://scalardb.scalar-labs.com/docs/latest/scalardb-analytics/design/)
- [Deploy ScalarDB Analytics](https://scalardb.scalar-labs.com/docs/latest/scalardb-analytics/deployment/)
- [Create ScalarDB Analytics Catalog](https://scalardb.scalar-labs.com/docs/latest/scalardb-analytics/create-scalardb-analytics-catalog/)
- [Amazon EMR Best Practices](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-instances-guidelines.html)
- [Databricks Cluster Configuration](https://docs.databricks.com/aws/en/compute/cluster-config-best-practices)
