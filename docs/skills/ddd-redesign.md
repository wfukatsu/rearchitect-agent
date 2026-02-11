# /ddd-redesign — DDD再設計

**カテゴリ**: Design（設計） | **Phase 3**

DDD評価結果に基づいて、境界コンテキスト・集約・値オブジェクトの再設計計画を策定します。

## 使用方法

```bash
/ddd-redesign ./path/to/source
```

## 前提条件

### 必須（すべて必要）
- `reports/02_evaluation/ddd-strategic-evaluation.md`（`/ddd-evaluation` の出力）
- `reports/02_evaluation/ddd-tactical-evaluation.md`
- `reports/02_evaluation/ddd-improvement-plan.md`

### 推奨
- `reports/01_analysis/ubiquitous-language.md`
- `reports/01_analysis/domain-code-mapping.md`
- `reports/02_evaluation/mmi-overview.md`
- `reports/02_evaluation/mmi-improvement-plan.md`
- `reports/02_evaluation/integrated-evaluation.md`

## 実行ステップ

1. **前提条件の検証** — 必須3ファイルの存在確認
2. **評価結果の統合** — DDD/MMI評価結果を読み込み、課題を優先順位付け（Critical/High/Medium/Low）
3. **ドメイン分析** — ビジネス構造軸（Pipeline/Blackboard/Dialogue）× サービス境界軸（Process/Master/Integration/Supporting）で分類 → `domain-analysis.md`
4. **境界コンテキストの再設計** — ビジネスケイパビリティ、チーム構造、技術的制約に基づく再定義 → `bounded-contexts-redesign.md`
5. **コンテキストマップの再設計** — Partnership/Shared Kernel/Customer-Supplier/ACL等の関係パターン定義 → `context-map.md`
6. **集約の再設計** — 集約ルート、エンティティ、値オブジェクト、ドメインイベントの設計 → `aggregate-redesign.md`
7. **ユビキタス言語の整備** — 用語統一、コンテキスト別用語定義 → `ubiquitous-language-refined.md`
8. **システムマッピング** — 現行モジュール→新コンテキストの対応表 → `system-mapping.md`
9. **移行ロードマップ** — Phase 0（準備）〜Phase 4（最適化）の段階的計画 → `ddd-migration-roadmap.md`
10. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/domain-analysis.md` | ドメイン分類結果 |
| `reports/03_design/bounded-contexts-redesign.md` | 境界コンテキスト再設計 |
| `reports/03_design/context-map.md` | コンテキストマップ（Mermaid図含む） |
| `reports/03_design/aggregate-redesign.md` | 集約・エンティティ・値オブジェクト再設計 |
| `reports/03_design/ubiquitous-language-refined.md` | 整備済みユビキタス言語 |
| `reports/03_design/system-mapping.md` | 現行→新設計マッピング |
| `reports/03_design/ddd-migration-roadmap.md` | 移行ロードマップ |

中間状態: `work/{project}/design/ddd-redesign/` 配下

## 補足

このスキルは旧 `/map-domains` のドメイン分類・コンテキストマップ・システムマッピング機能を統合しています。完全なDDD再設計を行う場合はこのスキルを使用してください。

## 関連スキル

- 前提: [/ddd-evaluation](ddd-evaluation.md), [/evaluate-mmi](evaluate-mmi.md), [/integrate-evaluations](integrate-evaluations.md)
- 次のフェーズ: [/design-microservices](design-microservices.md), [/design-scalardb](design-scalardb.md)
