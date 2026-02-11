# /system-investigation — システム調査

**カテゴリ**: Investigation（調査） | **Phase 0**

対象システムのコードベースを分析し、技術スタック・構造・問題点・DDD適合性を調査します。全パイプラインの出発点となるスキルです。

## 使用方法

```bash
/system-investigation ./path/to/source
```

## 前提条件

- **必須**: 対象システムのソースコードにアクセス可能
- **推奨**: Serena MCP が利用可能（Javaシンボル解析の精度向上）

## 実行ステップ

1. **プロジェクト名の特定** — ディレクトリ名やビルド設定から推定
2. **技術スタック調査** — 言語、フレームワーク、ライブラリ、ビルドツール → `technology-stack.md`
3. **構造分析** — パッケージ構造、レイヤリング、モジュール分割 → `codebase-structure.md`
4. **問題点特定** — 技術的負債、コードスメル、セキュリティ懸念 → `issues-and-debt.md`
5. **DDD適合性評価** — ドメイン分離度、ユビキタス言語の使用状況 → `ddd-readiness.md`
6. **調査レポートの統合** — 全結果をまとめた調査サマリー → `investigation-summary.md`
7. **Mermaid図の検証** — `/fix-mermaid` で生成図を検証

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/before/{project}/technology-stack.md` | 技術スタック一覧 |
| `reports/before/{project}/codebase-structure.md` | コードベース構造分析 |
| `reports/before/{project}/issues-and-debt.md` | 問題点・技術的負債 |
| `reports/before/{project}/ddd-readiness.md` | DDD適合性評価 |
| `reports/before/{project}/investigation-summary.md` | 調査サマリー |

中間状態: `work/{project}/investigation/` 配下

## 関連スキル

- 次のフェーズ: [/analyze-system](analyze-system.md), [/security-analysis](security-analysis.md)
