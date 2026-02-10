# ScalarDB & Spring Boot Coding Examples

コンパクト版のRulesファイルから参照される詳細な実装例を格納するディレクトリです。

## 作成済み

- `value-object-examples.md` - 値オブジェクトの詳細実装例（ID, 金額, 列挙型）

## 未作成（必要時に作成）

コード生成スキル（`/generate-scalardb-code`）実行時に、以下のファイルが必要になった場合に作成します。
基本的なパターンは `.claude/rules/scalardb-coding-patterns.md` および `.claude/rules/spring-boot-integration.md` で十分です。

### ScalarDB Patterns
- `entity-examples.md` - エンティティ/集約ルートの詳細実装例
- `repository-examples.md` - リポジトリパターンの詳細実装例
- `transaction-examples.md` - トランザクション管理の詳細例
- `config-examples.md` - ScalarDB設定の詳細例
- `exception-examples.md` - 例外ハンドリングの詳細例

### Spring Boot Integration
- `spring-boot-dependencies.md` - 依存関係の完全版
- `spring-boot-service.md` - アプリケーションサービスの詳細例
- `spring-boot-controller.md` - RESTコントローラーの詳細例
- `spring-boot-events.md` - イベント駆動の詳細実装
- `spring-boot-mapping.md` - MapStructマッピングの詳細例
- `spring-boot-testing.md` - テストパターンの詳細例
- `spring-boot-config.md` - Spring Boot設定の詳細
- `spring-boot-k8s.md` - Kubernetes設定の詳細

## 使用方法

Compact版Rulesファイルの各セクション末尾にある参照リンクから、必要時にのみReadツールで読み込んでください。
