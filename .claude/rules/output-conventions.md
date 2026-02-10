# 出力規則

スキルが `reports/` にファイルを出力する際の共通ルール。

## ディレクトリ構造

```
reports/
├── before/{project}/     # Phase 0: 調査（/system-investigation）
├── 00_summary/           # エグゼクティブサマリー（/compile-report）
├── 01_analysis/          # Phase 1: 分析（/analyze-system）
├── 02_evaluation/        # Phase 2: 評価（/evaluate-mmi, /ddd-evaluation, /integrate-evaluations）
├── 03_design/            # Phase 3-5: 設計（/ddd-redesign, /design-*）
│   └── api-specifications/  # API仕様書（/design-api）
├── 04_stories/           # ドメインストーリー（/create-domain-story）
├── 05_estimate/          # コスト見積もり（/estimate-cost）
├── 06_implementation/    # 実装仕様（/design-implementation）
├── 07_test-specs/        # テスト仕様（/generate-test-specs）
├── 08_infrastructure/    # インフラ構成（/design-infrastructure）
├── graph/                # ナレッジグラフ（/build-graph, /visualize-graph）
│   ├── data/             # CSV データ
│   └── visualizations/   # 可視化出力
└── sizing-estimates/     # サイジング見積もり（/scalardb-sizing-estimator）

generated/infrastructure/    # IaC & K8s manifests（/design-infrastructure）
├── k8s/                     # Kubernetes manifests (Kustomize base + overlays)
├── terraform/               # Terraform modules & environments
└── openshift/               # OpenShift configs（選択時のみ）
```

## ファイル命名規則

- **小文字ケバブケース**: `ubiquitous-language.md`, `mmi-overview.md`
- **フェーズプレフィックス不要**: ディレクトリで区別するため
- **サフィックスルール**:
  - 分析結果: `-analysis.md`
  - 評価結果: `-evaluation.md`
  - 設計: `-design.md` / `-architecture.md`
  - 仕様: `-specs.md`

## Markdown フロントマター

各出力ファイルの先頭に付与:

```yaml
---
title: ドキュメントタイトル
phase: "Phase 2: Evaluation"
skill: evaluate-mmi
generated_at: 2025-01-20T10:30:00Z
input_files:
  - reports/01_analysis/ubiquitous-language.md
  - reports/01_analysis/domain-code-mapping.md
---
```

## 即時出力ルール

**重要**: 各ステップ完了時に即座にファイルを出力すること。全ステップ完了後にまとめて出力してはいけない。
これにより、パイプラインの途中で中断しても途中成果物が残る。

## Mermaid図を含む場合

- `.claude/rules/mermaid-best-practices.md` のルールに従う
- 図は対応するMarkdownファイル内にインラインで記述（別ファイルにしない）
