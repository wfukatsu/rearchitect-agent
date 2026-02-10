---
name: mmi-analyzer
user_invocable: true
description: >
  Modularity Maturity Index (MMI) によるソフトウェアアーキテクチャの技術的負債を定量評価するスキル。
  Pythonプロジェクトのソースコードを解析し、モジュール性・階層性・パターン一貫性の3軸でスコアリングする。
  Serena MCP のLSP機能と組み合わせることで、シンボルレベルの依存関係解析やレイヤー違反検出の精度が向上する。
  
  このスキルは以下のような場面で使用する:
  - 「アーキテクチャを評価して」「技術的負債を測定して」と言われたとき
  - 「MMI」「モジュール性」「循環依存」「レイヤー違反」に言及されたとき
  - Pythonプロジェクトのコード品質やリファクタリング優先度を判断したいとき
  - レガシーシステムのリファクタリング vs 置き換えの判断材料が必要なとき
  - 「Serenaで解析して」と言われたとき（Serena MCPとの連携を前提とする）
---

# MMI Analyzer — Modularity Maturity Index 評価スキル

Dr. Carola Lilienthal の MMI (Modularity Maturity Index) に基づき、Pythonプロジェクトのアーキテクチャ品質を0〜10で定量評価する。

## 概要

MMIは3つのカテゴリの加重合計で算出される:

| カテゴリ | 重み | 主な評価対象 |
|---------|------|------------|
| Modularity（モジュール性） | 45% | モジュール分割、インターフェース、プロポーション |
| Hierarchy（階層性） | 30% | レイヤー違反、循環依存 |
| Pattern Consistency（パターン一貫性） | 25% | パターン適用率、DDD分離 |

### スコアの解釈

- **8〜10**: 技術的負債が少ない。保守コスト安定。
- **4〜8**: 要リファクタリング。段階的改善を推奨。
- **0〜4**: 保守困難。リファクタリング or システム置換の判断が必要。

## 前提条件

**環境:**
- Python 3.9+
- radon, networkx パッケージ (`pip install radon networkx`)

**必須:**
- 対象Pythonプロジェクトのソースコードにアクセス可能であること

**推奨:**
- Serena MCPが設定済みであること（シンボルレベル解析の精度向上）

## 出力先

結果は `reports/02_evaluation/` に出力します。
中間データ: `metrics_result.json`, `architecture_result.json`, `mmi_result.json`
**重要**: 各ステップ完了時に即座にファイルを出力してください。

## 3つのツール

本スキルは3つのPythonスクリプトで構成される。各ツールは独立して実行可能だが、Tool 3（MMI Calculator）が全体を統合する。

### Tool 1: Metrics Analyzer (`scripts/metrics_analyzer.py`)

コードメトリクスを自動計測する。MMI基準の 1.3（プロポーション）と 2.2（循環依存）をカバー。

```bash
pip install radon networkx --break-system-packages
python scripts/metrics_analyzer.py /path/to/project
```

**計測項目:**
- クラス/メソッドのLOC分布 → 大クラス・大メソッドの割合
- 循環的複雑度（Cyclomatic Complexity）→ 高複雑度メソッドの割合
- パッケージ（ディレクトリ）内クラス数分布
- import解析による循環依存検出（クラスレベル・パッケージレベル）
- モジュールサイズ比 `(LoC max / LoC min) / 数`

**出力:** `metrics_result.json`

### Tool 2: Architecture Analyzer (`scripts/architecture_analyzer.py`)

アーキテクチャ構造を解析する。MMI基準の 1.1（モジュール化）、1.2（インターフェース）、2.1（レイヤー違反）、3.1-3.2（パターン）をカバー。

```bash
python scripts/architecture_analyzer.py /path/to/project [--config architecture.json]
```

**解析項目:**
- ディレクトリ構造からドメインモジュール・技術レイヤーを推定
- ソースコードの各モジュール/レイヤーへの割当率
- レイヤー間の依存方向を解析し違反（逆方向参照）を検出
- パターン（Repository, Service, Controller 等）の適用率

**設定ファイル（任意）:** `architecture.json` でターゲットアーキテクチャを定義できる。
詳細は `references/architecture_config.md` を参照。

**出力:** `architecture_result.json`

### Tool 3: MMI Calculator (`scripts/mmi_calculator.py`)

Tool 1, 2 の結果とレビュアー入力を統合してMMIスコアを算出する。

```bash
python scripts/mmi_calculator.py \
  --metrics metrics_result.json \
  --architecture architecture_result.json \
  [--reviewer reviewer_input.json]
```

**処理:**
1. `references/mmi_scoring_table.md` のスコアリング閾値に基づき各基準を0〜10に変換
2. レビュアー判断が必要な基準はデフォルト5（partial）、`reviewer_input.json` で上書き可能
3. カテゴリ別平均 × 重み → 最終MMIスコア算出
4. Markdownレポートを生成

**出力:** `mmi_report.md`, `mmi_scores.json`

## 実行手順

### Step 1: 依存関係のインストール

```bash
pip install radon networkx --break-system-packages
```

### Step 2: メトリクス解析

```bash
python scripts/metrics_analyzer.py /path/to/project
```

### Step 3: アーキテクチャ解析

```bash
python scripts/architecture_analyzer.py /path/to/project
```

必要に応じて `architecture.json` を作成し、ターゲットアーキテクチャ（レイヤー順序、ドメインモジュール名など）を定義する。

### Step 4: MMI算出

```bash
python scripts/mmi_calculator.py \
  --metrics metrics_result.json \
  --architecture architecture_result.json
```

### Step 5: レポート確認

生成された `mmi_report.md` を確認し、ユーザーに提示する。

## Serena MCP との連携

Serena MCP が利用可能な場合、以下の機能で解析精度が大幅に向上する:

- **find_references**: 実際の参照関係に基づく結合度分析（importだけでは検出できない動的な依存を補完）
- **type_hierarchy**: 継承階層の完全な把握
- **call_hierarchy**: 呼び出し関係の追跡によるレイヤー違反の精密検出
- **document_symbols / workspace_symbols**: モジュール構造の正確な把握

Serena連携の詳細は `references/serena_integration.md` を参照。

## レビュアー入力

自動計測できない基準（1.1.5, 1.1.6, 1.2.2, 3.3, 3.4）はレビュアー判断が必要。
`reviewer_input.json` で以下の形式で入力する:

```json
{
  "1.1.5_clear_responsibilities": 5,
  "1.1.6_mapping_quality": 5,
  "1.2.2_interface_mapping": 5,
  "3.3_explicit_pattern_mapping": 5,
  "3.4_domain_technical_separation": 5
}
```

値は 0（No）, 5（partial）, 10（Yes）のいずれか。
ユーザーにインタラクティブに確認して入力するのが望ましい。

## スコアリング詳細

各基準の閾値テーブルは `references/mmi_scoring_table.md` に記載。
