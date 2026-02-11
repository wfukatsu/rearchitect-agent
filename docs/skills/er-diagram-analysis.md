# /er-diagram-analysis — ER図分析

**カテゴリ**: Investigation（調査） | **Phase 1.5c**

現行システムのER図をMermaid形式で生成し、エンティティ・リレーションシップ・カーディナリティを可視化します。

## 使用方法

```bash
/er-diagram-analysis ./path/to/source
```

## 前提条件

- **必須**: 対象コードベースへのアクセス
- **推奨**: `reports/01_analysis/data-model-analysis.md`（`/data-model-analysis` の出力）
- **推奨**: `reports/01_analysis/db-design-analysis.md`（`/db-design-analysis` の出力）

## 実行ステップ

1. **入力情報の収集** — 前提ファイル、ORM定義、DDL、設計書から情報を収集
2. **エンティティの整理** — 主キー、外部キー、制約の整理
3. **ER図の生成** — Mermaid `erDiagram` 形式で全体ER図とドメイン別ER図を生成
4. **分析レポートの作成** — エンティティカタログ、関連分析、マイクロサービス分割への示唆
5. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/01_analysis/er-diagram-current.md` | 全体ER図、ドメイン別ER図、エンティティカタログ、関連分析 |

## オプション

| フラグ | 説明 |
|--------|------|
| `--max-entities=N` | エンティティ数制限（大規模システム用） |
| `--domain=Name` | 特定ドメインのみER図生成 |

## 関連スキル

- 前提: [/data-model-analysis](data-model-analysis.md), [/db-design-analysis](db-design-analysis.md)
