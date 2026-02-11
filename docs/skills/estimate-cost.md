# /estimate-cost — コスト見積もり

**カテゴリ**: Estimation（見積もり） | **Phase 9**

マイクロサービスアーキテクチャ移行に伴うインフラストラクチャ費用とライセンス費用を見積もります。

## 使用方法

```bash
/estimate-cost ./reports
```

## 前提条件

### 必須
- `reports/03_design/target-architecture.md`（`/design-microservices`）

### 推奨
- `reports/03_design/scalardb-architecture.md`（`/design-scalardb`）
- `reports/sizing-estimates/*.md`（`/scalardb-sizing-estimator`）
- `reports/08_infrastructure/infrastructure-architecture.md`（`/design-infrastructure`）

## 見積もり項目

1. **クラウドインフラ費用** — Kubernetes（EKS/AKS/GKE）、データベース、ネットワーク、ストレージ
2. **ライセンス費用** — ScalarDB Enterprise、その他商用ソフトウェア
3. **運用費用** — 監視（Datadog/Prometheus）、バックアップ、サポート契約
4. **初期構築費用** — 移行作業、開発工数、トレーニング

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/05_estimate/cost-estimation.md` | 月額/年額のコスト見積もり、内訳、最適化提案 |

## 関連スキル

- 前提: [/design-microservices](design-microservices.md), [/design-infrastructure](design-infrastructure.md)
- 補完: [/scalardb-sizing-estimator](scalardb-sizing-estimator.md)
