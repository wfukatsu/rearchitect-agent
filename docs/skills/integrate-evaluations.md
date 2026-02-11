# /integrate-evaluations — 評価統合

**カテゴリ**: Evaluation（評価） | **Phase 2.5**

MMI評価とDDD評価の結果を統合し、相関分析と優先度付き改善計画を策定します。

## 使用方法

```bash
/integrate-evaluations ./path/to/source
```

## 前提条件

### 必須（すべて必要）
- `reports/02_evaluation/mmi-overview.md`（`/evaluate-mmi` の出力）
- `reports/02_evaluation/mmi-by-module.md`
- `reports/02_evaluation/mmi-improvement-plan.md`
- `reports/02_evaluation/ddd-strategic-evaluation.md`（`/ddd-evaluation` の出力）
- `reports/02_evaluation/ddd-tactical-evaluation.md`
- `reports/02_evaluation/ddd-improvement-plan.md`

### 推奨
- `reports/01_analysis/ubiquitous-language.md`
- `reports/01_analysis/domain-code-mapping.md`

## 実行ステップ

1. **前提条件の検証** — 必須6ファイルの存在確認
2. **評価結果の読み込み** — MMI/DDD両評価結果を読み込み
3. **相関分析** — MMIスコアとDDD適合度の相関を分析 → `integrated-evaluation.md`
4. **優先度マトリクスの作成** — 改善項目を影響度×実装難易度でマッピング → `priority-matrix.md`
5. **統合改善計画の策定** — 統一的な改善ロードマップ → `unified-improvement-plan.md`
6. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/02_evaluation/integrated-evaluation.md` | MMI×DDD相関分析 |
| `reports/02_evaluation/priority-matrix.md` | 優先度マトリクス（影響度×難易度） |
| `reports/02_evaluation/unified-improvement-plan.md` | 統合改善計画（ロードマップ） |

## 関連スキル

- 前提: [/evaluate-mmi](evaluate-mmi.md), [/ddd-evaluation](ddd-evaluation.md)
- 次のフェーズ: [/ddd-redesign](ddd-redesign.md)
