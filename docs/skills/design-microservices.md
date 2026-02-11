# /design-microservices — マイクロサービス設計

**カテゴリ**: Design（設計） | **Phase 4**

ドメイン分析・MMI評価の結果をもとに、ターゲットアーキテクチャ・変換計画・運用計画を策定します。

## 使用方法

```bash
/design-microservices ./path/to/source
```

## 前提条件

### 必須（`/ddd-redesign` の出力）
- `reports/03_design/bounded-contexts-redesign.md`
- `reports/03_design/context-map.md`
- `reports/03_design/aggregate-redesign.md`
- `reports/03_design/domain-analysis.md`
- `reports/03_design/system-mapping.md`

### 推奨
- `reports/02_evaluation/ddd-strategic-evaluation.md`
- `reports/02_evaluation/mmi-overview.md`
- `reports/01_analysis/ubiquitous-language.md`

## 実行ステップ

1. **前提条件の検証** — 必須5ファイルの存在確認
2. **設計原則の確認** — Single Responsibility、Loose Coupling等のマイクロサービス原則
3. **技術スタック・非機能要件の確認** — デプロイ基盤、通信パターン、可観測性をユーザーに対話形式で確認
4. **サービス設計** — 各コンテキストに対するサービス定義（API、イベント、依存関係、非機能要件）
5. **通信パターン設計** — 同期（REST/gRPC）と非同期（Event/Saga/CQRS）の設計
6. **データ設計** — Database per Service、データ同期パターン
7. **インフラ設計** — コンテナ/オーケストレーション、サービスメッシュ → `target-architecture.md`
8. **移行計画策定** — Phase 1-4の段階的移行戦略 → `transformation-plan.md`
9. **運用計画策定** — 可観測性、SLO/SLI、インシデント管理 → `operations-feedback.md`
10. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/target-architecture.md` | ターゲットアーキテクチャ（サービスカタログ、通信設計、データ設計、インフラ設計） |
| `reports/03_design/transformation-plan.md` | 変換計画（移行戦略、フェーズ別詳細、リスク管理） |
| `reports/03_design/operations-feedback.md` | 運用計画（可観測性、SLO/SLI、インシデント管理） |

## 関連スキル

- 前提: [/ddd-redesign](ddd-redesign.md), [/map-domains](map-domains.md)
- 次のフェーズ: [/design-api](design-api.md), [/design-scalardb](design-scalardb.md), [/design-implementation](design-implementation.md)
