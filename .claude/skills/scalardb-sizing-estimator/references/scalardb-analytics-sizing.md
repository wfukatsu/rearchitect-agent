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

## 10. ScalarDB Analytics ライセンス費用

### 10.1 課金モデル概要

ScalarDB Analytics には2つの課金モデルがあります。

| 課金モデル | 課金単位 | 単価 | 特徴 |
|-----------|---------|------|------|
| **直接契約（SDBU）** | SDBU | 33.5円/SDBU/時間 | 最小6 SDBU、長期利用向け |
| **AWS Marketplace Pay-as-you-go** | メータリング単位 | $0.0000232/unit | AWS請求一本化、従量課金 |

### 10.2 直接契約（SDBU課金）

#### SDBU概要

| 項目 | 値 |
|------|-----|
| **課金単位** | SDBU (ScalarDB Unit) |
| **単価** | 33.5円/SDBU/時間 |
| **最小構成** | 6 SDBU |
| **最小月額費用** | 約14.7万円/月（6 SDBU × 730時間 × 33.5円） |

#### SDBU ⇔ VM構成 対応表

| VMサイズ | vCPU | メモリ | SDBU数 |
|---------|------|--------|--------|
| XS | 2 | 8GB | 0.4 |
| S | 4 | 16GB | 0.75 |
| M | 8 | 32GB | 1.5 |
| L | 16 | 64GB | 3.0 |
| XL | 32 | 128GB | 6.0 |
| 2XL | 64 | 256GB | 12.0 |

**AWSインスタンスタイプとの対応:**

| VMサイズ | AWS (r5系) | SDBU |
|---------|-----------|------|
| XS | r5.large | 0.4 |
| S | r5.xlarge | 0.75 |
| M | r5.2xlarge | 1.5 |
| L | r5.4xlarge | 3.0 |
| XL | r5.8xlarge | 6.0 |
| 2XL | r5.16xlarge | 12.0 |

#### 最小構成パターン（6 SDBU）

最小構成の 6 SDBU を実現する組み合わせ例：

| パターン | ノード構成 | 総vCPU | 総メモリ | 特徴 |
|---------|-----------|--------|---------|------|
| A | XL × 1台 | 32 | 128GB | シンプル構成 |
| B | L × 2台 | 32 | 128GB | 冗長性あり |
| C | M × 4台 | 32 | 128GB | 高並列処理向け |
| D | S × 8台 | 32 | 128GB | 細粒度スケーリング |

#### 価格シミュレーション（直接契約）

**規模別月額費用**

| 規模 | SDBU構成 | 月間稼働時間 | 月額SDBU費用 |
|------|---------|------------|-------------|
| 最小 | 6 SDBU | 730時間（常時） | 約14.7万円 |
| 小規模 | 12 SDBU (XL×2) | 730時間 | 約29.4万円 |
| 中規模 | 24 SDBU (XL×4) | 730時間 | 約58.7万円 |
| 大規模 | 48 SDBU (XL×8) | 730時間 | 約117.4万円 |

**運用パターン別費用**

**パターン1: 24/7常時稼働（本番環境）**

| 構成 | SDBU | 計算式 | 月額 |
|------|------|--------|------|
| XL × 2台 | 12 | 12 × 730 × 33.5円 | 約29.4万円 |
| XL × 4台 | 24 | 24 × 730 × 33.5円 | 約58.7万円 |

**パターン2: 業務時間のみ稼働（10時間/日 × 20日/月 = 200時間）**

| 構成 | SDBU | 計算式 | 月額 |
|------|------|--------|------|
| XL × 2台 | 12 | 12 × 200 × 33.5円 | 約8.0万円 |
| XL × 4台 | 24 | 24 × 200 × 33.5円 | 約16.1万円 |

**パターン3: バッチ処理のみ（4時間/日 × 20日/月 = 80時間）**

| 構成 | SDBU | 計算式 | 月額 |
|------|------|--------|------|
| L × 4台 | 12 | 12 × 80 × 33.5円 | 約3.2万円 |
| XL × 2台 | 12 | 12 × 80 × 33.5円 | 約3.2万円 |

#### 見積もり計算式（直接契約）

```
月額SDBU費用 = SDBU数 × 月間稼働時間 × 33.5円

年間SDBU費用 = 月額SDBU費用 × 12

総コスト = SDBU費用 + EMR/Databricks費用 + Analytics Server費用 + Metadata DB費用
```

**計算例:**
```
中規模本番環境（24 SDBU、24/7稼働）の場合:
  SDBU費用 = 24 × 730 × 33.5 = 586,860円/月
            ≒ 約58.7万円/月
            ≒ 約704万円/年
```

#### 顧客ヒアリング項目

SDBU費用見積もりのための確認事項：

| カテゴリ | ヒアリング項目 | 影響 |
|---------|--------------|------|
| **データ規模** | 分析対象データ量（GB/TB） | ノードサイズ・数に影響 |
| **同時ユーザー** | 同時分析実行ユーザー数 | 必要SDBU数に影響 |
| **クエリ特性** | 典型的なクエリの複雑さ | メモリ要件に影響 |
| **稼働パターン** | 24/7 or 業務時間のみ | 稼働時間に影響 |
| **SLA要件** | 可用性要件（99.9%等） | 冗長構成に影響 |
| **成長予測** | 1-3年のデータ増加予測 | 将来のSDBO拡張に影響 |

#### コスト最適化のポイント（直接契約）

| 最適化項目 | 説明 | 削減効果 |
|-----------|------|---------|
| **稼働時間制御** | 不要時にクラスター停止 | 最大70%削減 |
| **適切なサイジング** | ワークロードに応じたVM選択 | 20-40%削減 |
| **バッチ集約** | 分析処理を特定時間帯に集約 | 50%以上削減 |
| **オートスケーリング** | 負荷に応じた自動調整 | 30%削減 |

### 10.3 AWS Marketplace Pay-as-you-go

AWS環境では、AWS Marketplace経由のPay-as-you-go課金が利用可能です。

#### 製品ラインナップ

| 製品 | 単価 | 課金単位 | 参照 |
|------|------|---------|------|
| **ScalarDB Analytics Server** | $0.0000232/unit | メータリング単位 | [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-53ik57autkmci) |

> **注意**: ScalarDB Analytics ServerはScalarDB Clusterとは別製品です。分析基盤にはScalarDB Analytics Serverが必要です。

#### 関連製品（参考）

ScalarDB Cluster（OLTP用）のAWS Marketplace価格：

| 製品 | 単価 | 課金単位 | 参照 |
|------|------|---------|------|
| ScalarDB Cluster Standard | $1.40/unit/hour | Pod単位 | [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-jx6qxatkxuwm4) |
| ScalarDB Cluster Premium | $2.79/unit/hour | Pod単位 | [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-djqw3zk6dwyk6) |

#### AWS Marketplace利用のメリット・デメリット

| 項目 | メリット | デメリット |
|------|---------|----------|
| **請求** | AWS請求に一本化 | - |
| **契約** | 契約手続き不要、いつでもキャンセル可能 | 返金なし |
| **利用形態** | 短期利用・PoC向け | 長期利用では直接契約より割高の可能性 |
| **サポート** | AWSサポートと統合 | 高度なサポートは要別途契約 |

#### 費用計算例（AWS Marketplace）

ScalarDB Analytics Serverの月額費用計算：

```
月額費用 = メータリング単位 × $0.0000232 × 稼働時間

※ メータリング単位の詳細はScalar社にお問い合わせください
※ 別途EMR/Databricksのインフラ費用が必要
```

#### 問い合わせ先

AWS Marketplace関連の質問：
- **Email**: marketplace-support@scalar-labs.com
- **詳細見積もり**: Scalar社営業担当にお問い合わせください

### 10.4 直接契約 vs AWS Marketplace 比較

| 項目 | 直接契約（SDBU） | AWS Marketplace |
|------|-----------------|-----------------|
| **課金単位** | SDBU（明確なVM対応） | メータリング単位 |
| **最小構成** | 6 SDBU | なし（従量課金） |
| **長期割引** | 交渉可能 | なし |
| **請求** | Scalar社から直接 | AWS請求に統合 |
| **契約期間** | 要契約 | いつでもキャンセル可 |
| **推奨用途** | 本番環境、長期利用 | PoC、短期プロジェクト |

#### 選択ガイドライン

```
直接契約を推奨:
├── 本番環境で長期利用する場合
├── 大規模構成でコスト最適化が必要な場合
├── 詳細なサイジング計画が立てられる場合
└── 専任サポートが必要な場合

AWS Marketplace を推奨:
├── PoC・評価目的の短期利用
├── AWS請求への一本化が必須の場合
├── 契約手続きを簡略化したい場合
└── 利用量が不確定な初期フェーズ
```

---

## 11. 監視

### 11.1 ScalarDB Analytics Server監視項目

| メトリクス | 閾値目安 | アクション |
|-----------|---------|----------|
| CPU使用率 | > 70% | レプリカ追加検討 |
| メモリ使用率 | > 80% | メモリリーク確認 |
| gRPCレイテンシ（P99） | > 500ms | ボトルネック調査 |
| エラー率 | > 1% | ログ調査 |

### 11.2 EMR/Databricks監視項目

| メトリクス | 説明 |
|-----------|------|
| クエリ実行時間 | 長時間クエリの検出 |
| シャッフルスピル | メモリ不足の指標 |
| Task失敗率 | クラスター健全性 |
| Executor使用率 | リソース効率 |

---

## 12. サイジングクイックリファレンス

| 環境 | Analytics Server | EMR Core Nodes | Databricks Workers |
|-----|-----------------|----------------|-------------------|
| 開発 | 1 Pod (0.5 CPU/1GB) | 2 × r5.xlarge | 2 × Standard_DS3_v2 |
| ステージング | 2 Pod (1 CPU/2GB) | 5 × r5.2xlarge | 4 × Standard_E8s_v5 |
| 本番 | 3+ Pod (1 CPU/2GB) | 10+ × r5.4xlarge | 8+ × Standard_E16s_v5 |

---

## 13. 重要な注意点

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
