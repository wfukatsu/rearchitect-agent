# /analyze-system — システム分析

**カテゴリ**: Investigation（調査） | **Phase 1**

既存システムの設計書とコードを分析し、ユビキタス言語・アクター・ロール・ドメイン-コード対応表を抽出します。DDD分析の基盤となる重要なスキルです。

## 使用方法

```bash
/analyze-system ./path/to/source
```

## 前提条件

- **必須**: 対象システムのソースコードにアクセス可能
- **推奨**: `reports/before/{project}/technology-stack.md`（`/system-investigation` の出力）
- **推奨**: `reports/before/{project}/codebase-structure.md`（`/system-investigation` の出力）

## 実行ステップ

1. **入力情報の収集と初期化** — プロジェクトメタデータの作成 → `project_metadata.json`
2. **設計書の解析** — 既存ドキュメントからドメイン知識を収集
3. **コードベースの解析** — Serena MCP/Grep でクラス・メソッド・依存関係を分析 → `system-overview.md`
4. **ユビキタス言語の抽出** — ドメイン用語の辞書を構築 → `ubiquitous-language.md`
5. **アクター・ロール・権限の整理** — システムの利用者と権限体系を整理 → `actors-roles-permissions.md`
6. **ドメイン-コード対応表の作成** — ビジネスドメインとコードの紐付け → `domain-code-mapping.md`
7. **メタデータの最終更新**
8. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/00_summary/project_metadata.json` | プロジェクトメタデータ |
| `reports/01_analysis/system-overview.md` | 現行システム概要 |
| `reports/01_analysis/ubiquitous-language.md` | ユビキタス言語辞書 |
| `reports/01_analysis/actors-roles-permissions.md` | アクター・ロール・権限一覧 |
| `reports/01_analysis/domain-code-mapping.md` | ドメイン-コード対応表 |

## 関連スキル

- 前提: [/system-investigation](system-investigation.md)
- 次のフェーズ: [/evaluate-mmi](evaluate-mmi.md), [/ddd-evaluation](ddd-evaluation.md), [/data-model-analysis](data-model-analysis.md)
