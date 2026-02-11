# /db-design-analysis — DB設計分析

**カテゴリ**: Investigation（調査） | **Phase 1.5b**

既存のデータベース設計を分析し、テーブル定義・インデックス設計・制約・正規化状態・問題点を抽出します。

## 使用方法

```bash
/db-design-analysis ./path/to/source
```

## 前提条件

- **推奨**: `reports/01_analysis/data-model-analysis.md`（`/data-model-analysis` の出力）
- **推奨**: `reports/before/{project}/technology-stack.md`（`/system-investigation` の出力）

前提ファイルがなくてもコードから直接分析可能です。

## 実行ステップ

1. **データベース関連ソースの特定** — DDL、マイグレーション、ORM設定の検索
2. **テーブル定義の抽出** — カラム名、型、制約、デフォルト値の一覧化
3. **インデックス設計の分析** — インデックスの妥当性、不足・冗長なインデックス
4. **正規化状態の分析** — 1NF〜3NF/BCNFへの適合度判定
5. **問題点と改善提案** — パフォーマンス問題、整合性リスクの特定
6. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/01_analysis/db-design-analysis.md` | テーブル定義書、インデックス分析、正規化分析、テーブル関連図、改善提案 |

## 関連スキル

- 前提: [/data-model-analysis](data-model-analysis.md)
- 関連: [/er-diagram-analysis](er-diagram-analysis.md)
