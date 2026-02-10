---
name: design-scalardb-app-patterns
description: ScalarDBアプリケーション設計パターンエージェント - ドメインタイプ判別に基づく設計パターン選択・データモデリング・DB選定・スキーマ設計。/design-scalardb-app-patterns [対象パス] で呼び出し。
user_invocable: true
---

# ScalarDB Application Design Patterns Agent

ドメインタイプの判別に基づいて、ScalarDBを使用するアプリケーションの設計パターン・データモデリング・DB選定・スキーマ設計を行うエージェントです。

## 概要

このエージェントは以下を実行します：

1. **ドメインタイプ判別**（Pipeline/Blackboard/Dialogue × Process/Master/Integration/Supporting）
2. **ドメインタイプ別設計パターン選択**
3. **ストレージバックエンド推奨**（エディション制約考慮）
4. **ScalarDBスキーマ設計**（Namespace/Table/Key設計）
5. **アプリケーションアーキテクチャパターン**（エディション別リポジトリ実装）

## 前提条件

**必須:**
- `work/{project}/scalardb-edition-config.md` ← `/select-scalardb-edition`

**推奨:**
- `reports/03_design/bounded-contexts-redesign.md` ← `/ddd-redesign`
- `reports/03_design/aggregate-redesign.md` ← `/ddd-redesign`
- `reports/03_design/context-map.md` ← `/ddd-redesign`
- `reports/03_design/domain-analysis.md` ← `/ddd-redesign`
- `reports/01_analysis/ubiquitous-language.md` ← `/analyze-system`

## 出力先

結果は `reports/03_design/` に出力します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

```
reports/03_design/
├── scalardb-app-patterns.md       # Step 3-6完了時
└── scalardb-database-selection.md  # Step 4完了時
```

## サブエージェント活用

- Step 0: Context7でScalarDB最新パターン取得（Pattern 3）
- 前フェーズ出力が多い場合: Exploreエージェントで要約読み込み（Pattern 2）

詳細は `.claude/skills/common/sub-agent-patterns.md` を参照。

## 実行プロンプト

あなたはScalarDBアプリケーション設計パターンの専門家です。以下の手順で設計を実行してください。

### Step 0: 前提条件の検証 + Context7取得

**前提条件チェック:**

```
必須ファイルの確認:
└── work/{project}/scalardb-edition-config.md  [必須] ← /select-scalardb-edition

推奨ファイルの確認:
├── reports/03_design/bounded-contexts-redesign.md  [推奨] ← /ddd-redesign
├── reports/03_design/aggregate-redesign.md         [推奨] ← /ddd-redesign
├── reports/03_design/context-map.md                [推奨] ← /ddd-redesign
└── reports/01_analysis/ubiquitous-language.md      [推奨] ← /analyze-system
```

**エラーハンドリング:**
- 必須ファイルが存在しない → `/select-scalardb-edition` を先に実行するよう案内
- 推奨ファイルが存在しない → 警告を表示して続行（対象パスのコード解析で補完）

**Context7取得:**

```
Task(subagent_type="general-purpose", description="Fetch ScalarDB patterns docs", prompt="
Context7 MCPでScalarDBの設計パターン情報を取得してください。

mcp__context7__query-docs を呼び出し:
- libraryId: /llmstxt/scalardb_scalar-labs_llms-full_txt
- query: ScalarDB application design patterns data modeling schema design best practices

取得した情報から以下をまとめてください:
- 推奨されるデータモデリングパターン
- スキーマ設計のベストプラクティス
- パーティションキー/クラスタリングキーの設計指針
")
```

### Step 1: 非機能要件の確認

設計パターン選択とストレージ推奨に影響する非機能要件をAskUserQuestionで確認する。

```json
{
  "questions": [
    {
      "question": "想定するトランザクションスループットを選択してください",
      "header": "スループット",
      "options": [
        {"label": "<500 TPS (推奨)", "description": "PoC・小規模サービス。単一ストレージで十分"},
        {"label": "500-2,000 TPS", "description": "標準的な業務アプリケーション"},
        {"label": "2,000-10,000 TPS", "description": "高トラフィック。ストレージ選定に大きく影響"},
        {"label": ">10,000 TPS", "description": "ECサイトのセール時等。水平分散必須"}
      ],
      "multiSelect": false
    },
    {
      "question": "トランザクションのレイテンシ要件を選択してください",
      "header": "レイテンシ",
      "options": [
        {"label": "<100ms (推奨)", "description": "一般的な業務アプリ。JDBC系ストレージで達成可能"},
        {"label": "<30ms", "description": "リアルタイム処理。DynamoDB/キャッシュ併用推奨"},
        {"label": "<500ms", "description": "バッチ系・バックオフィス。ストレージ制約が緩い"},
        {"label": "サービス別に異なる", "description": "コンテキストごとに異なるレイテンシ要件"}
      ],
      "multiSelect": false
    },
    {
      "question": "想定するデータボリューム（1年後）を選択してください",
      "header": "データ量",
      "options": [
        {"label": "<10GB (推奨)", "description": "マスターデータ中心。ストレージ選択の自由度が高い"},
        {"label": "10-100GB", "description": "トランザクションデータ蓄積。インデックス設計が重要"},
        {"label": "100GB-1TB", "description": "パーティション戦略・アーカイブ戦略が必要"},
        {"label": ">1TB", "description": "NoSQL/分散DB必須。ScalarDB Analyticsの検討推奨"}
      ],
      "multiSelect": false
    }
  ]
}
```

**反映先:** スループット・レイテンシ→Step 4 ストレージ推奨、データ量→Step 5 パーティション戦略

### Step 2: ドメインタイプ判別

各境界づけられたコンテキスト（またはマイクロサービス）に対して、2軸でドメインタイプを判別。

#### ビジネス構造軸

| タイプ | 判別基準 | 設計含意 |
|--------|---------|---------|
| **Pipeline** | 順次的なデータ/プロセスフロー、ステージ間のデータ変換 | Event Sourcing + CQRS |
| **Blackboard** | 共有データに対する協調作業、複数アクターによるデータ更新 | 共有データモデル + 楽観ロック |
| **Dialogue** | 双方向の対話・インタラクション、リクエスト-レスポンスの連鎖 | Saga + 状態マシン |

#### マイクロサービス境界軸

| タイプ | 判別基準 | 設計含意 |
|--------|---------|---------|
| **Process** | ビジネスプロセス実行、複数ステップのワークフロー | Saga/2PC、イベント駆動 |
| **Master** | マスターデータ管理、参照系が多い | CRUD中心、キャッシュ |
| **Integration** | 外部システム連携、アダプター | ACL、リトライ、サーキットブレーカー |
| **Supporting** | 横断的関心事、インフラ的サービス | 軽量トランザクション |

**判別結果テンプレート:**

```markdown
| コンテキスト/サービス | ビジネス構造 | サービスカテゴリ | 根拠 |
|---------------------|------------|----------------|------|
| 注文管理 | Pipeline | Process | 注文→確認→発送の順次フロー |
| 在庫管理 | Blackboard | Master | 複数サービスからの在庫更新 |
| 決済連携 | Dialogue | Integration | 外部決済APIとの対話 |
| 認証 | - | Supporting | 横断的関心事 |
```

### Step 3: ドメインタイプ別設計パターン選択

#### Pipeline × Process: Event Sourcing + CQRS

```markdown
### 設計パターン
- **Write Model**: イベントストア（ScalarDB テーブル）
- **Read Model**: 集約ビュー（ScalarDB 別テーブル / Materialized View）
- **トランザクション**: 各ステージ内はACID、ステージ間はイベント駆動

### ScalarDB テーブル設計
| テーブル | パーティションキー | クラスタリングキー | 用途 |
|---------|-------------------|------------------|------|
| events | aggregate_id | sequence_number | イベントストア |
| snapshots | aggregate_id | version | スナップショット |
| read_models | query_key | - | 読み取り専用ビュー |
```

#### Blackboard × Master: 共有データモデル + 楽観ロック

```markdown
### 設計パターン
- **データモデル**: CRUD中心、楽観ロック（version列）
- **整合性**: ScalarDB Consensus Commit（SERIALIZABLE）
- **キャッシュ**: 読み取り頻度が高い場合はアプリケーション層キャッシュ

### ScalarDB テーブル設計
| テーブル | パーティションキー | クラスタリングキー | 用途 |
|---------|-------------------|------------------|------|
| masters | entity_id | - | マスターデータ |
| master_versions | entity_id | version | バージョン履歴 |
```

#### Dialogue × Integration: Saga + 状態マシン

```markdown
### 設計パターン
- **Sagaパターン**: Orchestration（コーディネーター管理）
- **状態管理**: 状態マシンテーブルで進行状況追跡
- **補償**: 各ステップに補償アクション定義
- **トランザクション**: ステップ内はACID、ステップ間はSaga

### ScalarDB テーブル設計
| テーブル | パーティションキー | クラスタリングキー | 用途 |
|---------|-------------------|------------------|------|
| sagas | saga_id | - | Saga状態管理 |
| saga_steps | saga_id | step_order | ステップ管理 |
| compensations | saga_id | step_order | 補償アクション |
```

#### Process × Two-Phase Commit

```markdown
### 設計パターン
- **2PC**: ScalarDB TwoPhaseCommitTransactionManager
- **対象**: 複数サービスにまたがるデータ整合性が必須の場合
- **注意**: パフォーマンスへの影響大、必要最小限に限定

### エディション別制約
- **OSS**: TwoPhaseCommitTransactionManager を直接使用
- **Enterprise**: Cluster経由で2PC実行（推奨）
```

### Step 4: ストレージバックエンド推奨

エディション設定ファイルの `edition` と要件に基づき、各コンテキストに最適なストレージを推奨。

**推奨マトリクス:**

| ドメインタイプ | 推奨ストレージ | 理由 |
|-------------|-------------|------|
| Pipeline/Process | PostgreSQL (JDBC) | ACID保証、JSON対応、イベントストア |
| Blackboard/Master | PostgreSQL (JDBC) | リレーショナルクエリ、インデックス |
| Dialogue/Integration | DynamoDB / Cosmos DB | 高スループット、低レイテンシ |
| Supporting | PostgreSQL (JDBC) | 汎用、低コスト |
| 大量データ分析 | Cassandra | 高書き込みスループット |

**エディション別制約:**
- **OSS**: PostgreSQL/MySQL (JDBC)、DynamoDB、Cosmos DB、Cassandra
- **Enterprise Standard/Premium**: 上記 + Oracle、SQL Server、Aurora、YugabyteDB、MariaDB

**Multi-Storage構成の判断:**
- 単一ストレージで要件を満たせる → 単一ストレージ推奨
- コンテキストごとに異なるDB特性が必要 → Multi-Storage推奨

#### ストレージ推奨結果の確認

推奨結果をユーザーに提示した後、以下で確認する：

```json
{
  "questions": [{
    "question": "推奨されたストレージ構成で進めてよろしいですか？",
    "header": "ストレージ確認",
    "options": [
      {"label": "推奨通り (推奨)", "description": "アルゴリズムが選定したストレージ構成で設計を進める"},
      {"label": "単一ストレージに変更", "description": "運用簡素化のため全コンテキストで同一ストレージを使用"},
      {"label": "Multi-Storageに変更", "description": "コンテキスト別に異なるストレージを使用"},
      {"label": "ストレージを個別に変更", "description": "特定のコンテキストのストレージのみ変更"}
    ],
    "multiSelect": false
  }]
}
```

「ストレージを個別に変更」が選択された場合、変更対象のコンテキストとストレージを追加で確認する。

**このステップ完了時に出力**: `reports/03_design/scalardb-database-selection.md`

### Step 5: ScalarDBスキーマ設計

各コンテキストのスキーマを設計。

#### Namespace設計

```
命名規則: {service_name} (snake_case)
例: order_service, inventory_service, payment_service
```

#### テーブル設計

```markdown
## [コンテキスト名] スキーマ

### Namespace: {service_name}

#### テーブル: {entity}s

| カラム | 型 | キー | 説明 |
|--------|-----|------|------|
| id | TEXT | PK | エンティティID |
| ... | ... | ... | ... |
| version | INT | - | 楽観ロック用バージョン |
| created_at | BIGINT | - | 作成日時 (Unix millis) |
| updated_at | BIGINT | - | 更新日時 (Unix millis) |

**パーティションキー**: id
**クラスタリングキー**: なし（単一レコードアクセス）
```

#### キー設計ガイドライン

| パターン | パーティションキー | クラスタリングキー | ユースケース |
|---------|-------------------|------------------|------------|
| 単一エンティティ | entity_id | なし | マスターデータ |
| 親子関係 | parent_id | child_id | 注文→明細 |
| 時系列 | entity_id | timestamp DESC | イベント履歴 |
| 複合キー | tenant_id | entity_id | マルチテナント |

### Step 6: アプリケーションアーキテクチャパターン

エディション設定に基づくリポジトリ実装パターンを設計。

#### OSS/Community Edition: Core API直接使用

```java
// リポジトリ実装: Core Java API
@Repository
public class ScalarDbOrderRepository implements OrderRepository {
    private final DistributedTransactionManager txManager;
    private static final String NAMESPACE = "order_service";
    private static final String TABLE = "orders";

    @Override
    public Optional<Order> findById(OrderId id) {
        DistributedTransaction tx = txManager.start();
        try {
            Get get = Get.newBuilder()
                .namespace(NAMESPACE).table(TABLE)
                .partitionKey(Key.ofText("id", id.value()))
                .build();
            Optional<Result> result = tx.get(get);
            tx.commit();
            return result.map(this::toEntity);
        } catch (Exception e) {
            tx.abort();
            throw new InfrastructureException("Failed to find order", e);
        }
    }
}
```

#### Enterprise Edition: SQL Interface

```java
// リポジトリ実装: SQL Interface (Enterprise)
@Repository
public class SqlOrderRepository implements OrderRepository {
    private final SqlSessionFactory sqlSessionFactory;

    @Override
    public Optional<Order> findById(OrderId id) {
        SqlSession session = sqlSessionFactory.createSqlSession();
        try {
            ResultSet rs = session.execute(
                "SELECT * FROM order_service.orders WHERE id = ?", id.value());
            // ... map result
            session.commit();
            return result;
        } catch (Exception e) {
            session.rollback();
            throw new InfrastructureException("Failed to find order", e);
        }
    }
}
```

#### Enterprise Edition: Spring Data JDBC

```java
// リポジトリ実装: Spring Data JDBC (Enterprise)
// 自動生成されるリポジトリ
public interface OrderSpringRepository extends ScalarDbRepository<OrderEntity, String> {
    List<OrderEntity> findByCustomerId(String customerId);
    List<OrderEntity> findByStatus(String status);
}

// ドメインリポジトリのアダプター
@Repository
public class SpringDataOrderRepository implements OrderRepository {
    private final OrderSpringRepository springRepo;
    private final OrderEntityMapper mapper;

    @Override
    public Optional<Order> findById(OrderId id) {
        return springRepo.findById(id.value())
            .map(mapper::toDomain);
    }
}
```

**このステップ完了時に出力**: `reports/03_design/scalardb-app-patterns.md`

### Step 7: Mermaid図の検証

出力したファイルのMermaid図を検証し、エラーがあれば修正：

```bash
/fix-mermaid ./reports/03_design
```

## 出力フォーマット

### scalardb-app-patterns.md

```markdown
---
title: ScalarDB アプリケーション設計パターン
phase: "Phase 4.8: ScalarDB App Patterns"
skill: design-scalardb-app-patterns
generated_at: [timestamp]
input_files:
  - work/{project}/scalardb-edition-config.md
  - reports/03_design/bounded-contexts-redesign.md
---

# ScalarDB アプリケーション設計パターン

## エディション設定サマリー
[選定エディション、API、ストレージの概要]

## ドメインタイプ判別結果
[Step 2の結果テーブル]

## コンテキスト別設計パターン
[Step 3の各コンテキスト設計]

## スキーマ設計
[Step 5の各テーブル設計]

## リポジトリ実装パターン
[Step 6のエディション別リポジトリ]

## トランザクション設計
[単一/2PC/Sagaの使い分け]
```

### scalardb-database-selection.md

```markdown
---
title: ScalarDB ストレージ選定
phase: "Phase 4.8: ScalarDB App Patterns"
skill: design-scalardb-app-patterns
generated_at: [timestamp]
---

# ScalarDB ストレージ選定

## 選定方針
[エディション制約、要件に基づく方針]

## コンテキスト別ストレージマッピング
[各コンテキストの推奨ストレージ]

## Multi-Storage構成
[namespace_mapping設定]

## ストレージ別設定
[各ストレージの接続設定]
```

## エラーハンドリング

- エディション設定が未選定 → `/select-scalardb-edition` を先に実行するよう案内
- DDD設計が未実施 → 対象パスのコード解析からコンテキストを推定（精度低下を警告）
- 不明なドメインタイプ → ユーザーに確認（AskUserQuestion）

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/select-scalardb-edition` | エディション選定（入力） |
| `/design-scalardb` | ScalarDBデータアーキテクチャ設計（次ステップ） |
| `/generate-scalardb-code` | コード生成（次ステップ） |
| `/design-implementation` | 実装仕様生成（補完） |
