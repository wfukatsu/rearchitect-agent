# /review-scalardb — ScalarDBレビュー

**カテゴリ**: Design（設計） | **Phase 5/8**

ScalarDB関連の設計およびコードをレビューし、品質・整合性・ベストプラクティス準拠を検証します。

## 使用方法

```bash
# 設計レビュー
/review-scalardb --mode=design

# コードレビュー
/review-scalardb --mode=code
```

## 2つのモード

### Mode A: 設計レビュー (`--mode=design`)

ScalarDB設計ドキュメントの品質を検証します。

**必須入力:**
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`）
- `reports/03_design/scalardb-*.md` のいずれか（`/design-scalardb` or `/design-scalardb-app-patterns`）

**レビュー観点:**
- エディション設定との整合性
- スキーマ設計のベストプラクティス
- トランザクション設計の適切さ
- パフォーマンス最適化の考慮

### Mode B: コードレビュー (`--mode=code`)

生成されたScalarDB/Spring Bootコードの品質を検証します。

**必須入力:**
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`）
- `generated/{service}/`（`/generate-scalardb-code`）

**レビュー観点:**
- コーディングパターンの遵守
- エディション別API使用の正確さ
- 例外処理の適切さ
- トランザクション管理の正確さ

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/scalardb-design-review.md` | 設計レビュー結果（Mode A） |
| `reports/03_design/scalardb-code-review.md` | コードレビュー結果（Mode B） |

## 関連スキル

- 前提: [/select-scalardb-edition](select-scalardb-edition.md), [/design-scalardb](design-scalardb.md), [/generate-scalardb-code](generate-scalardb-code.md)
