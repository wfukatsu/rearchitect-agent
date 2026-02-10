# ScalarDB Coding Patterns (Compact)

ScalarDBコーディングパターンの要点のみをまとめた簡素版。

## 1. プロジェクト構造

```
{service}/
├── domain/model/           # Entity, ValueObject, Repository IF
├── domain/service/         # DomainService
├── application/           # ApplicationService, Command, DTO
├── infrastructure/        # Repository実装, Config, Messaging
└── presentation/          # Controller, Request, Response
```

## 2. 命名規則

| 種類 | パターン | 例 |
|------|---------|-----|
| エンティティ | `{Name}` | `Order` |
| 値オブジェクト | `{Name}` | `OrderId`, `Money` |
| リポジトリIF | `{Entity}Repository` | `OrderRepository` |
| リポジトリ実装 | `ScalarDb{Entity}Repository` | `ScalarDbOrderRepository` |
| Namespace | `{service_name}` (snake_case) | `order_service` |
| Table | `{entity}s` (plural, snake_case) | `orders` |

## 3. 値オブジェクト原則

### 必須要件
- **不変性**: `record` または `final` fields 使用
- **バリデーション**: コンストラクタで実行
- **ファクトリメソッド**: `of()`, `generate()` 提供
- **equals/hashCode**: 値で比較

### パターン
```java
public record OrderId(String value) {
    public OrderId { /* validation */ }
    public static OrderId generate() { /* UUID */ }
    public static OrderId of(String value) { /* ... */ }
}
```

📖 **詳細例**: `.claude/rules/examples/value-object-examples.md`

## 4. エンティティ原則

### 必須要件
- **ID識別**: 値オブジェクトのIDで識別
- **ファクトリメソッド**: `create()` で新規作成
- **復元メソッド**: `reconstitute()` で永続化データから復元
- **ドメインイベント**: `List<DomainEvent>` で管理
- **楽観ロック**: `version` フィールド

### 集約ルートパターン
```java
public class Order {
    private final OrderId id;
    private final List<DomainEvent> domainEvents = new ArrayList<>();

    public static Order create(...) { /* ... */ }
    public static Order reconstitute(...) { /* ... */ }
    private void registerEvent(DomainEvent event) { /* ... */ }
}
```


## 5. リポジトリ原則

### インターフェース（ドメイン層）
```java
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    Order save(Order order);
    void delete(OrderId id);
}
```

### ScalarDB実装（インフラ層）
- **トランザクション管理**: `DistributedTransactionManager` 使用
- **楽観ロックチェック**: 更新時に `version` 検証
- **例外変換**: `TransactionException` → ドメイン例外


## 6. トランザクション管理

### パターン
- **単一サービス**: `DistributedTransaction`
- **サービス間**: `TwoPhaseCommitTransaction`

```java
DistributedTransaction tx = transactionManager.start();
try {
    // CRUD operations
    tx.commit();
} catch (Exception e) {
    tx.abort();
    throw new RuntimeException(...);
}
```


## 7. ScalarDB設定

> **エディション別の設定が異なります。** 以下の構成で記載しています:
> - §7 基本例（OSS/Community向けデフォルト）
> - §7A: OSS/Community Edition 詳細
> - §7B: Enterprise Standard/Premium Edition 詳細
>
> Enterprise Standard/Premium Edition を使用する場合は **§7B** を参照してください。

### scalardb.properties（OSS/Community デフォルト）
```properties
scalar.db.transaction_manager=consensus-commit
scalar.db.storage=jdbc
scalar.db.contact_points=jdbc:postgresql://...
scalar.db.consensus_commit.isolation_level=SERIALIZABLE
```

### Spring Boot Config（OSS/Community デフォルト）
```java
@Bean
public DistributedTransactionManager transactionManager() {
    Properties props = loadProperties("scalardb.properties");
    return TransactionFactory.create(props).getTransactionManager();
}
```


### 7A. OSS/Community Edition（組み込みモード）

OSS版はアプリケーションに直接組み込むJavaライブラリとして使用。Clusterなし。

```properties
# scalar.db.transaction_manager=consensus-commit（デフォルト）
scalar.db.storage=jdbc
scalar.db.contact_points=jdbc:postgresql://localhost:5432/mydb
scalar.db.username=postgres
scalar.db.password=postgres
scalar.db.consensus_commit.isolation_level=SERIALIZABLE
```

```java
// OSS/Community: TransactionFactory で直接生成
Properties props = new Properties();
props.load(new FileInputStream("scalardb.properties"));
TransactionFactory factory = TransactionFactory.create(props);
DistributedTransactionManager txManager = factory.getTransactionManager();
// アプリケーション内でライフサイクル管理（close()必須）
```

**制約**: SQL Interface / Spring Data JDBC は使用不可。Core Java API のみ。

### 7B. Enterprise Standard/Premium Edition（Cluster Client モード）

Enterprise版はScalarDB Clusterに接続するクライアントSDKとして使用。

```properties
# Cluster Client 設定
scalar.db.transaction_manager=cluster
scalar.db.contact_points=indirect:scalardb-cluster-envoy.default.svc.cluster.local
scalar.db.contact_port=60053
scalar.db.cluster.auth.enabled=true
scalar.db.cluster.auth.username=admin
scalar.db.cluster.auth.password=admin_password
```

```java
// Enterprise: SQL Interface 統合（Enterprise Standard/Premium のみ）
@Configuration
public class ScalarDbSqlConfig {
    @Bean
    public SqlSessionFactory sqlSessionFactory() {
        return SqlSessionFactory.builder()
            .withPropertiesFile("scalardb-sql.properties")
            .build();
    }
}
```

```java
// Enterprise: Spring Data JDBC 統合（Enterprise Standard/Premium のみ）
// build.gradle: implementation 'com.scalar-labs:scalardb-sql-spring-data:3.14.0'
// Spring Data リポジトリが自動生成される
```

📖 **エディション詳細**: `.claude/rules/scalardb-edition-profiles.md`

## 8. 例外ハンドリング

### ドメイン例外
```java
public abstract class DomainException extends RuntimeException {
    private final String errorCode;
}
```

### グローバルハンドラ
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ErrorResponse> handle404(...) { /* ... */ }
}
```


## 9. チェックリスト

### 値オブジェクト
- [ ] `record` 使用またはimmutable
- [ ] コンストラクタでバリデーション
- [ ] ファクトリメソッド提供

### エンティティ
- [ ] ファクトリメソッド (`create`)
- [ ] 復元メソッド (`reconstitute`)
- [ ] ドメインイベント管理
- [ ] `version` フィールド

### リポジトリ
- [ ] インターフェースはドメイン層
- [ ] 実装はインフラ層
- [ ] トランザクション管理
- [ ] 楽観ロックチェック

---
