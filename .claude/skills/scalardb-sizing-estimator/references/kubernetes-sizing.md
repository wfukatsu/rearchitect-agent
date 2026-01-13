# Kubernetes サイジング詳細リファレンス

## 1. マネージドKubernetes比較

| 項目 | EKS | AKS | GKE |
|-----|-----|-----|-----|
| 管理費用 | $73/月/クラスター | Free Tier/Standard有 | Zonal: 1クラスター無料, Regional: $73/月 |
| 最大ノード数 | 5,000 | 5,000 (CNI Overlay) | 15,000+ (v1.31〜: 65,000) |
| Pod/ノード | 110-250 | 110-250 | 110-256 |
| SLA | 99.95% | 99.95% (Standard) | 99.95% (Regional) |
| 推奨オートスケーラー | Karpenter | Cluster Autoscaler | NAP / Cluster Autoscaler |

---

## 2. クラウド別サービスクォータ

### 2.1 Amazon EKS

| 項目 | デフォルト制限 | 最大（要申請） |
|-----|--------------|--------------|
| クラスター数/リージョン | 100 | 申請可能 |
| マネージドノードグループ/クラスター | 30 | 申請可能 |
| ノード数/ノードグループ | 450 | 申請可能 |
| Fargateプロファイル/クラスター | 10 | 申請可能 |
| etcdストレージ | 8 GiB | - |

**スケール目安**:
| スケール | ノード数 | Pod数 | 推奨事項 |
|---------|--------|-------|---------|
| 小規模 | 〜100 | 〜3,000 | 標準構成 |
| 中規模 | 100〜300 | 3,000〜15,000 | 計画的スケーリング |
| 大規模 | 300〜1,000 | 15,000〜50,000 | AWSサポート協議推奨 |
| 超大規模 | 1,000〜5,000 | 50,000〜 | TAM協議必須 |

### 2.2 Azure AKS

| 項目 | デフォルト制限 | 備考 |
|-----|--------------|------|
| ノード数/ノードプール | 1,000 | サポートチケットで拡張可 |
| ノードプール数/クラスター | 100 | - |
| Pod数/ノード（デフォルト） | 110 | maxPods設定で調整 |
| Azure CNI Overlay最大ノード | 5,000 | - |
| Azure CNI Overlay最大Pod | 200,000 | - |

**スケール目安**:
| スケール | ノード数 | Pod数 | 推奨CNI |
|---------|--------|-------|---------|
| 小規模 | 〜100 | 〜11,000 | Azure CNI |
| 中規模 | 100〜400 | 〜44,000 | Azure CNI |
| 大規模 | 400〜1,000 | 〜110,000 | Azure CNI / CNI Overlay |
| 超大規模 | 1,000〜5,000 | 〜200,000 | Azure CNI Overlay |

### 2.3 Google GKE

| 項目 | 制限 |
|-----|------|
| ノード数/クラスター（Standard） | 15,000（v1.31以降: 65,000） |
| Pod数/ノード（デフォルト） | 110 |
| Pod数/ノード（最大） | 256 |

**クラスターモード**:
| モード | 説明 | ScalarDB向け |
|-------|------|-------------|
| Standard | 完全制御 | 推奨（詳細設定が必要な場合） |
| Autopilot | Google管理 | 運用負荷軽減したい場合（一部制限あり） |

---

## 3. ノードインスタンスタイプ

### 3.1 AWS EC2 (EKS)

**推奨インスタンスファミリー**:
| ファミリー | 特徴 | ScalarDB向けユースケース |
|-----------|------|------------------------|
| m6i/m7i | 汎用（Intel） | 標準的なワークロード |
| m6g/m7g | 汎用（Graviton） | コスト効率重視（約20%安価） |
| r6i/r7i | メモリ最適化（Intel） | 大量接続、大きなヒープ |
| r6g/r7g | メモリ最適化（Graviton） | コスト効率+メモリ重視 |
| c6i/c7i | コンピュート最適化 | CPU集中型ワークロード |

**環境別推奨サイズ**:
| 環境 | 推奨インスタンス | vCPU | メモリ | 月額(USD) |
|-----|----------------|------|-------|----------|
| 開発 | m6i.large | 2 | 8 GiB | $70 |
| ステージング | m6i.xlarge | 4 | 16 GiB | $140 |
| 本番（小） | m6i.2xlarge | 8 | 32 GiB | $280 |
| 本番 ScalarDB | r6i.2xlarge | 8 | 64 GiB | $360 |
| 本番（大） | r6i.4xlarge | 16 | 128 GiB | $720 |
| 本番 App | m6i.xlarge | 4 | 16 GiB | $140 |

### 3.2 Azure VM (AKS)

**推奨VMシリーズ**:
| シリーズ | 特徴 | ScalarDB向けユースケース |
|--------|------|------------------------|
| Dsv5 | 汎用（最新） | 標準的なワークロード |
| Ddsv5 | 汎用 + ローカルSSD | 一時ストレージ要件 |
| Esv5 | メモリ最適化 | 大量接続、大きなヒープ |
| Edsv5 | メモリ最適化 + ローカルSSD | 高メモリ + 一時ストレージ |
| Dasv5 | AMD汎用 | コスト効率重視 |

**環境別推奨サイズ**:
| 環境 | 推奨VMサイズ | vCPU | メモリ | 月額(USD) |
|-----|-------------|------|-------|----------|
| 開発 | Standard_D2s_v5 | 2 | 8 GiB | $70 |
| ステージング | Standard_D4s_v5 | 4 | 16 GiB | $140 |
| 本番（小） | Standard_D8s_v5 | 8 | 32 GiB | $280 |
| 本番 ScalarDB | Standard_E8s_v5 | 8 | 64 GiB | $360 |
| 本番（大） | Standard_E16s_v5 | 16 | 128 GiB | $720 |
| 本番 App | Standard_D4s_v5 | 4 | 16 GiB | $140 |

**VMサイズ別オーバーヘッド**:
| メモリ | Kubernetesオーバーヘッド |
|-------|------------------------|
| 2 GiB | 〜65% |
| 8 GiB | 〜25% |
| 64 GiB | 〜10% |

### 3.3 GCP (GKE)

**推奨マシンシリーズ**:
| シリーズ | 特徴 | ScalarDB向けユースケース |
|--------|------|------------------------|
| E2 | 汎用（コスト効率） | 開発・テスト |
| N2 | 汎用（バランス） | 標準的なワークロード |
| N2D | AMD汎用 | コスト効率重視 |
| C2/C2D | コンピュート最適化 | CPU集中型 |
| M2/M3 | メモリ最適化 | 大量接続、大きなヒープ |
| T2A | Arm（Tau） | コスト最適化（約20%安価） |

**環境別推奨サイズ**:
| 環境 | 推奨マシンタイプ | vCPU | メモリ | 月額(USD) |
|-----|----------------|------|-------|----------|
| 開発 | e2-standard-2 | 2 | 8 GiB | $50 |
| ステージング | n2-standard-4 | 4 | 16 GiB | $120 |
| 本番（小） | n2-standard-8 | 8 | 32 GiB | $240 |
| 本番 ScalarDB | n2-highmem-8 | 8 | 64 GiB | $340 |
| 本番（大） | n2-highmem-16 | 16 | 128 GiB | $680 |
| 本番 App | n2-standard-4 | 4 | 16 GiB | $120 |

**カスタムマシンタイプ**:
```
n2-custom-{vCPU}-{メモリMB}
例: n2-custom-8-49152（8 vCPU, 48 GiB）
```

---

## 4. ノードあたりのPod数

### 4.1 EKS VPC CNI Pod制限

Pod数はENI（Elastic Network Interface）のIP数に依存:
```
最大Pod数 = (ENI数 × ENIあたりIP数) - 1
```

| インスタンスタイプ | ENI数 | ENIあたりIP | 最大Pod数 | Prefix Delegation有効時 |
|------------------|-------|-----------|----------|------------------------|
| t3.medium | 3 | 6 | 17 | 110 |
| m5.large | 3 | 10 | 29 | 110 |
| m5.xlarge | 4 | 15 | 58 | 110 |
| m5.2xlarge | 4 | 15 | 58 | 110 |
| m5.4xlarge | 8 | 30 | 234 | 250 |
| r5.2xlarge | 4 | 15 | 58 | 110 |
| r5.4xlarge | 8 | 30 | 234 | 250 |

**Prefix Delegation有効化**:
- 要件: Nitroシステム対応インスタンス、VPC CNI v1.9.0以降
- 設定: `ENABLE_PREFIX_DELEGATION=true`

### 4.2 AKS maxPods

| 構成 | 最大Pod数/ノード | 備考 |
|-----|-----------------|------|
| Azure CNI（デフォルト） | 110 | IPアドレス事前予約 |
| Azure CNI Overlay | 250 | オーバーレイネットワーク |
| Kubenet | 110 | ルートベース |

**maxPods設定**:
```bash
# クラスター作成時に指定（10〜110の範囲）
az aks create --max-pods 50

# ノードプール作成時に指定
az aks nodepool add --max-pods 30
```
**注意**: 作成後の変更は不可。ノードプールの再作成が必要。

### 4.3 GKE maxPodsPerNode

| 最大Pod数/ノード | 割り当てCIDR |
|-----------------|-------------|
| 8 | /28 |
| 16 | /27 |
| 32 | /26 |
| 64 | /25 |
| 110（デフォルト） | /24 |
| 256（最大） | /23 |

```bash
# クラスター/ノードプール作成時に指定
gcloud container clusters create CLUSTER_NAME \
  --max-pods-per-node=64
```

---

## 5. システムリソース予約

### 5.1 EKS リソース予約
```
CPU: 最初の4コアまで6%、以降0.25%
メモリ: 255MiB + 最初の4GBの25% + 次の4GBの20% + 以降6%
```

### 5.2 AKS リソース予約
```
CPU: 最初の1コアまで60m、以降25m/コア
メモリ: 750MiB〜（インスタンスサイズ依存）
```

### 5.3 GKE リソース予約

**CPU予約**:
- 1コア目の6%
- 次の1コアの1%
- 次の2コアの0.5%
- 4コア超の0.25%
- 110 Pod超の場合: 追加400 mCPU

**メモリ予約**:
- 1 GiB未満: 255 MiB
- 最初の4 GiB: 25%
- 次の4 GiB（4-8 GiB）: 20%
- 次の8 GiB（8-16 GiB）: 10%
- 次の112 GiB（16-128 GiB）: 6%
- 128 GiB超: 2%
- 追加: 100 MiB（eviction threshold）

**計算例（32 GiB メモリノード）**:
```
255 MiB + (4 × 0.25) + (4 × 0.20) + (8 × 0.10) + (16 × 0.06) + 100 MiB
≈ 3.1 GiB 予約
→ 使用可能: 約29 GiB
```

---

## 6. ネットワーク構成

### 6.1 CNIオプション比較

**EKS**:
| CNI | 特徴 | ユースケース |
|-----|------|-------------|
| VPC CNI | AWSネイティブ、高パフォーマンス | 標準（推奨） |
| VPC CNI + Prefix Delegation | 高Pod密度 | Pod数が多い場合 |
| Calico | ネットワークポリシー | セキュリティ要件が高い場合 |

**AKS**:
| CNI | IP消費 | スケール | ユースケース |
|-----|--------|---------|-------------|
| Azure CNI | 高（Pod単位） | 中 | VNet統合必須 |
| Azure CNI Overlay | 低（オーバーレイ） | 高 | 大規模クラスター |
| Kubenet | 低（NAT） | 中 | シンプル構成 |

**GKE**:
| 構成 | 説明 |
|-----|------|
| VPC-native | Alias IP、PodにVPCから直接IP割当（デフォルト） |
| Dataplane V2 (Cilium) | eBPF、高性能 |

### 6.2 IPアドレス計画

**EKS**:
```
必要IP数 = ノード数 × ノードあたりPod数 + 予備
例: 50ノード × 58 Pod/ノード = 2,900 IP → /20サブネット以上
```

**AKS**:
```
必要IP数 = ノード数 × maxPods + ノード数（ノードIP用）
例: 10ノード × 30 maxPods = 310 IP → /23サブネット以上
```

**GKE**:
```
Pod CIDR サイズ = ノード数 × (2 × maxPodsPerNode)
```

### 6.3 Pod CIDR計画

| クラスター規模 | ノードサブネット | Pod CIDR |
|--------------|----------------|----------|
| 〜50ノード | /24 | /16 |
| 〜250ノード | /22 | /14 |
| 〜1000ノード | /20 | /12 |

### 6.4 AKS使用不可アドレス範囲

以下のCIDRはAKSで使用不可:
- `169.254.0.0/16`
- `172.30.0.0/16`
- `172.31.0.0/16`
- `192.0.2.0/24`

---

## 7. ノード数計算

### 7.1 計算式

```
必要ノード数 = ceil(
  (ScalarDB_Pods × ScalarDB_CPU + App_Pods × App_CPU + System_Pods × System_CPU)
  / (Node_CPU × 利用可能率)
) × 冗長係数

利用可能率 = 0.85〜0.90（システム予約分を除く）
冗長係数 = 1.3〜1.5
```

### 7.2 環境別推奨ノード数

| 環境 | ScalarDB用 | App用 | System用 | 合計 |
|-----|-----------|-------|---------|------|
| 開発 | 1 | 1 | 0 | 2 |
| テスト | 2 | 1 | 0 | 3 |
| ステージング | 2-3 | 2 | 1 | 5 |
| 本番（小） | 3 | 3 | 2 | 8 |
| 本番（中） | 5 | 5 | 2 | 12 |
| 本番（大） | 10+ | 10+ | 3 | 23+ |

---

## 8. ノードプール構成

### 8.1 本番環境推奨

```yaml
nodePools:
  - name: system
    purpose: kube-system, monitoring, ingress
    instanceType: m6i.large / Standard_D4s_v5 / n2-standard-4
    minNodes: 2
    maxNodes: 3
    taints: []

  - name: scalardb
    purpose: ScalarDB Cluster Pods
    instanceType: r6i.2xlarge / Standard_E8s_v5 / n2-highmem-8
    minNodes: 3
    maxNodes: 10
    taints:
      - key: dedicated
        value: scalardb
        effect: NoSchedule
    labels:
      workload: scalardb

  - name: application
    purpose: Application Pods (BFF, Process API, System API)
    instanceType: m6i.xlarge / Standard_D4s_v5 / n2-standard-4
    minNodes: 3
    maxNodes: 20
    labels:
      workload: application
```

---

## 9. ストレージ

### 9.1 ディスクタイプ比較

**EKS (EBS)**:
| タイプ | IOPS | スループット | ユースケース | 月額/100GB |
|-------|------|-------------|-------------|-----------|
| gp3 | 3,000〜16,000 | 125〜1,000 MiB/s | 汎用（推奨） | $8 |
| io2 | 〜64,000 | 〜1,000 MiB/s | 高IOPS要件 | $12.5+ |

**AKS (Azure Disk)**:
| タイプ | IOPS | スループット | ユースケース | 月額/100GB |
|-------|------|-------------|-------------|-----------|
| Premium SSD | 〜20,000 | 〜900 MiB/s | 本番（推奨） | $15 |
| Premium SSD v2 | 〜80,000 | 〜1,200 MiB/s | 高IOPS要件 | $19 |
| Standard SSD | 〜6,000 | 〜750 MiB/s | 開発・テスト | $6 |
| Ultra Disk | 〜160,000 | 〜4,000 MiB/s | 超高性能 | $30+ |

**GKE (Persistent Disk)**:
| タイプ | IOPS/GiB | スループット | ユースケース | 月額/100GB |
|-------|----------|-------------|-------------|-----------|
| pd-standard | 読取0.75, 書込1.5 | 120 MiB/s | 開発 | $4 |
| pd-balanced | 6 | 240 MiB/s | 汎用 | $10 |
| pd-ssd | 30 | 480 MiB/s | 本番（推奨） | $17 |
| pd-extreme | カスタム | 2,400 MiB/s | 高IOPS | $30+ |

### 9.2 StorageClass推奨設定

**AWS**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
```

**Azure**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: managed-premium-retain
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**GCP**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

---

## 10. オートスケーリング

### 10.1 Cluster Autoscaler推奨設定

| 設定項目 | 推奨値 | 説明 |
|---------|-------|------|
| scan-interval | 10s | スキャン間隔 |
| scale-down-delay-after-add | 10m | スケールダウン待機 |
| scale-down-unneeded-time | 10m | 不要判定時間 |
| max-node-provision-time | 15m | プロビジョニングタイムアウト |
| scale-down-utilization-threshold | 0.5 | スケールダウン閾値 |

### 10.2 AWS Karpenter（推奨）

| 特徴 | 説明 |
|-----|------|
| 高速プロビジョニング | 数十秒でノード追加 |
| コスト最適化 | 最適なインスタンスタイプを自動選択 |
| 統合デプロビジョニング | 空きノードの効率的な削除 |

### 10.3 GKE Node Auto-Provisioning（NAP）

```bash
gcloud container clusters update CLUSTER_NAME \
  --enable-autoprovisioning \
  --min-cpu 10 \
  --max-cpu 100 \
  --min-memory 64 \
  --max-memory 512
```

| 特徴 | 説明 |
|-----|------|
| 自動ノードプール作成 | ワークロードに最適なノードプールを自動作成 |
| リソース制限 | CPU/メモリの上限設定可能 |

### 10.4 GKE オートスケーリングプロファイル

| プロファイル | 特徴 |
|------------|------|
| balanced | バランス型（デフォルト） |
| optimize-utilization | 積極的なスケールダウン |

### 10.5 HPA（Application Pod用）

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 11. 可用性構成

### 11.1 Multi-AZ/Zone構成

| 構成 | EKS SLA | AKS SLA | GKE SLA |
|-----|---------|---------|---------|
| Single AZ/Zone | 99.5% | 99.9% | 99.5% |
| Multi-AZ/Regional | 99.95% | 99.95% | 99.95% |

### 11.2 TopologySpreadConstraints

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: scalardb-cluster
```

---

## 12. Blue/Green・Canary対応

### 12.1 Blue/Green構成
```
必要ノード数 = 通常ノード数 × 2
切り替え方式: Ingress/Service切り替え or DNS切り替え
```

### 12.2 Canary構成（Argo Rollouts）
```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 30
      - pause: {duration: 5m}
      - setWeight: 60
      - pause: {duration: 5m}
```

---

## 13. コスト最適化

### 13.1 Reserved Instances / Committed Use

| クラウド | 1年 | 3年 |
|---------|-----|-----|
| AWS Savings Plans | 〜40% | 〜60% |
| Azure Reserved VM | 〜40% | 〜60% |
| GCP Committed Use | 〜37% | 〜55% |

### 13.2 Spot/Preemptible VM

| ユースケース | 適合性 |
|------------|--------|
| 開発環境 | 適合 |
| バッチ処理 | 適合 |
| ステージング | 条件付き適合 |
| 本番ScalarDB | **非推奨**（中断リスク） |

### 13.3 適正サイジング

- **目標使用率**: 70-80%
- **監視ツール**: CloudWatch Container Insights / Azure Monitor / Cloud Monitoring
- **推奨**: 各クラウドのRecommender機能を活用

### 13.4 Arm/Graviton インスタンス

| クラウド | Intel相当 | Arm相当 | コスト削減 |
|---------|----------|---------|-----------|
| AWS | m6i.xlarge | m6g.xlarge | 約20% |
| GCP | n2-standard-4 | t2a-standard-4 | 約20% |

**注意**: ARM64アーキテクチャのため、コンテナイメージの互換性を確認すること。

---

## 14. 監視と推奨アラート

### 14.1 推奨メトリクス

| メトリクス | 閾値目安 |
|-----------|---------|
| CPU使用率 | アラート: 80% |
| メモリ使用率 | アラート: 85% |
| Pod再起動数 | アラート: 5回/時 |
| ノードステータス | NotReady検知 |

### 14.2 監視ツール

| クラウド | 推奨ツール |
|---------|-----------|
| AWS | CloudWatch Container Insights |
| Azure | Azure Monitor for Containers |
| GCP | Cloud Monitoring / GKE Dashboard |

---

## 参照リンク

### AWS EKS
- [Amazon EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- [EKS Service Quotas](https://docs.aws.amazon.com/eks/latest/userguide/service-quotas.html)
- [VPC CNI Plugin](https://github.com/aws/amazon-vpc-cni-k8s)
- [Karpenter](https://karpenter.sh/)

### Azure AKS
- [AKS Quotas and Limits](https://learn.microsoft.com/en-us/azure/aks/quotas-skus-regions)
- [AKS VM Sizes](https://learn.microsoft.com/en-us/azure/aks/aks-virtual-machine-sizes)
- [Azure CNI Networking](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overview)
- [AKS Best Practices](https://learn.microsoft.com/en-us/azure/aks/best-practices)

### Google GKE
- [GKE Node Sizing](https://cloud.google.com/kubernetes-engine/docs/concepts/plan-node-sizes)
- [GKE Quotas and Limits](https://cloud.google.com/kubernetes-engine/quotas)
- [VPC-native Clusters](https://cloud.google.com/kubernetes-engine/docs/concepts/alias-ips)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
