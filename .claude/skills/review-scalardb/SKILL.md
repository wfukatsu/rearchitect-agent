---
name: review-scalardb
description: ScalarDBレビューエージェント - 設計レビュー（--mode=design）とコードレビュー（--mode=code）を実行。/review-scalardb --mode=design で呼び出し。
user_invocable: true
---

# ScalarDB Review Agent

ScalarDB関連の設計およびコードをレビューし、品質・整合性・ベストプラクティス準拠を検証するエージェントです。

## 概要

2つのモードで動作します：

1. **設計レビュー** (`--mode=design`): ScalarDB設計ドキュメントの品質検証
2. **コードレビュー** (`--mode=code`): 生成されたScalarDB/Spring Bootコードの品質検証

## 前提条件

### Mode A: 設計レビュー (`--mode=design`)

**必須:**
- `work/{project}/scalardb-edition-config.md` ← `/select-scalardb-edition`
- `reports/03_design/scalardb-*.md` のいずれか ← `/design-scalardb` or `/design-scalardb-app-patterns`

### Mode B: コードレビュー (`--mode=code`)

**必須:**
- `work/{project}/scalardb-edition-config.md` ← `/select-scalardb-edition`
- `generated/{service}/` ← `/generate-scalardb-code`

## 出力先

結果は `reports/03_design/` に出力します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

```
reports/03_design/
├── scalardb-design-review.md    # Mode A: Step 7A完了時
└── scalardb-code-review.md      # Mode B: Step 7B完了時
```

## サブエージェント活用

- Context7でScalarDB最新仕様を取得（Pattern 3）
- 観点別に並列レビューサブエージェントを起動（Pattern 4）

詳細は `.claude/skills/common/sub-agent-patterns.md` を参照。

## 実行プロンプト

あなたはScalarDBの設計・コード品質の専門家です。以下の手順でレビューを実行してください。

### Step 0: モード判定と前提条件検証

引数からモード（`--mode=design` or `--mode=code`）を判定。

```
必須ファイルの確認:
├── work/{project}/scalardb-edition-config.md  [必須]
├── [Mode A] reports/03_design/scalardb-*.md   [必須]
└── [Mode B] generated/{service}/              [必須]
```

**エラーハンドリング:**
- エディション設定が存在しない → `/select-scalardb-edition` を先に実行するよう案内
- 設計ファイルが存在しない → `/design-scalardb` を先に実行するよう案内
- コードが存在しない → `/generate-scalardb-code` を先に実行するよう案内

### Step 1: Context7で最新仕様を取得

```
Task(subagent_type="general-purpose", description="Fetch ScalarDB latest specs", prompt="
Context7 MCPでScalarDBの最新仕様を取得してください。

mcp__context7__query-docs を以下で呼び出し:
- libraryId: /llmstxt/scalardb_scalar-labs_llms-full_txt
- query: ScalarDB best practices schema design transaction management configuration

取得した情報から以下をまとめてください:
- 最新の設計ガイドライン
- 非推奨/廃止された機能
- パフォーマンスベストプラクティス
")
```

---

## Mode A: 設計レビュー

### Step 2A: レビュー対象の読み込み

以下の設計ファイルを読み込み：

- `work/{project}/scalardb-edition-config.md` （エディション設定）
- `reports/03_design/scalardb-schema-design.md` （スキーマ設計）
- `reports/03_design/scalardb-app-patterns.md` （アプリパターン）
- `reports/03_design/scalardb-database-selection.md` （DB選定）
- `reports/03_design/target-architecture.md` （ターゲットアーキテクチャ）

### Step 3A: エディション整合性チェック

| チェック項目 | 説明 | 重要度 |
|------------|------|--------|
| API使用 | 選定エディションで利用可能なAPIのみ使用しているか | Critical |
| ストレージ | 選定エディションで対応するストレージのみ指定しているか | Critical |
| 機能参照 | 認証・SQL・GraphQL等がエディション制約に適合しているか | Critical |
| 依存関係 | build.gradleの依存がエディションに適合しているか | High |
| 設定ファイル | scalardb.propertiesがエディションテンプレートに準拠しているか | High |

### Step 4A: Key設計妥当性チェック

| チェック項目 | 説明 | 重要度 |
|------------|------|--------|
| パーティションキー | 均等分散されるか、ホットスポットがないか | Critical |
| クラスタリングキー | 順序付けが適切か、範囲スキャンに対応しているか | High |
| 二次インデックス | 使用が最小限か、代替設計がないか | Medium |
| データ型 | ScalarDB対応型を使用しているか | High |
| Namespace設計 | サービス境界と一致しているか | High |

### Step 5A: トランザクション境界チェック

| チェック項目 | 説明 | 重要度 |
|------------|------|--------|
| 単一サービス | DistributedTransactionが適切に使用されているか | High |
| 2PC使用箇所 | TwoPhaseCommitが必要最小限か、代替（Saga）で置換可能か | Critical |
| 分離レベル | SERIALIZABLE/SNAPSHOT選択が適切か | High |
| デッドロック | 複数テーブルアクセスの順序が一貫しているか | High |
| トランザクション粒度 | 長すぎるトランザクションがないか | Medium |

### Step 6A: Multi-Storage構成チェック

| チェック項目 | 説明 | 重要度 |
|------------|------|--------|
| namespace_mapping | 全Namespaceがマッピングされているか | Critical |
| default_storage | デフォルトストレージが指定されているか | High |
| 2PC制約 | Multi-Storage + 2PCの制約を理解しているか | High |
| データ整合性 | ストレージ間のデータ整合性方針が明確か | High |

### Step 7A: レビュー結果出力

**出力**: `reports/03_design/scalardb-design-review.md`

---

## Mode B: コードレビュー

### Step 2B: レビュー対象の読み込み

```
Task(subagent_type="Explore", description="Scan generated code", prompt="
以下のディレクトリ内のScalarDB関連コードを調査してください:
- generated/{service}/ の全Javaファイル

以下の観点で情報を収集:
1. リポジトリ実装クラス一覧
2. トランザクション管理パターン
3. エンティティ/値オブジェクトの定義
4. 設定ファイルの内容
5. build.gradleの依存関係
")
```

### Step 3B: coding-patterns準拠チェック

`.claude/rules/scalardb-coding-patterns.md` に基づくチェック：

| チェック項目 | 対応ルール | 重要度 |
|------------|----------|--------|
| プロジェクト構造 | §1 | High |
| 命名規則 | §2 | High |
| 値オブジェクト | §3 | Critical |
| エンティティ | §4 | Critical |
| リポジトリ | §5 | Critical |
| トランザクション | §6 | Critical |
| 設定 | §7/7A/7B | Critical |
| 例外ハンドリング | §8 | High |

### Step 4B: エディション別APIチェック

| エディション | チェック内容 |
|------------|------------|
| **OSS** | Core API のみ使用、SQL/Spring Data未使用、TransactionFactory直接初期化 |
| **Enterprise Standard** | Cluster Client設定、SQL/Spring Data使用可、認証設定 |
| **Enterprise Premium** | Standard + GraphQL関連コード |

### Step 5B: トランザクション管理チェック

| チェック項目 | 説明 | 重要度 |
|------------|------|--------|
| try-catch-abort | 全トランザクションにabort処理があるか | Critical |
| close処理 | TransactionManager/Sessionのcloseがあるか | Critical |
| 例外変換 | TransactionException→ドメイン例外変換があるか | High |
| リトライ | CrudConflictExceptionのリトライ処理 | Medium |
| 楽観ロック | versionチェックが実装されているか | High |

### Step 6B: VO/Entity/Repositoryチェックリスト

**値オブジェクト:**
- [ ] `record` 使用またはimmutable
- [ ] コンストラクタでバリデーション
- [ ] ファクトリメソッド提供 (`of`, `generate`)
- [ ] equals/hashCodeは値で比較

**エンティティ:**
- [ ] ファクトリメソッド (`create`)
- [ ] 復元メソッド (`reconstitute`)
- [ ] ドメインイベント管理
- [ ] `version` フィールド

**リポジトリ:**
- [ ] インターフェースはドメイン層
- [ ] 実装はインフラ層
- [ ] エディション別API使用
- [ ] トランザクション管理
- [ ] 楽観ロックチェック

### Step 7B: レビュー結果出力

**出力**: `reports/03_design/scalardb-code-review.md`

---

## 出力フォーマット

### scalardb-design-review.md / scalardb-code-review.md

```markdown
---
title: ScalarDB [設計/コード]レビュー
phase: "Phase [5.9/8.5]: ScalarDB Review"
skill: review-scalardb
mode: [design/code]
generated_at: [timestamp]
input_files:
  - [レビュー対象ファイル一覧]
---

# ScalarDB [設計/コード]レビュー

## エグゼクティブサマリー

| カテゴリ | 合格 | 警告 | 不合格 | 合計 |
|---------|------|------|--------|------|
| エディション整合性 | X | X | X | X |
| Key設計 | X | X | X | X |
| トランザクション | X | X | X | X |
| [その他] | X | X | X | X |
| **合計** | **X** | **X** | **X** | **X** |

## 総合判定

- [ ] **PASS**: 問題なし、次フェーズ進行可能
- [ ] **CONDITIONAL PASS**: 警告あり、修正推奨だが進行可能
- [ ] **FAIL**: 不合格項目あり、修正必須

## 詳細レビュー結果

### [カテゴリ名]

| # | チェック項目 | 結果 | 重要度 | 詳細 | 修正提案 |
|---|------------|------|--------|------|---------|
| 1 | [項目] | PASS/WARN/FAIL | Critical/High/Medium | [詳細] | [提案] |

## 修正推奨事項（優先順）

### Critical（即時修正必須）
1. [項目と修正内容]

### High（早期修正推奨）
1. [項目と修正内容]

### Medium（改善推奨）
1. [項目と修正内容]

## Context7参照による最新仕様との差異
[Context7で取得した最新情報との差異があれば記載]
```

## エラーハンドリング

- レビュー対象がない → 前提スキルの実行を案内
- Context7で最新情報が取得できない → 静的ルールのみでレビュー実行（警告付き）
- 複数サービスのコードがある → ユーザーに対象サービスの選択を促す

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/design-scalardb` | ScalarDB設計（レビュー対象） |
| `/design-scalardb-app-patterns` | アプリケーション設計パターン（レビュー対象） |
| `/generate-scalardb-code` | コード生成（レビュー対象） |
| `/select-scalardb-edition` | エディション選定（前提） |
