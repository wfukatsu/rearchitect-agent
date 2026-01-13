# ScalarDB Cluster サイジング詳細リファレンス

## 1. Pod リソース制限

| 項目 | 制限値 | 備考 |
|-----|-------|------|
| CPU | 2 vCPU | 商用ライセンス制限 |
| メモリ | 4 GiB | 商用ライセンス制限 |
| gRPCポート | 60053/TCP | クライアント接続用 |
| モニタリングポート | 9080/TCP | Prometheus metrics |

**重要**: AWS Marketplace等のPay-as-you-goコンテナでは、2vCPU/4GBを超える設定でPodが自動停止。

---

## 2. ストレージオーバーヘッド

### 2.1 トランザクションメタデータカラム

**Afterイメージメタデータ（各レコードに追加）**:
| カラム名 | データ型 | サイズ目安 | 説明 |
|---------|---------|----------|------|
| `tx_id` | TEXT | 36バイト（UUID） | トランザクションID |
| `tx_state` | INT | 4バイト | トランザクション状態 |
| `tx_version` | INT | 4バイト | レコードバージョン |
| `tx_prepared_at` | BIGINT | 8バイト | Prepare時刻 |
| `tx_committed_at` | BIGINT | 8バイト | Commit時刻 |

**Afterイメージメタデータ合計: 約60バイト/レコード**

**Beforeイメージメタデータ（更新操作時）**:
| カラム名 | データ型 | サイズ目安 | 説明 |
|---------|---------|----------|------|
| `before_tx_id` | TEXT | 36バイト | 変更前のトランザクションID |
| `before_tx_state` | INT | 4バイト | 変更前の状態 |
| `before_tx_version` | INT | 4バイト | 変更前のバージョン |
| `before_tx_prepared_at` | BIGINT | 8バイト | 変更前のPrepare時刻 |
| `before_tx_committed_at` | BIGINT | 8バイト | 変更前のCommit時刻 |

**Beforeイメージメタデータ合計: 約60バイト/レコード**

### 2.2 ユーザーデータのBeforeイメージ

**重要**: ScalarDBは更新レコードの**全ての非プライマリキーカラム**のBeforeイメージを保持。
```
before_{カラム名} = 元のカラム値のコピー
```

### 2.3 ストレージオーバーヘッド計算式

```
レコードオーバーヘッド = Afterメタデータ + Beforeメタデータ + Beforeユーザーデータ
                      = 60バイト + 60バイト + Σ(非PKカラムサイズ)
                      = 120バイト + 非PKカラムサイズ
```

**オーバーヘッド率の一般式**:
```
オーバーヘッド率 = (120 + 非PKカラムサイズ) / 元のレコードサイズ × 100%
```

### 2.4 オーバーヘッド率の目安

| 元のレコードサイズ | 非PKカラムサイズ | オーバーヘッド率 |
|-----------------|----------------|--------------|
| 100バイト | 50バイト | 〜170% |
| 200バイト | 150バイト | 〜135% |
| 500バイト | 400バイト | 〜104% |
| 1,000バイト | 900バイト | 〜102% |
| 10,000バイト | 9,900バイト | 〜100.2% |

**結論**: レコードサイズが大きいほど、相対的なオーバーヘッド率は低下

### 2.5 計算例

**元のテーブル定義**:
```sql
CREATE TABLE orders (
    order_id    TEXT,        -- PK: 36バイト
    customer_id TEXT,        -- 36バイト
    product_id  TEXT,        -- 36バイト
    quantity    INT,         -- 4バイト
    price       INT,         -- 4バイト
    status      TEXT,        -- 20バイト（平均）
    created_at  BIGINT       -- 8バイト
);
```

**元のレコードサイズ**: 144バイト (PK: 36 + 非PK: 108)

**ScalarDB使用後のレコードサイズ**:
```
元のデータ:          144バイト
Afterメタデータ:      60バイト
Beforeメタデータ:     60バイト
Before非PKカラム:    108バイト
─────────────────────────────
合計:                372バイト
オーバーヘッド率:     158%
```

---

## 3. I/Oオーバーヘッド

### 3.1 読み取り操作のオーバーヘッド

| 操作 | 追加I/O |
|-----|--------|
| 単純読み取り（トランザクション外） | なし |
| トランザクション内読み取り | メタデータ読み取り |

### 3.2 書き込み操作のオーバーヘッド

| フェーズ | I/O操作 |
|---------|--------|
| Prepare | 1. 対象レコード読み取り（Beforeイメージ取得） |
|         | 2. Beforeイメージ + 新データの書き込み |
|         | 3. Coordinatorへの状態書き込み |
| Commit  | 4. Coordinatorの状態更新 |
|         | 5. 各レコードのコミット処理 |

### 3.3 I/Oオーバーヘッド見積もり

**1レコード更新の場合**:
```
通常のRDBMS:     1 write
ScalarDB:        1 read + 2 write + 2 coordinator write
                 = 約5倍のI/O操作
```

**Nレコード更新の場合（1トランザクション）**:
```
通常のRDBMS:     N writes
ScalarDB:        N reads + N writes + 2 coordinator writes
                 = 2N + 2 I/O操作
```

### 3.4 DynamoDB WCU/RCU計算例

```
元の1KB書き込み:    1 WCU
ScalarDB経由:
  - 読み取り(Before): ceil(2KB/4KB) = 1 RCU（強整合性）
  - 書き込み(After+Before): ceil(2KB/1KB) = 2 WCU
  - Coordinator書き込み: 1 WCU
  合計: 1 RCU + 3 WCU
```

---

## 4. Coordinatorテーブル

### 4.1 Coordinatorテーブル構造

| カラム名 | データ型 | サイズ目安 |
|---------|---------|----------|
| `id` | TEXT | 36バイト（トランザクションID） |
| `child_ids` | TEXT | 可変（グループコミット時） |
| `state` | INT | 4バイト |
| `created_at` | BIGINT | 8バイト |

**Coordinatorレコードサイズ: 約50〜100バイト/トランザクション**

### 4.2 Coordinatorテーブルサイズ見積もり

```
Coordinatorサイズ = トランザクション数 × レコードサイズ × 保持期間係数

例: 1,000 TPS × 50バイト × 3600秒 × 24時間 = 約4.3 GB/日
```

**注意**: Coordinatorテーブルは定期的なクリーンアップが必要

---

## 5. 主要パフォーマンス設定

| パラメータ | デフォルト | 説明 |
|-----------|----------|------|
| `parallel_executor_count` | 128 | 並列実行スレッド数 |
| `parallel_preparation.enabled` | true | Prepare並列実行 |
| `parallel_commit.enabled` | true | Commit並列実行 |
| `parallel_validation.enabled` | - | 検証フェーズの並列実行 |

### JDBC接続プール
| パラメータ | デフォルト |
|-----------|----------|
| `min_idle` | 20 |
| `max_idle` | 50 |
| `max_total` | 200 |

### グループコミット（オプション）
| パラメータ | デフォルト |
|-----------|----------|
| `group_commit.enabled` | false |
| `group_commit.slot_capacity` | 20 |
| `group_commit.group_size_fix_timeout_millis` | 40 |

### ScalarDB 3.17 クライアントサイド最適化（推奨）

**v3.17で追加されたRPCオーバーヘッド削減機能。有効化で最大2倍の性能向上。**

| パラメータ | デフォルト | 説明 |
|-----------|----------|------|
| `scalar.db.cluster.client.piggyback_begin.enabled` | **false** | Begin RPCを最初のCRUD操作に同梱 |
| `scalar.db.cluster.client.write_buffering.enabled` | **false** | 非条件書き込みをバッファリング・一括実行 |

#### Piggyback Begin
- トランザクション開始を最初のCRUD操作まで遅延
- Begin RPCを最初の操作に同梱し、専用Begin RPC呼び出しを削除
- **効果**: RPCラウンドトリップを1回削減

```
【従来】           【Piggyback Begin有効】
Client → Cluster   Client → Cluster
  Begin              Begin, Read (同梱)
  Read               Write
  Write              Commit
  Commit
```

#### Write Buffering
- Insert, Upsert, 無条件Update/Deleteをクライアント側でバッファリング
- Read操作またはCommit時にバッファ内容を一括送信
- **効果**: 複数の書き込みを1回のRPCにまとめる

```
【従来】           【Write Buffering有効】
Client → Cluster   Client → Cluster
  Begin              Begin
  Write1             Write1, Write2, Read (一括)
  Write2             Write3, Commit (一括)
  Read
  Write3
  Commit
```

#### 推奨設定（本番環境）
```properties
# クライアント側設定（アプリケーション側）
scalar.db.cluster.client.piggyback_begin.enabled=true
scalar.db.cluster.client.write_buffering.enabled=true

# サーバー側設定（ScalarDB Cluster側）
scalar.db.consensus_commit.async_commit.enabled=true
scalar.db.consensus_commit.one_phase_commit.enabled=true  # 単一DB構成時のみ
```

### ScalarDB 3.17 ベンチマーク結果

**環境構成**:
- ScalarDB Cluster: m5.xlarge × 10 pods (1 pod/node, 4vCPU/16GB)
- RDS PostgreSQL: db.m5.4xlarge
- ワークロード: YCSB-F (read-modify-write per transaction)
- 最適化設定: `async_commit=true`, `one_phase_commit=true`, connection_pool=200/500/500

| モード | 最適化なし | 最適化あり | 改善率 |
|-------|----------|----------|-------|
| Indirect (Envoy経由) | ~4,500 TPS | **~9,000 TPS** | **約2倍** |
| Direct | ~18,000 TPS | **~24,000 TPS** | 約1.3倍 |

**→ 10 pods で 9,000〜24,000 TPS = 900〜2,400 TPS/Pod**

### Transaction Metadata Decoupling（v3.17新機能）

**トランザクションメタデータをアプリケーションデータと別テーブルに分離する機能。**

#### 概要
- 従来：メタデータカラムがアプリケーションテーブルに直接追加
- Decoupling有効時：メタデータ専用テーブル（`<table_name>$metadata`）を使用

#### 設定
```properties
scalar.db.consensus_commit.transaction_metadata_decoupling.enabled=true
```

#### メリット
| 観点 | 効果 |
|------|------|
| **データ分離** | アプリケーションテーブルがクリーンに保たれる |
| **パフォーマンス** | メタデータ更新による競合を削減（特に高負荷時） |
| **管理性** | メタデータとデータの独立したバックアップ/メンテナンスが可能 |

#### 注意点
- スキーマ作成時に有効化が必要（既存テーブルには適用不可）
- メタデータテーブル用の追加ストレージが必要
- 一部の操作で追加のテーブルアクセスが発生

#### ストレージオーバーヘッドへの影響
Decoupling有効時のストレージ構造:
```
アプリケーションテーブル:
  - 元のデータのみ（メタデータなし）

メタデータテーブル (<table_name>$metadata):
  - tx_id, tx_state, tx_version, tx_prepared_at, tx_committed_at
  - before_* カラム群
  = 約120バイト/レコード + Beforeユーザーデータ
```

**→ 総ストレージは変わらないが、テーブル設計がシンプルになる**

---

## 6. TPS/Pod 見積もり

### 6.1 ワークロード別目安

| ワークロード | TPS/Pod（従来） | TPS/Pod（v3.17最適化） | 特徴 |
|------------|----------------|---------------------|------|
| 読み取りヘビー（90%読み取り） | 1,500〜3,000 | 2,000〜4,000 | キャッシュ効果大 |
| バランス型（50%読み取り） | 800〜1,500 | **900〜2,400** | 一般的なOLTP |
| 書き込みヘビー（90%書き込み） | 300〜800 | 500〜1,200 | Coordinator負荷大 |
| 複雑なトランザクション | 200〜500 | 300〜700 | 多レコード操作 |

**※ v3.17最適化**: `piggyback_begin.enabled=true` + `write_buffering.enabled=true` + `async_commit.enabled=true`

### 6.2 性能に影響する要因

| 要因 | 影響度 | 対策 |
|-----|-------|------|
| バックエンドDB性能 | 高 | DBスケールアップ |
| ネットワークレイテンシ | 高 | 同一AZ配置 |
| トランザクションサイズ | 中 | バッチ最適化 |
| 競合率 | 中 | データモデル見直し |
| 分離レベル | 低〜中 | 要件に応じて選択 |

### 6.3 スループット見積もり式

```
実効TPS = min(
    ScalarDB Cluster処理能力,
    バックエンドDB処理能力,
    ネットワーク帯域
)
```

**ScalarDB Cluster側の制限（理論値）**:
```
Pod単位のTPS ≈ parallel_executor_count / 平均トランザクション時間(秒)

例: parallel_executor_count=128, 平均TX時間=10ms
    128 / 0.01 = 12,800 TPS（理論最大値）
```

**現実的な目安**:
- **従来**: 500〜2,000 TPS/Pod（CPU/メモリ制限、GC、競合の影響）
- **v3.17最適化有効時**: **900〜2,400 TPS/Pod**（ベンチマーク実測値）

---

## 7. Pod数計算式

### 7.1 性能要件ベース
```
性能Pod数 = ceil(目標TPS / TPS_per_Pod)
```

### 7.2 可用性要件ベース
```
可用性Pod数 = 許容障害Pod数 + ceil(必要TPS / (障害時維持率 × TPS_per_Pod))
```

### 7.3 最終Pod数
```
最終Pod数 = max(性能Pod数, 可用性Pod数, 最小Pod数)
```

---

## 8. 可用性要件とPod数

### 8.1 可用性レベル別推奨構成

| 可用性レベル | 最小Pod数 | AZ分散 | 備考 |
|------------|---------|--------|------|
| 開発/テスト | 1 | 不要 | 単一障害点あり |
| 低（99.0%） | 2 | 推奨 | 1Pod障害で50%性能低下 |
| 中（99.9%） | 3 | 必須 | 1Pod障害で33%性能低下 |
| 高（99.95%） | 5 | 必須 | 1Pod障害で20%性能低下 |
| 極高（99.99%） | 7+ | 必須 | N+2冗長 |

### 8.2 障害時の動作

```
障害時の処理能力 = 正常Pod数 / 元のPod数 × 元の処理能力

例: 5 Pod構成で1Pod障害
    4/5 × 100% = 80% の処理能力維持
```

---

## 9. 環境別推奨構成

### 9.1 開発環境
```yaml
replicas: 2
resources:
  requests: {cpu: 500m, memory: 1Gi}
  limits: {cpu: 1, memory: 2Gi}
```

### 9.2 テスト環境
```yaml
replicas: 3
resources:
  requests: {cpu: 1, memory: 2Gi}
  limits: {cpu: 2, memory: 4Gi}
```

### 9.3 ステージング環境
```yaml
replicas: 3-5
resources:
  requests: {cpu: 1.5, memory: 3Gi}
  limits: {cpu: 2, memory: 4Gi}
podAntiAffinity: preferred
```

### 9.4 本番環境
```yaml
replicas: 5+
resources:
  requests: {cpu: 2, memory: 4Gi}
  limits: {cpu: 2, memory: 4Gi}
podAntiAffinity: required
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
podDisruptionBudget:
  minAvailable: 3
```

---

## 10. TPS別推奨Pod数・ライセンス費用早見表

### 10.1 ライセンスティア
| ティア | 月額/Pod | 特徴 |
|-------|---------|------|
| **Standard** | ¥100,000 | 基本機能、標準サポート |
| **Premium** | ¥200,000 | 高度な機能、優先サポート |

### 10.2 TPS別構成・費用早見表

| 目標TPS | 可用性 | 推奨Pod数 | Standard/月 | Premium/月 |
|--------|-------|---------|------------|-----------:|
| 〜500 | 99.9% | 3 | ¥300,000 | ¥600,000 |
| 〜1,000 | 99.9% | 3-5 | ¥300,000〜¥500,000 | ¥600,000〜¥1,000,000 |
| 〜2,000 | 99.9% | 5 | ¥500,000 | ¥1,000,000 |
| 〜2,000 | 99.95% | 6 | ¥600,000 | ¥1,200,000 |
| 〜2,000 | 99.99% | 7 | ¥700,000 | ¥1,400,000 |
| 〜5,000 | 99.95% | 7-10 | ¥700,000〜¥1,000,000 | ¥1,400,000〜¥2,000,000 |
| 〜10,000 | 99.95% | 10-15 | ¥1,000,000〜¥1,500,000 | ¥2,000,000〜¥3,000,000 |
| 〜50,000 | 99.99% | 20+ | ¥2,000,000+ | ¥4,000,000+ |

### 10.3 環境別ライセンス費用目安（Standard）

| 環境 | 推奨Pod数 | ライセンス費用/月 |
|-----|----------|-----------------:|
| 開発 | 2 | ¥200,000 |
| テスト | 3 | ¥300,000 |
| ステージング | 3-5 | ¥300,000〜¥500,000 |
| 本番（小規模） | 5 | ¥500,000 |
| 本番（中規模） | 7 | ¥700,000 |
| 本番（大規模） | 10+ | ¥1,000,000+ |

---

## 11. Pod Disruption Budget

| Pod数 | minAvailable | maxUnavailable |
|------|-------------|----------------|
| 3 | 2 | 1 |
| 5 | 3 | 2 |
| 7 | 5 | 2 |
| 10 | 7 | 3 |

---

## 12. Blue/Green・Canary デプロイ考慮

### Blue/Green
- 2系統の完全な環境が必要
- 切り替え時は瞬時にトラフィック移行
- 必要リソース: 通常の2倍

### Canary
- 段階的にトラフィックを移行
- 新バージョンPodを徐々に増加
- 必要リソース: 通常の1.2〜1.5倍

---

## 13. チューニングガイドライン

### 13.1 スループット向上

| 対策 | 効果 | 実装難易度 |
|-----|------|----------|
| Pod数増加 | 高 | 低 |
| グループコミット有効化 | 中〜高 | 低 |
| parallel_executor_count調整 | 中 | 低 |
| バックエンドDBスケールアップ | 高 | 中 |
| 接続プールサイズ調整 | 低〜中 | 低 |

### 13.2 レイテンシ改善

| 対策 | 効果 | 実装難易度 |
|-----|------|----------|
| DBとの距離短縮（同一AZ） | 高 | 中 |
| バックエンドDBスケールアップ | 中〜高 | 中 |
| トランザクションサイズ縮小 | 中 | 高（アプリ変更） |
| async_commit有効化 | 中 | 低（整合性注意） |

### 13.3 オーバーヘッド削減

| 対策 | 効果 |
|-----|------|
| レコードサイズを大きくする | 相対的オーバーヘッド率低下 |
| 不要なカラムを含めない | Beforeイメージサイズ削減 |
| バッチトランザクション | Coordinator I/O削減 |
| 読み取り専用はStorage API | メタデータ処理スキップ |
| Coordinator定期クリーンアップ | ストレージ削減 |

---

## 14. 監視メトリクス

### 14.1 ScalarDB Cluster監視項目

| メトリクス | 閾値目安 | アクション |
|-----------|---------|----------|
| CPU使用率 | > 70% | Pod追加検討 |
| メモリ使用率 | > 80% | メモリリーク確認 |
| gRPCレイテンシ（P99） | > 100ms | ボトルネック調査 |
| トランザクション失敗率 | > 1% | 競合/エラー調査 |
| 接続プール使用率 | > 80% | プールサイズ増加 |

### 14.2 Prometheus/Grafanaクエリ例

```promql
# TPS
sum(rate(scalardb_cluster_transaction_total[1m]))

# レイテンシ P99
histogram_quantile(0.99, sum(rate(scalardb_cluster_transaction_latency_bucket[5m])) by (le))

# エラー率
sum(rate(scalardb_cluster_transaction_total{status="error"}[5m]))
/ sum(rate(scalardb_cluster_transaction_total[5m]))
```

---

## 15. サイジングワークシート

### 15.1 ストレージオーバーヘッド

```
【入力パラメータ】
A. 元のレコードサイズ（平均）:     _____ バイト
B. プライマリキーサイズ:          _____ バイト
C. 非PKカラムサイズ (A - B):      _____ バイト
D. レコード数:                    _____ 件
E. 1日のトランザクション数:        _____ TPS

【計算】
1. メタデータオーバーヘッド/レコード = 120バイト
2. Beforeイメージ/レコード = C バイト
3. 総オーバーヘッド/レコード = 120 + C バイト
4. 総ストレージオーバーヘッド = (120 + C) × D バイト
5. Coordinatorサイズ/日 = E × 86400 × 50バイト
```

### 15.2 Pod数計算

```
【入力パラメータ】
A. 目標TPS:                    _____ TPS
B. ワークロードタイプ:           読み取り / バランス / 書き込みヘビー
C. 目標可用性:                  _____ %
D. 許容障害Pod数:               _____ Pod

【計算】
1. Pod単位TPS（ワークロード別）= _____ TPS
2. 性能Pod数 = ceil(A / 1) = _____ Pod
3. 可用性Pod数 = D + ceil(2 / 0.8) = _____ Pod
4. 最終Pod数 = max(2, 3, 3) = _____ Pod
```

---

## 参照リンク

- [ScalarDB Cluster Configurations](https://scalardb.scalar-labs.com/docs/latest/scalardb-cluster/scalardb-cluster-configurations/)
- [ScalarDB Benchmarks](https://github.com/scalar-labs/scalardb-benchmarks)
- [Helm Chart Configuration](https://github.com/scalar-labs/helm-charts/blob/main/docs/configure-custom-values-scalardb-cluster.md)
- [EKS Cluster Guidelines](https://scalardb.scalar-labs.com/docs/latest/scalar-kubernetes/CreateEKSClusterForScalarDBCluster/)
- [ScalarDB Schema Loader](https://scalardb.scalar-labs.com/docs/latest/schema-loader/)
