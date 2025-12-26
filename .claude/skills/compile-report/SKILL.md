---
name: compile-report
description: レポートコンパイルエージェント - 分析結果のMarkdownファイルを統合HTMLレポートに変換。/compile-report [出力パス] で呼び出し。
user_invocable: true
---

# Report Compiler Agent

分析結果のMarkdownファイルを統合HTMLレポートに変換するエージェントです。

## 目的

このエージェントは以下の機能を提供します：

1. **Markdownの統合** - 複数のMarkdownファイルを1つのHTMLに統合
2. **Mermaid図のレンダリング** - Mermaid図をSVGとしてインライン埋め込み
3. **目次生成** - 自動的に目次を生成
4. **スタイリング** - プロフェッショナルなスタイルを適用
5. **PDF出力** - 印刷用のPDF出力（オプション）

## 前提条件

- Python 3.9+
- markdown パッケージ
- （オプション）mermaid-cli（Mermaid図のレンダリング用）

## 実行プロンプト

あなたはレポートをコンパイルする専門家エージェントです。以下の手順でHTMLレポートを生成してください。

### Step 1: 環境確認

```bash
# 必要なパッケージの確認
source .venv/bin/activate
pip install markdown pymdown-extensions
```

### Step 2: レポートコンパイルスクリプトの実行

```bash
source .venv/bin/activate && python scripts/compile_report.py \
  --input-dir ./reports \
  --output ./reports/00_summary/full-report.html \
  --title "Scalar Auditor for BOX - リファクタリング分析レポート"
```

### Step 3: 出力形式

#### 統合HTMLレポート

```html
<!DOCTYPE html>
<html>
<head>
    <title>リファクタリング分析レポート</title>
    <style>/* プロフェッショナルスタイル */</style>
</head>
<body>
    <nav><!-- 目次 --></nav>
    <main>
        <section id="summary"><!-- エグゼクティブサマリー --></section>
        <section id="analysis"><!-- 分析結果 --></section>
        <section id="evaluation"><!-- MMI評価 --></section>
        <section id="design"><!-- 設計書 --></section>
        <section id="stories"><!-- ドメインストーリー --></section>
    </main>
</body>
</html>
```

### Step 4: コマンドオプション

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| `--input-dir` | 入力ディレクトリ | ./reports |
| `--output` | 出力HTMLファイル | ./reports/full-report.html |
| `--title` | レポートタイトル | Analysis Report |
| `--theme` | テーマ (light/dark) | light |
| `--toc` | 目次を生成 | true |
| `--mermaid` | Mermaid図をレンダリング | true |
| `--pdf` | PDF出力も生成 | false |

## 出力ファイル

```
reports/
└── 00_summary/
    ├── full-report.html   # 統合HTMLレポート
    └── full-report.pdf    # PDF版（オプション）
```

## 使用例

### 例1: 基本的なコンパイル

```bash
/compile-report
```

### 例2: カスタムタイトルとダークテーマ

```bash
/compile-report --title "My Project Report" --theme dark
```

### 例3: PDF出力も生成

```bash
/compile-report --pdf
```

## 関連スキル

- `/render-mermaid` - Mermaid図を画像に変換
- `/visualize-graph` - GraphDBを可視化
