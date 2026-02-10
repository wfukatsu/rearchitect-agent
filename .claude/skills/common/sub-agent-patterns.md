# Sub-Agent Patterns

スキル実行時にTask toolで活用するサブエージェントの標準パターン。
メインコンテキストの肥大化を防ぎ、並列処理で効率化する。

## Pattern 1: コードベース探索エージェント

コードベースを直接スキャンするスキルで使用。メインエージェントのコンテキストを保護しながら、大規模コードベースの情報を収集する。

### 対象スキル

system-investigation, analyze-system, evaluate-mmi, ddd-evaluation

### 使用方法

```
Task(
  subagent_type="Explore",
  prompt="対象ディレクトリ {target_path} のコードベースを探索し、以下を調査してください:
    1. [調査項目1]
    2. [調査項目2]
    結果をJSON形式でまとめてください。",
  description="コードベース探索"
)
```

### 並列探索パターン

複数の観点を同時に調査する場合、独立したExploreエージェントを並列起動:

```
# 並列で3つのExploreエージェントを起動（1つのメッセージで複数Task呼び出し）
Task(subagent_type="Explore", prompt="パッケージ構造と依存関係を調査...", description="構造調査")
Task(subagent_type="Explore", prompt="ドメイン用語とビジネスロジックを抽出...", description="ドメイン用語抽出")
Task(subagent_type="Explore", prompt="外部連携とAPI定義を調査...", description="外部連携調査")
```

### ベストプラクティス

- **スコープを絞る**: 1エージェントにつき1つの明確な調査目的
- **結果フォーマットを指定**: JSON/Markdown等、メインエージェントが処理しやすい形式を指定
- **ファイル数が多い場合はサンプリング指示**: 「主要なファイルを最大20件調査」等


## Pattern 2: 前フェーズ出力読み込みエージェント

前フェーズの出力ファイルを読み込んで要約し、メインエージェントに必要な情報のみを渡す。

### 対象スキル

integrate-evaluations, ddd-redesign, map-domains, design-microservices, design-api, design-scalardb, design-scalardb-analytics, design-implementation, generate-test-specs, generate-scalardb-code, estimate-cost

### 使用方法

```
Task(
  subagent_type="Explore",
  prompt="以下のファイルを読み込み、{current_skill}に必要な情報を抽出・要約してください:

    必須ファイル:
    - reports/02_evaluation/mmi-overview.md
    - reports/02_evaluation/ddd-strategic-evaluation.md

    推奨ファイル（存在すれば読み込み）:
    - reports/01_analysis/ubiquitous-language.md

    抽出する情報:
    1. モジュール一覧とMMIスコア
    2. 境界コンテキスト候補
    3. 主要な改善提案

    結果をMarkdown形式でまとめてください。
    ファイルが存在しない場合は、そのファイル名を「未検出」として報告してください。",
  description="前フェーズ出力の読み込み"
)
```

### 前提条件チェックとの組み合わせ

Step 0（前提条件検証）で存在確認と読み込みを同時に行う:

```
Task(
  subagent_type="Explore",
  prompt="以下のファイルの存在を確認し、存在するファイルの内容を要約してください:

    [必須] reports/03_design/bounded-contexts-redesign.md
    [必須] reports/03_design/aggregate-redesign.md
    [推奨] reports/02_evaluation/mmi-overview.md

    結果フォーマット:
    - ファイルパス: 存在(found)/未検出(not_found)
    - 要約: (存在する場合のみ)

    必須ファイルが未検出の場合は明確に警告してください。",
  description="前提条件チェック"
)
```

### ベストプラクティス

- **要約を求める**: 全文をメインコンテキストに送らず、必要情報のみ抽出
- **存在確認を含める**: ファイルの有無で分岐処理に活用
- **抽出項目を明示**: 「何を抽出するか」を具体的に指定


## Pattern 3: Context7 ドキュメント取得エージェント

Context7 MCPを使用して、ScalarDBの最新ドキュメントやベストプラクティスを動的に取得する。
スキル実行時に静的ルールだけでなく、最新の公式情報を参照することで精度を向上させる。

### 対象スキル

select-scalardb-edition, design-scalardb-app-patterns, review-scalardb, design-scalardb

### 使用方法

```
Task(
  subagent_type="general-purpose",
  prompt="Context7 MCPでScalarDBの最新情報を取得してください。

    mcp__context7__query-docs を以下のパラメータで呼び出し:
    - libraryId: /llmstxt/scalardb_scalar-labs_llms-full_txt
    - query: {取得したい情報のクエリ}

    取得した情報から以下をまとめてください:
    1. [抽出項目1]
    2. [抽出項目2]
    3. [抽出項目3]

    結果をMarkdown形式で返してください。",
  description="Context7でScalarDB最新情報取得"
)
```

### クエリ例

| スキル | クエリ例 |
|-------|---------|
| select-scalardb-edition | `ScalarDB editions comparison features licensing deployment modes` |
| design-scalardb-app-patterns | `ScalarDB application design patterns data modeling schema design best practices` |
| review-scalardb | `ScalarDB best practices schema design transaction management configuration` |
| design-scalardb | `ScalarDB multi-storage configuration two-phase commit transaction isolation levels` |

### エラーハンドリング

Context7で情報を取得できない場合:
- 静的ルール（`.claude/rules/scalardb-edition-profiles.md`, `.claude/rules/scalardb-coding-patterns.md`）のみでスキルを続行
- 出力に「Context7参照: 取得不可（静的ルールのみで実行）」と警告を記載

### ベストプラクティス

- **クエリを具体的にする**: 「ScalarDB」だけでなく、目的に合ったキーワードを含める
- **取得情報を要約させる**: 全文をメインコンテキストに送らず、必要情報のみ抽出
- **Library IDを固定する**: ScalarDB用は常に `/llmstxt/scalardb_scalar-labs_llms-full_txt`
- **フォールバックを用意する**: Context7障害時も静的ルールで動作できるようにする


## Pattern 4: レビューエージェント

レビュー対象を観点別に分割し、並列レビューサブエージェントで効率的にチェックする。
結果を集約してレビューレポートを生成する。

### 対象スキル

review-scalardb

### 使用方法

#### 並列レビュー起動

```
# 観点ごとに並列でExploreエージェントを起動（1つのメッセージで複数Task呼び出し）
Task(
  subagent_type="Explore",
  prompt="以下の観点でScalarDB設計をレビューしてください:
    【エディション整合性チェック】
    - 選定エディションで利用可能なAPIのみ使用しているか
    - build.gradleの依存がエディションに適合しているか
    - 設定ファイルがエディションテンプレートに準拠しているか

    対象ファイル:
    - work/{project}/scalardb-edition-config.md
    - reports/03_design/scalardb-schema-design.md

    結果フォーマット:
    | チェック項目 | 結果(PASS/WARN/FAIL) | 重要度 | 詳細 | 修正提案 |",
  description="エディション整合性レビュー"
)

Task(
  subagent_type="Explore",
  prompt="以下の観点でScalarDB設計をレビューしてください:
    【Key設計・トランザクション境界チェック】
    - パーティションキーが均等分散されるか
    - クラスタリングキーの順序が適切か
    - トランザクション境界が適切か
    - 2PC使用が最小限か

    対象ファイル:
    - reports/03_design/scalardb-schema-design.md
    - reports/03_design/scalardb-app-patterns.md

    結果フォーマット:
    | チェック項目 | 結果(PASS/WARN/FAIL) | 重要度 | 詳細 | 修正提案 |",
  description="Key設計・トランザクションレビュー"
)
```

#### 結果集約パターン

```
# 並列レビュー完了後、メインエージェントで結果を集約
# 各サブエージェントの結果テーブルをマージし、以下を生成:
# 1. エグゼクティブサマリー（カテゴリ別 合格/警告/不合格 集計）
# 2. 総合判定（PASS / CONDITIONAL PASS / FAIL）
# 3. 修正推奨事項（Critical → High → Medium の優先順）
```

### レビュー観点テンプレート

| 観点 | サブエージェント | 主なチェック項目 |
|------|---------------|----------------|
| エディション整合性 | Explore #1 | API使用、依存関係、設定ファイル |
| Key設計 | Explore #2 | パーティションキー、クラスタリングキー、インデックス |
| トランザクション | Explore #3 | 境界、2PC使用、分離レベル、デッドロック |
| コーディング規約 | Explore #4 | coding-patterns準拠、VO/Entity/Repositoryチェック |

### ベストプラクティス

- **観点を独立させる**: 各サブエージェントが独立してレビュー可能な観点に分割
- **結果フォーマットを統一**: 全サブエージェントに同一フォーマットを指定し、集約を容易にする
- **重要度を明示させる**: Critical/High/Medium で分類し、優先度付き修正リストを生成
- **サブエージェントは3-4個まで**: 多すぎると集約コストが増大


## Pattern 5: セキュリティ分析エージェント

セキュリティ脆弱性やアクセス制御の分析を並列で実行する。

### 対象スキル

security-analysis, access-control-analysis

### 使用方法

```
# 並列で複数の観点を調査（1つのメッセージで複数Task呼び出し）
Task(
  subagent_type="Explore",
  prompt="対象ディレクトリ {target_path} でOWASP Top 10の脆弱性を調査:
    1. インジェクション（SQL, NoSQL, OS Command）
    2. 認証・セッション管理の不備
    3. 機密データの露出（ハードコード秘密鍵、平文パスワード等）
    結果をチェックリスト形式でまとめてください。",
  description="OWASP脆弱性スキャン"
)

Task(
  subagent_type="Explore",
  prompt="対象ディレクトリ {target_path} のアクセス制御を分析:
    1. 認証メカニズム（JWT, Session, OAuth等）
    2. 認可モデル（RBAC, ABAC等）
    3. ゼロトラスト準備度
    結果をMarkdown形式でまとめてください。",
  description="アクセス制御分析"
)
```

### ベストプラクティス

- **OWASP観点とアクセス制御観点を分離**: 異なる専門性が必要なため並列実行が効果的
- **脆弱性はファイルパスと行番号を含める**: メインエージェントが修正提案を生成しやすくする
- **機密情報のリストアップ**: .env, credentials, API key 等のパターンを明示的に指示


## Pattern 6: データモデル分析エージェント

データベーススキーマ、エンティティ関係、ER図の分析を効率化する。

### 対象スキル

data-model-analysis, db-design-analysis, er-diagram-analysis

### 使用方法

```
# スキーマ定義とエンティティの並列抽出
Task(
  subagent_type="Explore",
  prompt="対象ディレクトリ {target_path} からデータベーススキーマを抽出:
    1. テーブル/コレクション定義（DDL, マイグレーション, エンティティアノテーション）
    2. カラム名・型・制約（NOT NULL, UNIQUE, FK等）
    3. インデックス定義
    結果をテーブル一覧形式でまとめてください。",
  description="スキーマ定義抽出"
)

Task(
  subagent_type="Explore",
  prompt="対象ディレクトリ {target_path} からエンティティ関係を抽出:
    1. エンティティ間のリレーションシップ（1:1, 1:N, N:M）
    2. 外部キー参照
    3. JPA/Hibernate等のアノテーションから関連を推定
    Mermaid ER図形式でまとめてください。",
  description="エンティティ関係抽出"
)
```

### ベストプラクティス

- **スキーマとリレーションを分離**: スキーマ抽出後にリレーション分析を行うと精度が向上
- **マイグレーションファイルを優先**: ORM定義より正確な場合が多い
- **Mermaid ER図出力を指示**: メインエージェントがレポートに直接組み込める


## Pattern 7: コード生成・実装仕様エージェント

大量のコード生成やサービス別の仕様生成を並列化する。

### 対象スキル

design-implementation, generate-scalardb-code, generate-test-specs

### 使用方法

```
# サービス別に並列でコード生成（1つのメッセージで複数Task呼び出し）
Task(
  subagent_type="general-purpose",
  prompt="以下の設計仕様を読み込み、{service_name}サービスのリポジトリ実装コードを生成:

    入力ファイル:
    - reports/06_implementation/repository-interfaces-spec.md
    - reports/03_design/scalardb-schema.md

    生成ルール:
    - .claude/rules/scalardb-coding-patterns.md に準拠
    - エディション: {edition} (work/{project}/scalardb-edition-config.md 参照)

    出力: Javaソースコードをそのまま返してください。",
  description="{service_name} リポジトリ実装生成"
)
```

### 並列生成パターン

複数サービスのコードを同時に生成:

```
# サービスAとサービスBを並列生成
Task(subagent_type="general-purpose", prompt="order-serviceのエンティティ/VOを生成...", description="order-service生成")
Task(subagent_type="general-purpose", prompt="customer-serviceのエンティティ/VOを生成...", description="customer-service生成")
```

### ベストプラクティス

- **サービス単位で分割**: 1エージェント1サービスで並列化
- **ルールファイルのパスを明示**: エージェントが自力でルールを読み込めるようにする
- **エディション情報を明示的に渡す**: コード生成の分岐に必須
- **生成コードの結合はメインエージェントで**: ファイル書き出しと整合性チェックはメインで実行


## Pattern 8: ユーティリティ・レポートエージェント

Mermaid検証、レポートコンパイル、グラフ操作等のバッチ処理を効率化する。

### 対象スキル

compile-report, fix-mermaid, render-mermaid, build-graph, visualize-graph, estimate-cost, scalardb-sizing-estimator

### 使用方法

```
# Mermaid検証: ファイル群を分割して並列チェック
Task(
  subagent_type="Explore",
  prompt="以下のディレクトリ内のMarkdownファイルからMermaid図を抽出し、構文エラーを検出:
    対象: reports/03_design/
    チェック項目:
    1. 日本語テキストがダブルクオートで囲まれているか
    2. サブグラフ名がダブルクオートで囲まれているか
    3. ノードIDが英数字のみか
    結果を {ファイルパス, 行番号, エラー内容, 修正案} 形式で返してください。",
  description="Mermaid構文チェック (03_design)"
)
```

### レポートコンパイルパターン

```
# 各フェーズの出力を並列で要約収集し、最終レポートに統合
Task(subagent_type="Explore", prompt="reports/01_analysis/ の全ファイルを読み、主要findings3-5個を抽出...", description="Phase1要約")
Task(subagent_type="Explore", prompt="reports/02_evaluation/ の全ファイルを読み、評価スコアと改善提案を抽出...", description="Phase2要約")
Task(subagent_type="Explore", prompt="reports/03_design/ の全ファイルを読み、設計決定と構成図を抽出...", description="Phase3要約")
```

### ベストプラクティス

- **ディレクトリ単位で分割**: reports/01_analysis, reports/02_evaluation 等をそれぞれ別エージェントに
- **検証系は結果フォーマットを統一**: エラー一覧テーブル形式で統一すると集約が容易
- **レポートコンパイルは要約を先に**: 全文をメインに送らず、要約→テンプレート埋め込みの2段階で


## パターン一覧

| パターン | 対象カテゴリ | 対象スキル数 | サブエージェント種別 |
|---------|------------|------------|-------------------|
| 1. コードベース探索 | 調査・分析 | 4 | Explore |
| 2. 前フェーズ出力読み込み | 設計・生成 | 11 | Explore |
| 3. Context7 ドキュメント取得 | ScalarDB関連 | 4 | general-purpose |
| 4. レビュー | レビュー | 1 | Explore |
| 5. セキュリティ分析 | セキュリティ | 2 | Explore |
| 6. データモデル分析 | データ分析 | 3 | Explore |
| 7. コード生成・実装仕様 | 生成 | 3 | general-purpose |
| 8. ユーティリティ・レポート | ユーティリティ | 7 | Explore |
