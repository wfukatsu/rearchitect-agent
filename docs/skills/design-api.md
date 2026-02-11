# /design-api — API設計

**カテゴリ**: Design（設計） | **Phase 5.5**

リファクタリング後のマイクロサービスAPI設計を行います。REST/GraphQL/gRPC/AsyncAPIの仕様書、API Gateway設計、認証・認可設計を策定します。

## 使用方法

```bash
/design-api ./path/to/source
```

## 前提条件

### 必須
- `reports/03_design/target-architecture.md`（`/design-microservices`）

### 推奨
- `reports/03_design/scalardb-schema.md`（`/design-scalardb`）
- `reports/03_design/scalardb-architecture.md`
- `reports/01_analysis/system-overview.md`
- `reports/01_analysis/ubiquitous-language.md`

## 実行ステップ

1. **前提条件の検証** — 必須ファイルの存在確認
2. **API仕様設計** — REST（OpenAPI）/ GraphQL / gRPC（Protocol Buffers）/ AsyncAPIの仕様書生成
3. **API Gateway設計** — ルーティング、認証、レート制限
4. **認証・認可設計** — OAuth2/OIDC、RBAC/ABAC
5. **API管理戦略** — バージョニング、ドキュメント、テスト
6. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/api-design-overview.md` | API設計概要 |
| `reports/03_design/api-specifications/openapi/` | OpenAPI（REST）仕様ファイル |
| `reports/03_design/api-specifications/graphql/` | GraphQLスキーマファイル |
| `reports/03_design/api-specifications/grpc/` | gRPC Protobufファイル |
| `reports/03_design/api-specifications/asyncapi/` | AsyncAPI（イベント）仕様ファイル |

## 関連スキル

- 前提: [/design-microservices](design-microservices.md), [/design-scalardb](design-scalardb.md)
- 次のフェーズ: [/design-implementation](design-implementation.md)
