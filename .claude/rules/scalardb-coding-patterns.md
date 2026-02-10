# ScalarDB Coding Patterns (Compact)

ScalarDBコーディングパターンの要点のみをまとめた簡素版。詳細な実装例は `examples/` 参照。

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

📖 **詳細例**: `.claude/rules/examples/entity-examples.md`

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

📖 **詳細例**: `.claude/rules/examples/repository-examples.md`

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

📖 **詳細例**: `.claude/rules/examples/transaction-examples.md`

## 7. ScalarDB設定

### scalardb.properties
```properties
scalar.db.transaction_manager=consensus-commit
scalar.db.storage=jdbc
scalar.db.contact_points=jdbc:postgresql://...
scalar.db.consensus_commit.isolation_level=SERIALIZABLE
```

### Spring Boot Config
```java
@Bean
public DistributedTransactionManager transactionManager() {
    Properties props = loadProperties("scalardb.properties");
    return TransactionFactory.create(props).getTransactionManager();
}
```

📖 **詳細例**: `.claude/rules/examples/config-examples.md`

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

📖 **詳細例**: `.claude/rules/examples/exception-examples.md`

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
