# /scalardb-sizing-estimator — ScalarDBサイジング見積もり

**カテゴリ**: Estimation（見積もり） | **Phase 9.5**

対話形式でScalarDB Cluster / Analyticsのインフラ構成・Pod数・コスト見積もりを算出します。

## 使用方法

```bash
/scalardb-sizing-estimator
```

> **注意**: このスキルは対話形式で実行します。引数は不要です。

## 前提条件

### 推奨
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`、未選定時はヒアリングで確認）
- `reports/03_design/target-architecture.md`（`/design-microservices`）

## エディション別見積もり

### Enterprise版（Cluster構成）
- Kubernetes Pod数・リソース（CPU/メモリ）
- ScalarDB Cluster ノード数
- Envoyプロキシ構成
- ストレージバックエンドのサイジング

### OSS版（組み込み構成）
- アプリケーションPodへのリソース追加分
- ストレージバックエンドのサイジング

## 対話形式のヒアリング項目

1. **エディション確認** — OSS / Enterprise Standard / Premium
2. **サービス数** — マイクロサービスの数と各サービスのTPS
3. **データボリューム** — 初期データ量、年間成長率
4. **可用性要件** — SLA目標（99.9% / 99.99%）
5. **環境数** — 開発/ステージング/本番

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/sizing-estimates/scalardb-sizing-*.md` | サイジング見積もり結果（Markdown） |
| `reports/sizing-estimates/scalardb-sizing-*.html` | サイジング見積もり結果（HTML） |

## 関連スキル

- 前提: [/select-scalardb-edition](select-scalardb-edition.md)
- 補完: [/estimate-cost](estimate-cost.md), [/design-infrastructure](design-infrastructure.md)
