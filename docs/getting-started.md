# クイックスタートガイド

このガイドでは、architecture-redesign-agent のセットアップから初回実行、結果の確認方法までを説明します。

## 前提条件

### 必須

| ツール | 用途 | インストール確認 |
|--------|------|-----------------|
| **Claude Code** | エージェント実行環境 | `claude --version` |
| **Python 3.9+** | グラフ構築・レポート生成 | `python3 --version` |
| **Node.js 18+** | Mermaid図レンダリング | `node --version` |

### 推奨

| ツール | 用途 | インストール確認 |
|--------|------|-----------------|
| **Serena MCP** | シンボルレベルのJavaコード解析 | `.serena/project.yml` の存在 |
| **Graphviz** | DOT形式のグラフ描画 | `dot -V` |

## セットアップ

### 1. リポジトリ取得

```bash
git clone <repository-url>
cd architecture-redesign-agent
```

### 2. Python依存パッケージのインストール

```bash
# venv推奨
python3 -m venv .venv
source .venv/bin/activate

# 必要パッケージをインストール
pip install ryugraph pandas markdown pymdown-extensions radon networkx
```

### 3. Mermaid CLIのインストール

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version  # 動作確認
```

### 4. Serena MCPの設定（推奨）

Javaプロジェクトを分析する場合、`.serena/project.yml` にプロジェクト設定が必要です。
設定済みであればClaude Codeが自動的にSerenaを利用します。

## 最初の実行

### 方法1: 対話的に実行する（推奨）

`/workflow` を使うと、実行したい処理を対話的に選択できます。

```bash
/workflow ./path/to/source
```

以下のような選択肢が表示されます：

1. **完全パイプライン実行** — 調査から設計・コード生成まで全フェーズ一括
2. **分析・評価まで実行** — Phase 0-2（調査→分析→MMI/DDD評価→統合）
3. **設計から実行** — Phase 3-8（DDD再設計→ScalarDB設計→実装→コード生成）
4. **個別フェーズ選択** — 全フェーズから個別に選択

初回は「分析・評価まで実行」がおすすめです。短時間で現行システムの全体像を把握できます。

### 方法2: 全フェーズを一括実行する

```bash
/full-pipeline ./path/to/source
```

Phase 0（調査）からPhase 13（エグゼクティブサマリー）まで、26以上のフェーズを順番に自動実行します。
対象コードベースの規模にもよりますが、完了まで時間がかかります。

### 方法3: 分析のみ実行する

```bash
/refactor-system ./path/to/source
```

コード生成を行わず、分析・設計までを実行します。

## 出力結果の確認

### ディレクトリ構造

実行が完了すると、`reports/` ディレクトリに成果物が生成されます。

```
reports/
├── before/{project}/     ← Phase 0: システム調査結果
├── 00_summary/           ← エグゼクティブサマリー
├── 01_analysis/          ← Phase 1: ユビキタス言語、ドメイン分析
├── 02_evaluation/        ← Phase 2: MMI・DDD評価
├── 03_design/            ← Phase 3-5: アーキテクチャ設計
│   └── api-specifications/  ← API仕様書
├── 04_stories/           ← ドメインストーリー
├── 05_estimate/          ← コスト見積もり
├── 06_implementation/    ← 実装仕様
├── 07_test-specs/        ← テスト仕様
├── 08_infrastructure/    ← インフラ構成
└── graph/                ← ナレッジグラフ
    ├── data/             ← CSV形式の中間データ
    └── visualizations/   ← Mermaid/DOT/HTML可視化

generated/                ← 生成されたSpring Bootコード
├── {service}/            ← サービスごとのソースコード
└── infrastructure/       ← IaC・K8sマニフェスト
```

### HTMLレポートの確認

全レポートを統合HTMLで閲覧できます：

```bash
/compile-report
open reports/00_summary/full-report.html  # macOS
```

### ナレッジグラフの可視化

インタラクティブなグラフビューアで関係性を確認できます：

```bash
/visualize-graph
open reports/graph/visualizations/graph.html  # macOS
```

### 個別レポートの確認

重要なレポートファイル：

| ファイル | 内容 |
|---------|------|
| `reports/00_summary/executive-summary.md` | 全体サマリー |
| `reports/01_analysis/ubiquitous-language.md` | ユビキタス言語辞書 |
| `reports/01_analysis/actors-roles-permissions.md` | アクター・ロール一覧 |
| `reports/02_evaluation/mmi-overview.md` | モジュール成熟度評価 |
| `reports/03_design/bounded-contexts.md` | 境界コンテキスト設計 |
| `reports/03_design/target-architecture.md` | ターゲットアーキテクチャ |

## 中断と再開

パイプラインが途中で中断した場合、`--resume-from` で再開できます。

```bash
# 進捗状態の確認
cat work/{project}/pipeline-progress.json

# Phase 6から再開
/full-pipeline ./path/to/source --resume-from=phase-6
```

## 特定フェーズのみ実行

個別のスキルを直接呼び出すこともできます。

```bash
# システム調査のみ
/system-investigation ./path/to/source

# MMI評価のみ
/evaluate-mmi ./path/to/source

# DDD再設計のみ
/ddd-redesign ./path/to/source
```

全スキル一覧は [スキルリファレンス](skill-reference.md) を参照してください。

## よくある質問

### Q: 対象言語は何に対応していますか？

主にJavaプロジェクトを対象としています。Serena MCPがJavaのシンボルレベル解析に対応しており、最も精度が高くなります。ただし、スキルの多くはソースコードの一般的なパターン認識に基づいているため、他の言語のプロジェクトでも基本的な分析は可能です。

### Q: ScalarDBを使わないプロジェクトでも使えますか？

はい。ScalarDB関連のフェーズ（Phase 4.7〜5.9, 8）は `--skip-*` オプションでスキップできます。DDD分析・設計のフェーズはScalarDBに依存しません。

### Q: 出力ファイルはGitにコミットすべきですか？

`reports/`、`generated/`、`work/`、`knowledge.ryugraph` はすべて `.gitignore` に設定済みです。分析結果は再実行で生成できるため、通常はコミット不要です。

### Q: 実行にどのくらい時間がかかりますか？

コードベースの規模とフェーズ数によりますが、`/full-pipeline` の全フェーズ実行で小〜中規模プロジェクトの場合、数十分程度です。

### Q: エラーが発生した場合はどうすればいいですか？

[高度な使い方 - トラブルシューティング](advanced-usage.md#トラブルシューティング) セクションを参照してください。
