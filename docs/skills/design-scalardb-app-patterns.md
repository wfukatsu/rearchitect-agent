# /design-scalardb-app-patterns — ScalarDBアプリケーション設計パターン

**カテゴリ**: Design（設計） | **Phase 4.8**

ドメインタイプ判別に基づいて、ScalarDBを使用するアプリケーションの設計パターン・データモデリング・DB選定・スキーマ設計を行います。

## 使用方法

```bash
/design-scalardb-app-patterns ./path/to/source
```

## 前提条件

### 必須
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition` の出力）

### 推奨
- `reports/03_design/bounded-contexts-redesign.md`（`/ddd-redesign`）
- `reports/03_design/aggregate-redesign.md`
- `reports/03_design/context-map.md`
- `reports/01_analysis/ubiquitous-language.md`

## 実行ステップ

1. **前提条件検証 + Context7取得** — エディション設定確認、ScalarDB最新パターン取得
2. **非機能要件の確認** — スループット、レイテンシ、データボリュームを対話形式で確認
3. **ドメインタイプ判別** — 各コンテキストを2軸（ビジネス構造 × サービス境界）で分類
4. **設計パターン選択** — ドメインタイプに応じたパターン:
   - Pipeline × Process → Event Sourcing + CQRS
   - Blackboard × Master → 共有データモデル + 楽観ロック
   - Dialogue × Integration → Saga + 状態マシン
5. **ストレージバックエンド推奨** — エディション制約・要件に基づく各コンテキストの最適ストレージ選定 → `scalardb-database-selection.md`
6. **ScalarDBスキーマ設計** — Namespace/テーブル/キー設計
7. **リポジトリ実装パターン** — エディション別（Core API / SQL Interface / Spring Data JDBC）→ `scalardb-app-patterns.md`
8. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/scalardb-app-patterns.md` | ドメインタイプ別設計パターン、スキーマ設計、リポジトリ実装パターン |
| `reports/03_design/scalardb-database-selection.md` | コンテキスト別ストレージ選定、Multi-Storage構成 |

## 関連スキル

- 前提: [/select-scalardb-edition](select-scalardb-edition.md)
- 次のフェーズ: [/design-scalardb](design-scalardb.md), [/generate-scalardb-code](generate-scalardb-code.md)
