# /select-scalardb-edition — ScalarDBエディション選定

**カテゴリ**: Design（設計） | **Phase 4.5**

対話形式で最適なScalarDBエディション（OSS / Enterprise Standard / Enterprise Premium）を選定し、下流スキルで参照されるエディション設定ファイルを出力します。

## 使用方法

```bash
/select-scalardb-edition
```

> **注意**: このスキルは対象パスの引数を必要としません。スタンドアロンで実行可能です。

## 前提条件

- **必須**: なし
- **推奨**: `reports/03_design/target-architecture.md`（`/design-microservices`）
- **推奨**: `reports/03_design/bounded-contexts-redesign.md`（`/ddd-redesign`）

## 実行ステップ

1. **Context7で最新情報取得** — ScalarDB最新エディション情報をContext7 MCPで取得
2. **要件ヒアリング（対話形式）** — 以下の5項目をAskUserQuestionで収集:
   - Q1: デプロイモデル（組み込み / Cluster / 未定）
   - Q2: API要件（Core Java API / SQL Interface / Spring Data / GraphQL）
   - Q3: 機能要件（Multi-Storage / 2PC / 認証・認可 / Analytics）
   - Q4: ストレージバックエンド（PostgreSQL / DynamoDB / Oracle等）
   - Q5: 環境・予算（開発/PoC / 本番コスト重視 / 本番機能重視 / AWS Marketplace）
3. **エディション判定** — 判定ロジックに基づく推奨エディション決定
4. **ユーザー確認** — 推奨結果を提示し確認
5. **設定ファイル出力** → `work/{project}/scalardb-edition-config.md`

## 判定ロジック

| 優先順位 | 条件 | 推奨エディション |
|---------|------|----------------|
| 1 | GraphQLが必要 | Enterprise Premium |
| 2 | AWS Marketplace課金 | Enterprise Premium |
| 3 | SQL Interface / Spring Data / 認証・認可 / Oracle / Analytics | Enterprise Standard |
| 4 | Cluster（分散デプロイ）が必要 | Enterprise Standard |
| 5 | 上記いずれも不要 | OSS/Community |

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `work/{project}/scalardb-edition-config.md` | エディション設定（YAML frontmatter + 選定理由・構成・依存関係） |

## 下流スキルへの影響

このスキルの出力は以下の6スキルから参照されます:
- `/design-scalardb` — データアーキテクチャ設計
- `/design-scalardb-app-patterns` — アプリケーション設計パターン
- `/generate-scalardb-code` — コード生成
- `/design-implementation` — 実装仕様
- `/scalardb-sizing-estimator` — サイジング見積もり
- `/review-scalardb` — 設計・コードレビュー

## 関連スキル

- 次のフェーズ: [/design-scalardb](design-scalardb.md), [/design-scalardb-app-patterns](design-scalardb-app-patterns.md)
