# /evaluate-mmi — MMI評価（4軸定性）

**カテゴリ**: Evaluation（評価） | **Phase 2a**

Modularity Maturity Index（MMI）による4軸のモジュール成熟度評価を実施します。マイクロサービス移行準備度を判定する手動定性評価です。

## 使用方法

```bash
/evaluate-mmi ./path/to/source
```

## 前提条件

- **必須**: 対象コードベースへのアクセス
- **推奨**: `reports/01_analysis/system-overview.md`（`/analyze-system` の出力）
- **推奨**: `reports/01_analysis/ubiquitous-language.md`（`/analyze-system` の出力）

## 評価軸

| 軸 | 重み | 評価観点 |
|----|------|----------|
| **Cohesion（凝集度）** | 30% | 単一責任原則の遵守度、機能的凝集度 |
| **Coupling（結合度）** | 30% | 他モジュールへの依存度、インターフェースの明確さ |
| **Independence（独立性）** | 20% | 独立デプロイ・スケーリング可能性 |
| **Reusability（再利用性）** | 20% | 他ドメインでの再利用可能性 |

### スコア計算

```
MMI = (0.3 × Cohesion + 0.3 × Coupling + 0.2 × Independence + 0.2 × Reusability) / 5 × 100
```

| スコア | レベル | 意味 |
|--------|--------|------|
| 80-100 | High | マイクロサービス化準備完了 |
| 60-80 | Medium | 軽微なリファクタリングで移行可能 |
| 40-60 | Low-Medium | 大幅なリファクタリングが必要 |
| 0-40 | Immature | 全面再設計が必要 |

## 実行ステップ

1. **前提条件の検証** — 分析結果ファイルの存在確認
2. **モジュール抽出** — パッケージ/名前空間/クラス/サービス単位でモジュールを特定
3. **各軸の評価** — Cohesion/Coupling/Independence/Reusability を各5点満点で評価
4. **スコア集計** — 全体MMIスコアとモジュール別スコアを算出
5. **改善計画策定** — Quick Wins / 短期 / 中期 / 長期の改善アクションを定義

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/02_evaluation/mmi-overview.md` | 評価概要サマリー（全体スコア、レーダーチャート） |
| `reports/02_evaluation/mmi-by-module.md` | モジュール別詳細評価 |
| `reports/02_evaluation/mmi-improvement-plan.md` | 改善計画（フェーズ別アクション） |

## 関連スキル

- 前提: [/analyze-system](analyze-system.md)
- 関連: [/mmi-analyzer](mmi-analyzer.md)（Lilienthal 3軸の自動定量評価）
- 次のフェーズ: [/integrate-evaluations](integrate-evaluations.md)
