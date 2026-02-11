# /compile-report — レポートコンパイル

**カテゴリ**: Utility（ユーティリティ） | **Phase 13**

分析結果のMarkdownファイルを統合HTMLレポートに変換します。

## 使用方法

```bash
/compile-report
```

## 前提条件

- `reports/` 配下にMarkdownファイルが存在すること
- Python 3.9+（HTMLコンパイル用）

## 機能

1. **Markdownの自動検出・統合** — 各ディレクトリ内のすべてのMarkdownファイルを動的に検出
2. **設定ファイルの表示** — YAML/JSON/Properties/TOML等をシンタックスハイライト付きで表示
3. **Mermaid図のレンダリング** — Mermaid図をインラインで埋め込み
4. **GraphDB可視化** — D3.jsインタラクティブグラフを埋め込み
5. **目次生成** — サイドバー目次を自動生成
6. **スタイリング** — ライト/ダークテーマ対応
7. **レスポンシブ** — モバイル/印刷対応
8. **重複除去** — 命名規則が異なる重複ファイルを自動除去
9. **HTML検証・自動修正** — 各セクションの表示を検証
10. **XSSサニタイゼーション** — 危険なHTMLタグを自動エスケープ

## 出力形式

| 形式 | 推奨用途 |
|------|---------|
| **単一HTML** | ブラウザで直接閲覧、メール添付 |
| **Nextra** | Next.jsベースの静的サイト |

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/00_summary/report.html` | 統合HTMLレポート |

## 使用例

```bash
# 基本的な使い方
/compile-report

# Nextra形式で生成
python scripts/compile_report.py --input-dir ./reports --format nextra
```

## 関連スキル

- 前提: 各フェーズのスキルが `reports/` にMarkdownを出力済み
- 補完: [/render-mermaid](render-mermaid.md)（Mermaid図の画像変換）
- 補完: [/visualize-graph](visualize-graph.md)（D3.jsグラフの事前生成）
