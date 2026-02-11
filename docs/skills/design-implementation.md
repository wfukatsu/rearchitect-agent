# /design-implementation — 実装設計

**カテゴリ**: Design（設計） | **Phase 6**

AIエージェントがコーディング可能なレベルの詳細実装仕様を生成します。ドメインサービス・リポジトリ・値オブジェクト・例外マッピングのメソッドシグネチャと実装詳細を策定します。

## 使用方法

```bash
/design-implementation ./path/to/source
```

## 前提条件

### 必須
- `reports/03_design/target-architecture.md`（`/design-microservices`）
- `reports/03_design/api-design-overview.md`（`/design-api`）

### 推奨
- `work/{project}/scalardb-edition-config.md`（`/select-scalardb-edition`）
- `reports/03_design/scalardb-schema.md`（`/design-scalardb`）
- `reports/03_design/scalardb-app-patterns.md`（`/design-scalardb-app-patterns`）
- `reports/03_design/bounded-contexts-redesign.md`（`/ddd-redesign`）
- `reports/03_design/aggregate-redesign.md`
- `reports/01_analysis/ubiquitous-language.md`

## 実行ステップ

1. **前提条件の検証** — 必須ファイルの存在確認
2. **ドメインサービス仕様** — メソッドシグネチャ、バリデーション、イベント発行、例外定義
3. **リポジトリインターフェース仕様** — メソッド、クエリ、キャッシュ、トランザクション（エディション別実装パターン含む）
4. **値オブジェクト詳細仕様** — 型定義、バリデーション、操作メソッド
5. **例外マッピング表** — ドメイン例外 → HTTPステータス変換
6. **Sagaオーケストレーション仕様** — ステップ定義、補償トランザクション
7. **API Gateway実装仕様** — Kong設定、認証プラグイン、レート制限、サーキットブレーカー
8. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/06_implementation/domain-services-spec.md` | ドメインサービス仕様 |
| `reports/06_implementation/repository-interfaces-spec.md` | リポジトリインターフェース仕様 |
| `reports/06_implementation/value-objects-spec.md` | 値オブジェクト詳細仕様 |
| `reports/06_implementation/exception-mapping-spec.md` | 例外マッピング表 |
| `reports/06_implementation/saga-orchestration-spec.md` | Sagaオーケストレーション仕様 |
| `reports/06_implementation/api-gateway-spec.md` | API Gateway実装仕様 |

## エディション別リポジトリ仕様

エディション設定が存在する場合、リポジトリインターフェース仕様にエディション別実装パターンを含めます:
- **OSS**: Core API直接使用（Get/Put/Delete/Scan）
- **Enterprise Standard/Premium**: SQL Interface or Spring Data JDBC

## 関連スキル

- 前提: [/design-microservices](design-microservices.md), [/design-api](design-api.md)
- 次のフェーズ: [/generate-test-specs](generate-test-specs.md), [/generate-scalardb-code](generate-scalardb-code.md)
