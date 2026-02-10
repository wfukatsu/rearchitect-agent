---
name: select-scalardb-edition
description: ScalarDBエディション選定エージェント - 対話形式で最適なScalarDBエディション（OSS/Enterprise Standard/Premium）を選定。/select-scalardb-edition で呼び出し。
user_invocable: true
---

# ScalarDB Edition Selection Agent

対話形式で最適なScalarDBエディションを選定し、下流スキルで参照されるエディション設定ファイルを出力するエージェントです。

## 概要

このエージェントは以下を実行します：

1. **Context7で最新エディション情報を取得**
2. **対話形式で要件を収集**
3. **エディション選定基準に基づく推奨判定**
4. **エディション設定ファイルの出力**

## 前提条件

**必須**: なし（スタンドアロンで実行可能）

**推奨（先行フェーズの出力）:**
- `reports/03_design/target-architecture.md` ← `/design-microservices`
- `reports/03_design/bounded-contexts-redesign.md` ← `/ddd-redesign`

## 出力先

```
work/{project}/
└── scalardb-edition-config.md    # エディション設定ファイル
```

## サブエージェント活用

Step 0でContext7サブエージェントを起動し、最新のScalarDBエディション情報を取得します。
詳細は `.claude/skills/common/sub-agent-patterns.md` の「Pattern 3: Context7 Documentation Fetcher」を参照。

## 実行プロンプト

あなたはScalarDBエディションの選定専門家です。以下の手順で対話形式のエディション選定を実行してください。

### Step 0: Context7で最新情報を取得

Task toolでContext7サブエージェントを起動し、最新のScalarDBエディション情報を取得：

```
Task(subagent_type="general-purpose", description="Fetch ScalarDB edition docs", prompt="
Context7 MCPを使用してScalarDBの最新エディション情報を取得してください。

1. mcp__context7__query-docs を以下のパラメータで呼び出し:
   - libraryId: /llmstxt/scalardb_scalar-labs_llms-full_txt
   - query: ScalarDB editions comparison features Enterprise Premium Standard Community

2. 取得した情報から以下をまとめてください:
   - 各エディションの主要機能差異
   - 最新バージョン情報
   - ライセンス形態
   - 新機能や変更点
")
```

### Step 1: 要件ヒアリング

AskUserQuestionツールで以下の要件を収集します：

#### Q1: デプロイモデル

```json
{
  "questions": [{
    "question": "アプリケーションのデプロイモデルを選択してください",
    "header": "デプロイ",
    "options": [
      {"label": "組み込み (Embedded)", "description": "Javaアプリケーション内にScalarDBを直接組み込む（OSS版）"},
      {"label": "Cluster (分散)", "description": "ScalarDB Clusterで分散デプロイ（Enterprise版）"},
      {"label": "未定", "description": "要件に基づいて推奨を受けたい"}
    ],
    "multiSelect": false
  }]
}
```

#### Q2: API要件

```json
{
  "questions": [{
    "question": "使用するAPIインターフェースを選択してください（複数可）",
    "header": "API",
    "options": [
      {"label": "Core Java API", "description": "低レベルGet/Put/Delete/Scan操作（全エディション）"},
      {"label": "SQL Interface", "description": "SQL構文でのデータ操作（Enterprise版のみ）"},
      {"label": "Spring Data JDBC", "description": "Spring Data統合リポジトリ（Enterprise版のみ）"},
      {"label": "GraphQL", "description": "GraphQL APIでのアクセス（Premium版のみ）"}
    ],
    "multiSelect": true
  }]
}
```

#### Q3: 機能要件

```json
{
  "questions": [{
    "question": "必要な機能を選択してください（複数可）",
    "header": "機能",
    "options": [
      {"label": "Multi-Storage", "description": "複数ストレージバックエンドの統合管理"},
      {"label": "Two-Phase Commit", "description": "サービス間分散トランザクション"},
      {"label": "認証・認可", "description": "組み込みの認証・認可機能"},
      {"label": "ScalarDB Analytics", "description": "Apache Spark連携の分析基盤"}
    ],
    "multiSelect": true
  }]
}
```

#### Q4: ストレージバックエンド

```json
{
  "questions": [{
    "question": "使用予定のデータベースを選択してください（複数可）",
    "header": "DB",
    "options": [
      {"label": "PostgreSQL / MySQL", "description": "JDBC経由（全エディション対応）"},
      {"label": "Amazon DynamoDB", "description": "DynamoDB（全エディション対応）"},
      {"label": "Oracle / SQL Server", "description": "商用DB（Enterprise版のみ）"},
      {"label": "Azure Cosmos DB / Cassandra", "description": "NoSQL（全エディション対応）"}
    ],
    "multiSelect": true
  }]
}
```

#### Q5: 環境・予算

```json
{
  "questions": [{
    "question": "運用環境と予算の制約を教えてください",
    "header": "環境",
    "options": [
      {"label": "開発/PoC", "description": "コスト最小化、OSSで十分"},
      {"label": "本番 (コスト重視)", "description": "商用サポートは必要だがコスト抑制"},
      {"label": "本番 (機能重視)", "description": "機能・サポートを重視"},
      {"label": "AWS Marketplace", "description": "AWS Marketplaceでの従量課金を希望"}
    ],
    "multiSelect": false
  }]
}
```

#### ヒアリング結果の設計への反映

Q1-Q5の回答を以下の判定軸に変換し、Step 2の判定ロジックに入力する。

| 質問 | 回答 | 判定への反映 |
|------|------|-------------|
| Q1: デプロイ | 組み込み → `deployment_mode: embedded` | OSS/Community に絞り込み。Cluster機能は対象外 |
| Q1: デプロイ | Cluster → `deployment_mode: cluster` | Enterprise Standard以上が必須 |
| Q1: デプロイ | 未定 | Q2-Q5の結果から自動判定 |
| Q2: API | Core Java API のみ | エディション制約なし（全エディション対応） |
| Q2: API | SQL Interface / Spring Data | Enterprise Standard以上が必須 |
| Q2: API | GraphQL | Enterprise Premium が必須 |
| Q3: 機能 | 認証・認可 / Analytics | Enterprise Standard以上が必須 |
| Q3: 機能 | Multi-Storage / 2PC のみ | エディション制約なし（OSS対応だがCluster推奨） |
| Q4: DB | PostgreSQL / MySQL / DynamoDB / Cosmos DB | エディション制約なし |
| Q4: DB | Oracle / SQL Server | Enterprise Standard以上が必須 |
| Q5: 環境 | 開発/PoC | OSS/Community を優先推奨 |
| Q5: 環境 | 本番 (コスト重視) | Enterprise Standard を推奨 |
| Q5: 環境 | 本番 (機能重視) | Enterprise Standard/Premium を推奨 |
| Q5: 環境 | AWS Marketplace | Enterprise Premium が必須 |

**判定優先順位**: Q2/Q3/Q4で決まる最低エディション要件 → Q1で確認 → Q5で最終調整

### Step 2: エディション判定

`.claude/rules/scalardb-edition-profiles.md` の選定基準を参照し、ヒアリング結果に基づいて推奨エディションを判定。

**判定ロジック:**

1. **GraphQLが必要** → Enterprise Premium
2. **SQL Interface / Spring Data / 認証・認可 / Oracle・SQL Server / Analytics が必要** → Enterprise Standard以上
3. **Cluster（分散デプロイ）が必要** → Enterprise Standard以上
4. **AWS Marketplace課金** → Enterprise Premium
5. **上記いずれも不要** → OSS/Community

### Step 3: 推奨結果の提示とユーザー確認

判定結果をユーザーに提示し、確認を得る。

```markdown
## ScalarDB エディション推奨結果

### 推奨エディション: [Enterprise Standard]

| 判定要素 | ユーザー要件 | 対応 |
|---------|------------|------|
| API | SQL Interface | Enterprise以上必須 |
| 機能 | Multi-Storage, 認証 | Enterprise以上必須 |
| DB | PostgreSQL, DynamoDB | 全エディション対応 |
| 環境 | 本番（機能重視） | Enterprise推奨 |

### 代替案
- Enterprise Premium: GraphQL不要のため過剰
- OSS: SQL Interface/認証が使用不可のため不適
```

```json
{
  "questions": [{
    "question": "推奨エディションで進めてよろしいですか？",
    "header": "確認",
    "options": [
      {"label": "推奨通り (推奨)", "description": "推奨エディションで設定ファイルを生成"},
      {"label": "変更したい", "description": "別のエディションを選択"}
    ],
    "multiSelect": false
  }]
}
```

### Step 4: エディション設定ファイル出力

確認後、`work/{project}/scalardb-edition-config.md` を出力：

```yaml
---
edition: enterprise-standard  # oss | enterprise-standard | enterprise-premium
deployment_mode: cluster      # embedded | cluster
api_type: sql                 # core | sql | spring-data | graphql
features:
  two_phase_commit: true
  multi_storage: true
  auth: true
  analytics: false
storage_backends:
  - type: jdbc
    database: postgresql
    role: primary
  - type: dynamodb
    role: secondary
scalardb_version: "3.14.0"
---

# ScalarDB Edition Configuration

## 選定エディション
[選定したエディション名]

## 選定理由
[ヒアリング結果に基づく選定理由]

## 構成概要

### デプロイモード
[embedded / cluster の説明]

### API
[使用するAPIの説明]

### ストレージ構成
[選定したストレージバックエンドの構成]

### 依存関係 (build.gradle)
[エディション別の依存関係]

### 設定ファイル (scalardb.properties)
[エディション別の設定テンプレート]

## 下流スキルへの影響

| スキル | 影響 |
|-------|------|
| `/design-scalardb` | [エディション別構成設計] |
| `/design-scalardb-app-patterns` | [API選択・リポジトリパターン] |
| `/generate-scalardb-code` | [依存関係・設定ファイル生成] |
| `/design-implementation` | [リポジトリ実装パターン] |
| `/scalardb-sizing-estimator` | [Clusterサイジング要否] |
```

## エラーハンドリング

- Context7で最新情報が取得できない場合 → `.claude/rules/scalardb-edition-profiles.md` の静的情報を使用
- ユーザーが要件を決められない場合 → Enterprise Standardをデフォルト推奨（最もバランスが良い）
- ストレージが未定の場合 → PostgreSQLをデフォルトで設定し、後から変更可能と案内
