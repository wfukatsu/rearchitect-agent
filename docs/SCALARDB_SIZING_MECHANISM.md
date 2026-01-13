# ScalarDB サイジング見積もりの仕組み

本ドキュメントでは、`/scalardb-sizing-estimator` スキルによるScalarDB Clusterのサイジング見積もりの仕組みを説明します。

## 1. 概要

### 1.1 目的

ScalarDBサイジング見積もりは、以下を算出するためのツールです：

- **ScalarDB Cluster Pod数** - 性能要件と可用性要件を満たすPod数
- **Kubernetes構成** - ノード数、インスタンスタイプ
- **バックエンドDB構成** - Aurora/DynamoDB/CosmosDB等のサイジング
- **インフラコスト** - 月額・年額のクラウド費用
- **ライセンスコスト** - ScalarDBライセンス費用

### 1.2 対象バージョン

- ScalarDB v3.17以上（最適化設定対応）
- ScalarDB Analytics（オプション）

---

## 2. 見積もりフロー

```
┌─────────────────────────────────────────────────────────────┐
│                    要件ヒアリング                            │
│  ・性能要件（TPS）                                           │
│  ・可用性要件（SLA）                                         │
│  ・データ量                                                  │
│  ・環境構成                                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    サイジング計算                            │
│  ・Pod数計算（性能/可用性）                                  │
│  ・ストレージオーバーヘッド計算                              │
│  ・I/Oオーバーヘッド計算                                     │
│  ・Kubernetes Node計算                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    コスト計算                                │
│  ・インフラコスト（AWS/Azure/GCP）                           │
│  ・ScalarDBライセンスコスト                                  │
│  ・環境別コストサマリー                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    出力生成                                  │
│  ・Markdown形式レポート                                      │
│  ・HTML形式レポート（オプション）                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Pod数計算の仕組み

### 3.1 基本計算式

Pod数は以下の3つの要素の最大値で決定されます：

```
最終Pod数 = max(性能要件Pod数, 可用性要件Pod数, 最小Pod数)
```

#### 3.1.1 性能要件Pod数

```
性能Pod数 = ceil(目標TPS / TPS_per_Pod)
```

**TPS/Pod のベンチマーク値:**

| ワークロードタイプ | 最適化なし | v3.17最適化有効 |
|-------------------|-----------|----------------|
| 読み取り中心 | 1,500 TPS | 2,400 TPS |
| バランス型 | 600 TPS | 1,000 TPS |
| 書き込み中心 | 400 TPS | 900 TPS |

#### 3.1.2 可用性要件Pod数

```
可用性Pod数 = 許容障害Pod数 + ceil(必要TPS / (障害時維持率 × TPS_per_Pod))
```

**SLAとPod数の対応:**

| 目標SLA | 許容ダウンタイム/年 | 推奨Pod数 | 許容障害Pod数 |
|---------|-------------------|-----------|--------------|
| 99.0% | 87.6時間 | 2 pods | 0 |
| 99.9% | 8.76時間 | 3 pods | 1 |
| 99.95% | 4.38時間 | 5 pods | 2 |
| 99.99% | 52.6分 | 7+ pods | 3+ |

#### 3.1.3 最小Pod数

- **開発環境**: 1 pod（HA不要）
- **テスト環境**: 2 pods（基本HA）
- **ステージング/本番**: 3 pods（Raftクォーラム）

### 3.2 計算例

**シナリオ**: 500 TPS、99.9% SLA、バランス型ワークロード

```
1. 性能要件Pod数:
   ceil(500 / 1,000) = 1 pod

2. 可用性要件Pod数:
   Raftクォーラム最小 = 3 pods
   1 Pod障害時: 2 pods × 1,000 TPS = 2,000 TPS > 500 TPS ✓

3. 最終Pod数:
   max(1, 3, 3) = 3 pods
```

---

## 4. リソース計算

### 4.1 Podリソース制限

ScalarDB Clusterの推奨リソース制限：

| 環境 | CPU/Pod | Memory/Pod |
|------|---------|------------|
| 開発 | 500m | 1Gi |
| テスト | 1 | 2Gi |
| ステージング | 2 | 4Gi |
| 本番 | 2 | 4Gi |

### 4.2 Kubernetesノード計算

```
必要vCPU = ScalarDB_Pods × 2 + Application_Pods × 1 + System_Overhead
必要ノード数 = ceil(必要vCPU / ノードあたりvCPU) × 冗長係数(1.3)
```

**計算例（本番環境）:**

```
ScalarDB: 3 pods × 2 vCPU = 6 vCPU
Application: 6 services × 2 pods × 1 vCPU = 12 vCPU
Kong: 2 pods × 0.5 vCPU = 1 vCPU
Monitoring: 2 vCPU
合計: 21 vCPU

ノード数 = ceil(21 / 4) × 1.3 ≈ 7 nodes
→ 3 AZ分散で 9 nodes (3 × 3)
```

---

## 5. ストレージオーバーヘッド

### 5.1 ScalarDBのストレージ構造

ScalarDBは、トランザクション管理のために追加のメタデータを保存します：

| コンポーネント | サイズ | 説明 |
|--------------|-------|------|
| Afterイメージ | 60 bytes | コミット後の状態 |
| Beforeイメージ | 60 bytes + 非PKカラムデータ | ロールバック用 |
| トランザクションID | 36 bytes | UUID形式 |
| タイムスタンプ | 8 bytes | 作成・更新時刻 |

### 5.2 ストレージ計算式

```
ScalarDBストレージ = 元データ × (1 + オーバーヘッド率)
オーバーヘッド率 ≈ 30%（一般的なケース）
```

**計算例:**

```
元データ: 100 GB
ScalarDBオーバーヘッド: 30%
必要ストレージ: 100 GB × 1.3 = 130 GB
```

### 5.3 Coordinatorテーブル

分散トランザクションの調整に使用：

```
Coordinatorサイズ = アクティブTX数 × (TxID + 状態 + タイムスタンプ)
                  ≈ アクティブTX数 × 100 bytes
```

---

## 6. I/Oオーバーヘッド

### 6.1 トランザクションパターン別I/O

ScalarDBの2相コミットにより、I/O操作が増加します：

| 操作 | 元のI/O | ScalarDB I/O | 倍率 |
|------|--------|-------------|------|
| 単一レコード更新 | 1 | 5 | 5x |
| 複数レコード更新（N件） | N | 2N + 3 | 2-3x |
| 読み取りのみ | 1 | 1-2 | 1-2x |

### 6.2 I/O計算式

```
必要IOPS = TPS × トランザクションあたりI/O数
```

**計算例:**

```
TPS: 500
トランザクションあたりI/O: 5
必要IOPS: 500 × 5 = 2,500 IOPS
```

---

## 7. v3.17最適化設定

### 7.1 クライアント側最適化

```yaml
# Piggyback Begin - トランザクション開始をまとめる
scalar.db.cluster.client.piggyback_begin.enabled: true

# Write Buffering - 書き込みをバッファリング
scalar.db.cluster.client.write_buffering.enabled: true
```

### 7.2 サーバー側最適化

```yaml
# 非同期コミット - コミット応答を高速化
scalar.db.consensus_commit.async_commit.enabled: true

# 1フェーズコミット - 単一DB時に2PC省略
scalar.db.consensus_commit.one_phase_commit.enabled: true
```

### 7.3 期待効果

| 最適化 | 効果 |
|--------|------|
| Piggyback Begin | レイテンシ10-20%削減 |
| Write Buffering | スループット20-30%向上 |
| Async Commit | レイテンシ30-50%削減 |
| One Phase Commit | 単一DB時50%高速化 |
| **総合効果** | **1.5-2倍の性能向上** |

---

## 8. コスト計算

### 8.1 ScalarDBライセンス

#### ライセンス形態

ScalarDBは2つのライセンス形態から選択できます：

**1. 直接契約（年間契約）**

| エディション | 費用/Pod/月 | 主な機能 |
|-------------|------------|---------|
| Standard | ¥100,000 | 基本機能、標準サポート |
| Premium | ¥200,000 | 高度機能、24/7サポート、SLA保証 |

**2. AWS Marketplace Pay-as-you-go（従量課金）**

| エディション | 時間単価 | 月額換算/Pod | 主な機能 |
|-------------|---------|-------------|---------|
| Standard | $1.40/時間 | 約¥153,300 | 基本機能 |
| Premium | $2.80/時間※推定 | 約¥306,600 | 高度機能 |

※ 月額 = 時間単価 × 730時間
※ 参照: [AWS Marketplace ScalarDB](https://aws.amazon.com/marketplace/pp/prodview-jx6qxatkxuwm4)

#### AWS Marketplace Pay-as-you-go の特徴

**単位の定義**
```
1単位 = 1 Pod = 2 vCPU / 4 GB memory
単位数 = max(ceil(vCPU / 2), ceil(memory_GB / 4))
```

**リソース制限**
- 最大vCPU/Pod: 2 vCPU
- 最大メモリ/Pod: 4 GB
- 制限超過時: Podが自動停止

**選択の判断基準**

| ユースケース | 推奨形態 |
|------------|---------|
| 短期PoC（1-3ヶ月） | AWS Marketplace |
| 開発・検証（短期） | AWS Marketplace |
| 本番環境（長期） | 直接契約 |
| AWS請求一本化 | AWS Marketplace |
| コスト最適化重視 | 直接契約 |

**コスト比較（5Pod構成）**

| 形態 | ライセンス/月 | 直接契約比 |
|------|-------------|-----------|
| 直接契約 Standard | ¥500,000 | 基準 |
| AWS Marketplace Standard | ¥766,500 | +53% |

### 8.2 インフラコスト（AWS例）

| コンポーネント | 開発 | テスト | ステージング | 本番 |
|--------------|------|--------|-------------|------|
| EKS Cluster | $73 | $73 | $73 | $73 |
| EC2 Nodes | $150 | $300 | $500 | $900 |
| Aurora PostgreSQL | $50 | $150 | $300 | $500 |
| ALB | $20 | $30 | $50 | $80 |
| **月額計** | **$293** | **$553** | **$923** | **$1,553** |

### 8.3 総コスト計算式

```
月額総コスト = (Pod数 × ライセンス単価) + インフラコスト

年間総コスト = 月額総コスト × 12
```

### 8.4 コスト最適化オプション

| オプション | 削減率 | 適用環境 |
|-----------|--------|---------|
| Reserved Instances (1年) | 30-40% | 本番・ステージング |
| Savings Plans | 20-30% | 全環境 |
| Spot Instances | 60-70% | 開発・テスト |
| 夜間停止 | 50% | 開発 |

---

## 9. 環境別デフォルト構成

### 9.1 開発環境

```yaml
scalardb:
  pods: 2
  cpu_per_pod: 500m
  memory_per_pod: 1Gi
kubernetes:
  nodes: 2
  instance_type: t3.medium
database:
  type: Aurora PostgreSQL
  class: db.t4g.medium
  multi_az: false
```

### 9.2 本番環境

```yaml
scalardb:
  pods: 3
  cpu_per_pod: 2
  memory_per_pod: 4Gi
kubernetes:
  nodes: 9  # 3 AZ × 3
  instance_type: m6i.xlarge
database:
  type: Aurora PostgreSQL
  class: db.r6g.xlarge
  multi_az: true
  read_replicas: 1
```

---

## 10. 使用方法

### 10.1 インタラクティブモード

```bash
/scalardb-sizing-estimator
```

対話形式で以下を入力：
1. 性能要件（TPS）
2. 可用性要件（SLA）
3. 環境構成
4. クラウドプロバイダー
5. ScalarDB Analytics有無

### 10.2 出力例

```markdown
## ScalarDB Cluster サイジング見積もり

### 要件サマリー
| 項目 | 値 |
|------|-----|
| 目標TPS | 500 |
| SLA | 99.9% |
| クラウド | AWS |

### 構成
| コンポーネント | 値 |
|--------------|-----|
| ScalarDB Pods | 3 |
| K8s Nodes | 9 |
| Aurora | db.r6g.xlarge |

### 費用（月額）
| 項目 | 金額 |
|------|------|
| ライセンス | ¥300,000 |
| インフラ | ¥255,450 |
| **合計** | **¥555,450** |
```

---

## 11. 制限事項と注意点

### 11.1 見積もりの前提条件

- AWS東京リージョン（デフォルト）
- ScalarDB v3.17以上
- Kubernetes v1.28以上
- ネットワークレイテンシ < 1ms（同一リージョン）

### 11.2 注意点

- ライセンス費用は参考値（正式見積もりはScalar社へ）
- クラウド費用は変動する可能性あり
- 為替レートは 1 USD = 150 JPY で計算

---

## 12. 関連ドキュメント

- [ScalarDB公式ドキュメント](https://scalardb.scalar-labs.com/docs/)
- [ScalarDB Cluster設定ガイド](https://scalardb.scalar-labs.com/docs/latest/scalardb-cluster/)
- `/design-scalardb` - ScalarDBアーキテクチャ設計スキル
- `/design-scalardb-analytics` - ScalarDB Analytics設計スキル

---

*本ドキュメント作成日: 2026年1月*
