---
description: レポートコンパイルエージェント - 分析結果のMarkdownファイルを統合HTMLレポートに変換。
argument-hint: [出力パス]
---

# レポートコンパイルエージェント

分析結果のMarkdownファイルを統合HTMLレポートに変換します。

## 使用方法

```bash
# 基本的なコンパイル
/compile-report

# カスタム出力先
/compile-report ./output/report.html

# オプション付き
/compile-report --theme dark --pdf
```

## 出力

- **HTML** - プロフェッショナルなスタイルの統合レポート
- **PDF** - 印刷用（オプション）

## オプション

| オプション | 説明 |
|-----------|------|
| `--theme` | light/dark |
| `--toc` | 目次生成 |
| `--pdf` | PDF出力 |

詳細は `.claude/skills/compile-report/SKILL.md` を参照してください。
