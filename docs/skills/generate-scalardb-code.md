# /generate-scalardb-code — ScalarDBコード生成

**カテゴリ**: Code Generation & Test（コード生成・テスト） | **Phase 8**

設計仕様からScalarDB/Spring Bootのコードを自動生成します。エンティティ、リポジトリ、サービス、コントローラーを出力します。

## 使用方法

```bash
/generate-scalardb-code ./path/to/source
```

## 前提条件

### 必須ルール（自動読み込み）
- `.claude/rules/scalardb-coding-patterns.md` — コーディングパターン
- `.claude/rules/spring-boot-integration.md` — Spring Boot統合パターン
- `.claude/rules/scalardb-edition-profiles.md` — エディションプロファイル

### 必須入力
- `reports/06_implementation/domain-services-spec.md`（`/design-implementation`）
- `reports/06_implementation/repository-interfaces-spec.md`

### 推奨
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`）
- `reports/03_design/scalardb-schema.md`（`/design-scalardb`）
- `reports/03_design/scalardb-app-patterns.md`（`/design-scalardb-app-patterns`）

## 生成対象

1. **値オブジェクト** — ID、Money、Quantity等の不変オブジェクト（`record`使用）
2. **エンティティ** — 集約ルート、子エンティティ（`create()`/`reconstitute()`パターン）
3. **ドメインイベント** — Created、Updated、Deleted等
4. **例外クラス** — ドメイン固有の例外
5. **リポジトリ** — インターフェース（ドメイン層）+ ScalarDB実装（インフラ層）
6. **アプリケーションサービス** — ユースケース実装
7. **コントローラー** — REST API実装
8. **設定ファイル** — application.yml、scalardb.properties、build.gradle
9. **テストコード** — ユニットテスト、統合テスト

## 出力先

```
generated/{service}/
├── domain/model/           # エンティティ、値オブジェクト
├── domain/service/         # ドメインサービス
├── application/            # アプリケーションサービス、DTO
├── infrastructure/         # リポジトリ実装、設定
├── presentation/           # コントローラー
└── src/test/               # テストコード
```

## エディション別コード生成

| コンポーネント | OSS | Enterprise Standard/Premium |
|-------------|-----|---------------------------|
| リポジトリ実装 | Core API（Get/Put/Delete/Scan） | SQL Interface or Spring Data JDBC |
| 設定ファイル | `TransactionFactory.create()` | Cluster Client接続 |
| 依存関係 | `scalardb:3.14.0` | `scalardb-cluster-java-client-sdk:3.14.0` |

## 関連スキル

- 前提: [/design-implementation](design-implementation.md), [/select-scalardb-edition](select-scalardb-edition.md)
- レビュー: [/review-scalardb --mode=code](review-scalardb.md)
