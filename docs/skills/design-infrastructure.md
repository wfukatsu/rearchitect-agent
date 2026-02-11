# /design-infrastructure — インフラ基盤構成設計

**カテゴリ**: Design（設計） | **Phase 8.7**

AWS/Azure/GCP/OpenShift向けのKubernetes・IaC構成を設計・生成します。

## 使用方法

```bash
/design-infrastructure
```

> **注意**: このスキルは対象パスの引数を必要としません。設計ドキュメントから自動的にインフラ構成を生成します。

## 前提条件

### 必須
- `reports/03_design/target-architecture.md`（`/design-microservices`）

### 推奨
- `reports/sizing-estimates/*.md`（`/scalardb-sizing-estimator`）
- `reports/03_design/scalardb-schema.md`（`/design-scalardb`）
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`）

## 実行ステップ

1. **前提条件の検証** — 設計ドキュメントの存在確認
2. **Kubernetes base manifests生成** — Kustomize base/overlayパターンでサービス別マニフェスト
3. **環境別overlay生成** — dev / staging / production の環境分離
4. **IaC生成** — Terraform / Pulumi / CloudFormation でクラウドリソース定義
5. **OpenShift構成生成** — Operator, Route, SCC, Project等（選択時のみ）
6. **ScalarDB Cluster Helm values生成** — エディション・環境別の values.yaml
7. **インフラドキュメント生成** — アーキテクチャ図、デプロイ手順書、環境マトリクス

## 出力ファイル

### レポート

| ファイル | 内容 |
|---------|------|
| `reports/08_infrastructure/infrastructure-architecture.md` | アーキテクチャ総合図（Mermaid含む） |
| `reports/08_infrastructure/deployment-guide.md` | デプロイ手順書 |
| `reports/08_infrastructure/environment-matrix.md` | 環境比較マトリクス |
| `reports/08_infrastructure/security-configuration.md` | セキュリティ設定ガイド |

### 生成コード

| ディレクトリ | 内容 |
|-------------|------|
| `generated/infrastructure/k8s/base/` | Kustomize baseマニフェスト |
| `generated/infrastructure/k8s/overlays/` | 環境別overlay（dev/staging/production） |
| `generated/infrastructure/terraform/` | Terraformモジュール＆環境設定 |
| `generated/infrastructure/openshift/` | OpenShift固有設定（選択時のみ） |

## 関連スキル

- 前提: [/design-microservices](design-microservices.md), [/scalardb-sizing-estimator](scalardb-sizing-estimator.md)
- 補完: [/estimate-cost](estimate-cost.md)
