---
name: generate-scalardb-code
description: ScalarDBコード生成エージェント - 設計仕様からScalarDB/Spring Bootのコードを自動生成。エンティティ、リポジトリ、サービス、コントローラーを出力。/generate-scalardb-code [対象パス] で呼び出し。
user_invocable: true
---

# ScalarDB Code Generation Agent

設計仕様からScalarDB/Spring Bootのコードを自動生成するエージェントです。

## 概要

このエージェントは、設計ドキュメントから以下のコードを生成します：

1. **値オブジェクト** - ID、Money、Quantity等の不変オブジェクト
2. **エンティティ** - 集約ルート、子エンティティ
3. **ドメインイベント** - Created、Updated、Deleted等
4. **例外クラス** - ドメイン固有の例外
5. **リポジトリ** - インターフェースとScalarDB実装
6. **アプリケーションサービス** - ユースケース実装
7. **コントローラー** - REST API実装
8. **設定ファイル** - application.yml、scalardb.properties、build.gradle
9. **テストコード** - ユニットテスト、統合テスト

## 前提条件

### 必須ルール（自動読み込み）
以下のルールファイルを必ず参照してください：

- `.claude/rules/scalardb-coding-patterns.md` - ScalarDBコーディングパターン
- `.claude/rules/spring-boot-integration.md` - Spring Boot統合パターン

### 必須入力ファイル
以下のファイルが存在すること：

- `reports/06_implementation/domain-services-spec.md` ← /design-implementation
- `reports/06_implementation/value-objects-spec.md` ← /design-implementation
- `reports/06_implementation/repository-interfaces-spec.md` ← /design-implementation
- `reports/03_design/scalardb-schema.md` ← /design-scalardb

### 推奨入力ファイル
- `reports/01_analysis/ubiquitous-language.md` ← /analyze-system
- `reports/03_design/bounded-contexts-redesign.md` ← /ddd-redesign

## 出力先ディレクトリ

結果は `generated/{service-name}/` に出力します。

```
generated/{service-name}/
├── src/main/java/com/example/{service}/
│   ├── {ServiceName}Application.java
│   ├── domain/
│   │   ├── model/
│   │   │   ├── {Entity}.java
│   │   │   └── {ValueObject}.java
│   │   ├── repository/
│   │   │   └── {Entity}Repository.java
│   │   ├── event/
│   │   │   └── {Entity}CreatedEvent.java
│   │   └── exception/
│   │       └── {Entity}NotFoundException.java
│   ├── application/
│   │   ├── service/
│   │   │   └── {Entity}ApplicationService.java
│   │   ├── command/
│   │   │   └── Create{Entity}Command.java
│   │   └── dto/
│   │       └── {Entity}Dto.java
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   └── ScalarDb{Entity}Repository.java
│   │   ├── messaging/
│   │   │   └── Kafka{Entity}EventPublisher.java
│   │   └── config/
│   │       └── ScalarDbConfig.java
│   └── presentation/
│       ├── rest/
│       │   └── {Entity}Controller.java
│       ├── request/
│       │   └── Create{Entity}Request.java
│       └── response/
│           └── {Entity}Response.java
├── src/main/resources/
│   ├── application.yml
│   └── scalardb.properties
├── src/test/java/
│   └── ...
├── build.gradle
├── Dockerfile
└── k8s/
    └── deployment.yaml
```

## 実行プロンプト

あなたはScalarDBとSpring Bootに精通したコード生成エージェントです。
設計仕様に基づいて、本番環境で動作するコードを生成してください。

### Step 0: ルールの読み込み

**重要**: コード生成前に必ず以下のルールを読み込んでください。

```
Read .claude/rules/scalardb-coding-patterns.md
Read .claude/rules/spring-boot-integration.md
```

これらのルールには：
- プロジェクト構造
- 命名規則
- コードパターン（値オブジェクト、エンティティ、リポジトリ）
- Spring Boot設定
- テストパターン

が含まれています。ルールに従ってコードを生成してください。

### Step 1: 設計仕様の読み込み

以下のファイルから情報を抽出：

1. **ドメインサービス仕様** (`domain-services-spec.md`)
   - サービス一覧
   - メソッドシグネチャ
   - バリデーションルール
   - ビジネスロジック

2. **値オブジェクト仕様** (`value-objects-spec.md`)
   - 値オブジェクト定義
   - バリデーション
   - ファクトリメソッド
   - 操作メソッド

3. **リポジトリ仕様** (`repository-interfaces-spec.md`)
   - メソッド定義
   - ScalarDBクエリ
   - キャッシュ設定

4. **ScalarDBスキーマ** (`scalardb-schema.md`)
   - Namespace
   - テーブル定義
   - カラム型
   - インデックス

### Step 2: プロジェクト構造の生成

サービスごとに以下のディレクトリ構造を作成：

```bash
mkdir -p generated/{service-name}/src/main/java/com/example/{service}/{domain,application,infrastructure,presentation}
mkdir -p generated/{service-name}/src/main/resources
mkdir -p generated/{service-name}/src/test/java
mkdir -p generated/{service-name}/k8s
```

### Step 3: ビルド設定の生成

**出力**: `generated/{service-name}/build.gradle`

ルール `.claude/rules/spring-boot-integration.md` の「依存関係」セクションに従い、
build.gradleを生成してください。

### Step 4: 値オブジェクトの生成

**出力**: `generated/{service-name}/src/main/java/.../domain/model/`

ルール `.claude/rules/scalardb-coding-patterns.md` の「値オブジェクト実装パターン」に従い、
各値オブジェクトを生成してください。

生成するクラス：
- ID値オブジェクト (OrderId, CustomerId, ProductId等)
- 金額値オブジェクト (Money)
- 数量値オブジェクト (Quantity)
- 列挙型 (OrderStatus等)
- 住所等の複合値オブジェクト (Address)

### Step 5: エンティティの生成

**出力**: `generated/{service-name}/src/main/java/.../domain/model/`

ルール `.claude/rules/scalardb-coding-patterns.md` の「エンティティ実装パターン」に従い、
集約ルートと子エンティティを生成してください。

必須要素：
- privateコンストラクタ
- ファクトリメソッド (`create()`)
- 復元メソッド (`reconstitute()`)
- ドメインイベント登録
- 楽観ロック用version

### Step 6: ドメインイベントの生成

**出力**: `generated/{service-name}/src/main/java/.../domain/event/`

各エンティティの操作に対応するドメインイベントを生成：
- {Entity}CreatedEvent
- {Entity}UpdatedEvent
- {Entity}DeletedEvent
- {Entity}StatusChangedEvent

### Step 7: 例外クラスの生成

**出力**: `generated/{service-name}/src/main/java/.../domain/exception/`

ドメイン例外を生成：
- {Entity}NotFoundException
- Invalid{Entity}Exception
- {BusinessRule}ViolationException

### Step 8: リポジトリの生成

**出力**:
- `generated/{service-name}/src/main/java/.../domain/repository/{Entity}Repository.java`
- `generated/{service-name}/src/main/java/.../infrastructure/persistence/ScalarDb{Entity}Repository.java`

ルール `.claude/rules/scalardb-coding-patterns.md` の「リポジトリ実装パターン」に従い、
インターフェースとScalarDB実装を生成してください。

ScalarDB実装の必須要素：
- トランザクション管理
- Get/Scan/Put/Delete操作
- 楽観ロックチェック
- 例外ハンドリング

### Step 9: アプリケーションサービスの生成

**出力**: `generated/{service-name}/src/main/java/.../application/service/`

ルール `.claude/rules/spring-boot-integration.md` の「アプリケーションサービス」に従い、
ユースケースを実装するサービスを生成してください。

必須要素：
- コマンド/クエリの分離
- `@Transactional` アノテーション
- バリデーション (`@Valid`)
- ドメインイベントのパブリッシュ

### Step 10: コントローラーの生成

**出力**: `generated/{service-name}/src/main/java/.../presentation/rest/`

ルール `.claude/rules/spring-boot-integration.md` の「コントローラー」に従い、
REST APIエンドポイントを生成してください。

必須要素：
- OpenAPIアノテーション
- バリデーション
- 適切なHTTPステータス
- エラーハンドリング

### Step 11: 設定ファイルの生成

**出力**:
- `generated/{service-name}/src/main/resources/application.yml`
- `generated/{service-name}/src/main/resources/scalardb.properties`

ルールに従い、設定ファイルを生成してください。

### Step 12: Dockerとk8sの生成

**出力**:
- `generated/{service-name}/Dockerfile`
- `generated/{service-name}/k8s/deployment.yaml`

ルール `.claude/rules/spring-boot-integration.md` の「Dockerfile」「Kubernetes マニフェスト」に従い、
デプロイ用ファイルを生成してください。

### Step 13: テストコードの生成

**出力**: `generated/{service-name}/src/test/java/`

以下のテストを生成：
- 値オブジェクトのユニットテスト
- エンティティのユニットテスト
- アプリケーションサービスの統合テスト
- コントローラーのAPIテスト

### Step 14: 生成サマリーの出力

**出力**: `generated/{service-name}/GENERATED.md`

生成したファイルの一覧と、次のステップ（手動で必要な作業）を記載：

```markdown
# 生成されたコード

## 生成日時
{timestamp}

## 生成元
- domain-services-spec.md
- value-objects-spec.md
- repository-interfaces-spec.md
- scalardb-schema.md

## 生成ファイル一覧
[ファイルリスト]

## 次のステップ
1. build.gradleの依存関係バージョン確認
2. scalardb.propertiesの接続情報を環境に合わせて設定
3. ScalarDBスキーマの作成（schema-loader使用）
4. Kafkaトピックの作成
5. テストの実行
6. Docker イメージのビルドとプッシュ
```

## オプション

### --service={service-name}
特定のサービスのみ生成

### --output={output-dir}
出力ディレクトリを指定（デフォルト: `generated/`）

### --skip-tests
テストコード生成をスキップ

### --skip-k8s
Kubernetes マニフェスト生成をスキップ

## 使用例

### 基本的な使用
```
/generate-scalardb-code ./reports
```

### 特定サービスのみ生成
```
/generate-scalardb-code ./reports --service=order-service
```

### カスタム出力先
```
/generate-scalardb-code ./reports --output=./src
```

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/design-implementation` | 実装仕様生成（入力） |
| `/design-scalardb` | ScalarDBスキーマ設計（入力） |
| `/generate-test-specs` | テスト仕様生成（補完） |

## 注意事項

- 生成されたコードは直接使用可能ですが、プロジェクト固有の調整が必要な場合があります
- 環境依存の設定（接続情報等）は環境変数またはSecretで管理してください
- ScalarDBスキーマは別途 schema-loader で作成してください
- 本番環境へのデプロイ前に、セキュリティレビューを行ってください
