# /mmi-analyzer — MMI自動定量評価（Lilienthal 3軸）

**カテゴリ**: Evaluation（評価） | **Phase 2（代替）**

Dr. Carola Lilienthal の手法に基づき、Pythonプロジェクトのアーキテクチャ品質を自動的に定量評価します。Pythonスクリプトで自動計測するため、再現性の高い評価が可能です。

## 使用方法

```bash
/mmi-analyzer ./path/to/python-project
```

## 前提条件

- **必須**: Python 3.9+、対象Pythonプロジェクトのソースコード
- **推奨**: `radon`, `networkx` パッケージ
- **推奨**: Serena MCP が設定済み

> **注意**: このスキルはPythonプロジェクト専用です。Javaプロジェクトには `/evaluate-mmi` を使用してください。

## 評価軸

| カテゴリ | 重み | 主な評価対象 |
|---------|------|------------|
| **Modularity（モジュール性）** | 45% | モジュール分割、インターフェース、プロポーション |
| **Hierarchy（階層性）** | 30% | レイヤー違反、循環依存 |
| **Pattern Consistency（パターン一貫性）** | 25% | パターン適用率、DDD分離 |

### スコア計算

```
MMI = Modularity × 0.45 + Hierarchy × 0.30 + Pattern × 0.25
```

| スコア | レベル | 意味 |
|--------|--------|------|
| 8-10 | Good | 技術的負債が少ない |
| 4-8 | Warning | 段階的リファクタリングを推奨 |
| 0-4 | Critical | リファクタリング vs 置換の判断が必要 |

## 実行ステップ

1. **依存関係のインストール** — `radon`, `networkx` の確認
2. **メトリクス解析**（Tool 1: Metrics Analyzer） — 循環複雑度、行数、依存関係を自動計測
3. **アーキテクチャ解析**（Tool 2: Architecture Analyzer） — レイヤー違反、循環依存を検出
4. **MMI算出**（Tool 3: MMI Calculator） — 閾値テーブルに基づくスコアリング
5. **レポート確認** — 結果を `reports/02_evaluation/` に出力

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/02_evaluation/mmi_report.md` | MMI評価レポート |
| `reports/02_evaluation/mmi_scores.json` | スコアデータ（JSON） |

中間ファイル: `metrics_result.json`, `architecture_result.json`, `mmi_result.json`

## オプション

| フラグ | 説明 |
|--------|------|
| `--config` | `architecture.json` でターゲットアーキテクチャを定義 |
| `--reviewer` | `reviewer_input.json` でレビュアー判断を入力 |

## 関連スキル

- 関連: [/evaluate-mmi](evaluate-mmi.md)（4軸定性評価、言語非依存）
- 次のフェーズ: [/integrate-evaluations](integrate-evaluations.md)
