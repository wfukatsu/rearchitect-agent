# /ddd-evaluation — DDD評価

**カテゴリ**: Evaluation（評価） | **Phase 2b**

ドメイン駆動設計（DDD）の視点から既存システムを評価し、戦略的設計・戦術的設計の両面で改善点を特定します。

## 使用方法

```bash
/ddd-evaluation ./path/to/source
```

## 前提条件

- **必須**: 対象システムのソースコードにアクセス可能
- **推奨**: `reports/01_analysis/ubiquitous-language.md`（`/analyze-system` の出力）
- **推奨**: `reports/before/{project}/ddd-readiness.md`（`/system-investigation` の出力）

## 実行ステップ

1. **前提条件の検証** — 分析結果ファイルの存在確認
2. **戦略的設計の評価** — 境界コンテキスト、ユビキタス言語、コンテキストマップの分析 → `ddd-strategic-evaluation.md`
3. **戦術的設計の評価** — エンティティ、値オブジェクト、集約、リポジトリの分析 → `ddd-tactical-evaluation.md`
4. **パターン適用状況の分析** — DDDパターンの適用率と整合性 → `ddd-pattern-analysis.md`
5. **改善計画の策定** — 優先度付きの改善アクション → `ddd-improvement-plan.md`
6. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/02_evaluation/ddd-strategic-evaluation.md` | 境界コンテキスト、ユビキタス言語、コンテキストマップの評価 |
| `reports/02_evaluation/ddd-tactical-evaluation.md` | エンティティ、値オブジェクト、集約、リポジトリの評価 |
| `reports/02_evaluation/ddd-pattern-analysis.md` | パターン適用状況分析 |
| `reports/02_evaluation/ddd-improvement-plan.md` | 改善計画 |

中間状態: `work/{project}/investigation/ddd-evaluation/` 配下

## 関連スキル

- 前提: [/analyze-system](analyze-system.md)
- 次のフェーズ: [/integrate-evaluations](integrate-evaluations.md)
