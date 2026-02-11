# /data-model-analysis — データモデル分析

**カテゴリ**: Investigation（調査） | **Phase 1.5a**

既存システムのデータモデルを分析し、エンティティ・リレーションシップ・ドメインルールを抽出します。

## 使用方法

```bash
/data-model-analysis ./path/to/source
```

## 前提条件

- **推奨**: `reports/01_analysis/system-overview.md`（`/analyze-system` の出力）
- **推奨**: `reports/01_analysis/domain-code-mapping.md`（`/analyze-system` の出力）

前提ファイルがなくてもコードから直接分析可能です。

## 実行ステップ

1. **データモデル関連ソースの特定** — ORM定義、DDLファイル、エンティティクラスの特定
2. **エンティティの抽出と分類** — DDD観点での分類（Entity/Value Object/Aggregate）
3. **リレーションシップの分析** — エンティティ間の関連とカーディナリティ
4. **ドメインルールの抽出** — バリデーション、ビジネスルール、制約
5. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/01_analysis/data-model-analysis.md` | エンティティ一覧、リレーションシップマップ、ドメインルール、データフロー、改善ポイント |

## 関連スキル

- 前提: [/analyze-system](analyze-system.md)
- 関連: [/db-design-analysis](db-design-analysis.md), [/er-diagram-analysis](er-diagram-analysis.md)
