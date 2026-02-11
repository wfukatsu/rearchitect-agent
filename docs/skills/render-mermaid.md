# /render-mermaid — Mermaidレンダリング

**カテゴリ**: Utility（ユーティリティ）

Mermaid CLI（mmdc）を使用してMermaid図をPNG/SVG/PDF画像ファイルに変換します。

## 使用方法

```bash
/render-mermaid ./reports/
```

## 前提条件

### Mermaid CLIのインストール

```bash
# npmでインストール
npm install -g @mermaid-js/mermaid-cli

# 確認
mmdc --version
```

## 機能

1. **単一ファイル変換** — `.mmd` ファイルを PNG/SVG/PDF に変換
2. **Markdown内図変換** — Markdown内の ` ```mermaid ` ブロックを画像に抽出・変換
3. **一括変換** — ディレクトリ内の全Mermaid図を一括変換
4. **エラー検出** — シンタックスエラーの検出と報告

## 出力形式

| 形式 | 用途 |
|------|------|
| **PNG** | ドキュメント埋め込み、プレゼンテーション |
| **SVG** | Web表示、スケーラブル |
| **PDF** | 印刷、アーカイブ |

## オプション

| フラグ | 説明 |
|--------|------|
| `--format=png` | 出力形式の指定（デフォルト: png） |
| `--theme=dark` | ダークテーマの使用 |
| `--width=1200` | 出力幅の指定 |

## 関連スキル

- 補完: [/fix-mermaid](fix-mermaid.md)（レンダリング前のエラー修正）
- 統合: [/compile-report](compile-report.md)（HTMLレポートでのインライン表示）
