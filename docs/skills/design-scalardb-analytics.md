# /design-scalardb-analytics — ScalarDB Analytics設計

**カテゴリ**: Design（設計） | **Phase 5.5**

ScalarDB Analyticsを使用した分析基盤アーキテクチャを設計します。Apache Sparkベースの分析クエリ、マルチDB横断分析を策定します。

## 使用方法

```bash
/design-scalardb-analytics ./path/to/source
```

> **注意**: トランザクション処理の設計には `/design-scalardb` を使用してください。分析要件がある場合に本スキルを併用します。

## 前提条件

### 必須
- `reports/01_analysis/` 配下の分析結果
- `reports/03_design/target-architecture.md`

### 推奨
- `reports/03_design/scalardb-schema.md`（`/design-scalardb`）

## ScalarDB Analytics概要

ScalarDB AnalyticsはHTAP（Hybrid Transactional/Analytical Processing）アーキテクチャの分析コンポーネントです。Apache Sparkをクエリエンジンとして、複数データベースにまたがる統合分析クエリを実現します。

> **エディション制約**: Enterprise Standard / Premium でのみ利用可能。OSS版では使用不可。

## 実行ステップ

1. **前提条件の検証** — 分析結果ファイルの存在確認
2. **分析基盤アーキテクチャ設計** — Spark構成、データソース統合
3. **データカタログ設計** — 論理スキーマ、物理マッピング
4. **クエリ設計** — 分析クエリパターン、パフォーマンス最適化
5. **データパイプライン設計** — ETL/ELTフロー、リアルタイム分析
6. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/scalardb-analytics-design.md` | 分析基盤アーキテクチャ、データカタログ、クエリパターン、パイプライン設計 |

## 関連スキル

- 前提: [/design-scalardb](design-scalardb.md)
- 補完: [/scalardb-sizing-estimator](scalardb-sizing-estimator.md)（サイジング見積もり）
