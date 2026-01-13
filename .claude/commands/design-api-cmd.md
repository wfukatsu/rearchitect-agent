---
description: API設計エージェント - リファクタリング後のマイクロサービスAPI設計。REST/GraphQL/gRPC/AsyncAPIの仕様書、API Gateway設計、認証・認可設計を策定。
argument-hint: [対象パス]
---

# API Design Agent

リファクタリング後のマイクロサービスAPIを設計するエージェントです。

## 概要

このエージェントは、マイクロサービス設計の結果をもとに、以下を策定します：

1. **API仕様設計** - REST/GraphQL/gRPC/AsyncAPIの仕様書
2. **API Gateway設計** - ルーティング、認証、レート制限
3. **認証・認可設計** - OAuth2/OIDC、RBAC/ABAC
4. **API管理戦略** - バージョニング、ドキュメント、テスト

## 前提条件

以下の中間ファイルが存在すること：
- `01_analysis/` 配下の分析結果
- `03_design/target-architecture.md`

## 出力ファイル

```
reports/03_design/
├── api-design-overview.md       # API設計概要
├── api-specifications/          # API仕様書ディレクトリ
│   ├── openapi/                 # OpenAPI (REST) 仕様
│   ├── graphql/                 # GraphQL スキーマ
│   ├── grpc/                    # gRPC プロトコル定義
│   └── asyncapi/                # AsyncAPI (イベント) 仕様
├── api-gateway-design.md        # API Gateway設計
└── api-security-design.md       # 認証・認可設計
```

## 実行例

```bash
# 基本的な使い方
/design-api ./src

# マイクロサービス設計後に実行
/design-microservices ./src
/design-api ./src
```

## 設計内容

### API通信パターン

| パターン | 適用条件 | 実装技術 |
|---------|---------|---------|
| REST | CRUD操作、外部公開 | OpenAPI 3.1 |
| GraphQL | 複雑なクエリ、BFF | Apollo/Hasura |
| gRPC | 内部通信、高性能 | Protocol Buffers |
| AsyncAPI | イベント駆動 | Kafka/RabbitMQ |

### API Gateway機能

- ルーティング
- 認証・認可（JWT、API Key、mTLS）
- レート制限
- リクエスト/レスポンス変換
- ログ・メトリクス

### 認証・認可

- OAuth2/OIDC（Keycloak）
- JWT設計
- RBAC/ABAC
- スコープ設計
