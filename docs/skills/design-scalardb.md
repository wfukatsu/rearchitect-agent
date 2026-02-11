# /design-scalardb — ScalarDBデータアーキテクチャ設計

**カテゴリ**: Design（設計） | **Phase 5**

エディション設定に基づき、マイクロサービスのデータアーキテクチャを設計します。分散トランザクション、スキーマ設計、ポリグロット永続化を策定します。

## 使用方法

```bash
/design-scalardb ./path/to/source
```

## 前提条件

### 必須
- `reports/03_design/target-architecture.md`（`/design-microservices` の出力）

### 推奨
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`、未選定時はEnterprise Standardをデフォルト）
- `reports/03_design/aggregate-redesign.md`（`/ddd-redesign`）
- `reports/03_design/bounded-contexts-redesign.md`
- `reports/01_analysis/system-overview.md`

## 実行ステップ

1. **前提条件の検証** — 必須ファイル、エディション設定の確認
2. **エディション別ワークフロー分岐** — OSS（組み込み）/ Enterprise（Cluster）で設計内容を分岐
3. **現状分析** — データソース一覧、クロスサービストランザクション、課題整理
4. **非機能要件の確認** — 整合性レベル、ワークロード特性、データ保持を対話形式で確認
5. **Cluster構成設計** — ノード数、リージョン構成、接続方式（Enterprise版のみ）
6. **ストレージバックエンド設計** — サービス別ストレージマッピング、Multi-Storage構成
7. **スキーマ設計** — Namespace/テーブル/パーティションキー/クラスタリングキー設計
8. **トランザクション設計** — Consensus Commit / Two-Phase Commit / Sagaパターン
9. **例外処理設計** — Transient/Non-Transient/Unknown例外の処理戦略
10. **パフォーマンス最適化** — Group Commit、Implicit Pre-Read
11. **マイグレーション計画** — Shadow Migration → 段階的切り替え → 完全移行
12. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/scalardb-architecture.md` | Cluster構成、接続方式、ストレージ構成、セキュリティ |
| `reports/03_design/scalardb-schema.md` | テーブル定義、インデックス、パーティション戦略 |
| `reports/03_design/scalardb-transaction.md` | トランザクションパターン、Saga設計、例外処理 |
| `reports/03_design/scalardb-migration.md` | フェーズ別移行計画、検証計画、ロールバック手順 |

## エディション別の設計差異

| ステップ | Enterprise (Cluster) | OSS (Embedded) |
|---------|---------------------|----------------|
| Cluster構成設計 | 実行 | スキップ |
| 対応ストレージ | 全DB | PostgreSQL/MySQL/DynamoDB/CosmosDB/Cassandra |
| API | Core/SQL/Spring Data/GraphQL | Core APIのみ |
| 認証・認可 | Cluster組み込み | アプリケーション側で実装 |

## 関連スキル

- 前提: [/design-microservices](design-microservices.md), [/select-scalardb-edition](select-scalardb-edition.md)
- 補完: [/design-scalardb-analytics](design-scalardb-analytics.md)（分析基盤が必要な場合）
- 次のフェーズ: [/design-api](design-api.md), [/design-implementation](design-implementation.md)
