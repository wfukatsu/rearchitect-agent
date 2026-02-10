# Spring Boot Integration Patterns (Compact)

Spring BootとScalarDB統合の要点。

## 1. 依存関係

### build.gradle（エディション別）

```groovy
// 共通依存関係
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.kafka:spring-kafka'
    implementation 'org.mapstruct:mapstruct:1.5.5.Final'
    // Test
    testImplementation 'org.testcontainers:testcontainers:1.19.3'
    testImplementation 'org.testcontainers:postgresql:1.19.3'
}
```

```groovy
// OSS/Community Edition
dependencies {
    implementation 'com.scalar-labs:scalardb:3.14.0'
}
```

```groovy
// Enterprise Standard/Premium (Cluster Client SDK)
dependencies {
    implementation 'com.scalar-labs:scalardb-cluster-java-client-sdk:3.14.0'
}
```

```groovy
// Enterprise + SQL Interface / Spring Data JDBC
dependencies {
    implementation 'com.scalar-labs:scalardb-cluster-java-client-sdk:3.14.0'
    implementation 'com.scalar-labs:scalardb-sql-spring-data:3.14.0'
}
```

📖 **エディション詳細**: `.claude/rules/scalardb-edition-profiles.md`

## 2. レイヤー構成

### Application Service
```java
@Service
@Validated
public class OrderApplicationService {
    @Transactional
    public OrderDto createOrder(@Valid CreateOrderCommand command) {
        // 1. Command → Domain変換
        // 2. Domain logic実行
        // 3. 永続化
        // 4. Event publish
        // 5. DTO変換
    }
}
```


## 3. Controller

### RESTコントローラー
```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
        @Valid @RequestBody CreateOrderRequest request) {
        // Command変換 → Service呼び出し → Response変換
    }
}
```


## 4. Event駆動

### Domain Event
```java
public interface DomainEvent {
    Instant occurredAt();
}

public record OrderCreatedEvent(OrderId orderId, ...) implements DomainEvent {}
```

### Kafka Publisher
```java
@Component
public class KafkaEventPublisher implements DomainEventPublisher {
    @Override
    public void publish(DomainEvent event) {
        String topic = resolveTopic(event);
        String payload = objectMapper.writeValueAsString(event);
        kafkaTemplate.send(topic, payload);
    }
}
```


## 5. MapStruct

### Mapper定義
```java
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface OrderMapper {
    @Mapping(target = "id", source = "id.value")
    OrderDto toDto(Order order);
}
```


## 6. テスト

### Testcontainers統合
```java
@SpringBootTest
@Testcontainers
public abstract class IntegrationTestBase {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(...);

    @Container
    static KafkaContainer kafka = new KafkaContainer(...);
}
```


## 7. 設定ファイル

### application.yml
```yaml
spring:
  application:
    name: order-service

scalardb:
  config-file: classpath:scalardb.properties

management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
```

### ScalarDB Config Bean（エディション別）

#### OSS/Community Edition
```java
@Configuration
public class ScalarDbConfig {
    @Bean
    public DistributedTransactionManager transactionManager() {
        Properties props = loadProperties("scalardb.properties");
        return TransactionFactory.create(props).getTransactionManager();
    }
}
```

#### Enterprise Standard/Premium Edition — SQL Interface
```java
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

#### Enterprise Standard/Premium Edition — Spring Data JDBC
```java
// build.gradle: implementation 'com.scalar-labs:scalardb-sql-spring-data:3.14.0'
// @EnableScalarDbRepositories でリポジトリ自動生成を有効化
@Configuration
@EnableScalarDbRepositories(basePackages = "com.example.order.infrastructure.persistence")
public class ScalarDbSpringDataConfig {
    // Spring Data JDBC が自動的にリポジトリ実装を生成
    // ScalarDbRepository<T, ID> を継承したインターフェースのみ定義すればよい
}
```

📖 **エディション詳細**: `.claude/rules/scalardb-edition-profiles.md`

## 8. Kubernetes

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:latest
          ports:
            - containerPort: 8080
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
```


## 9. チェックリスト

### 依存性注入
- [ ] コンストラクタインジェクション使用
- [ ] `@Service`, `@Repository`, `@Component` 付与
- [ ] インターフェースに対してプログラミング

### バリデーション
- [ ] `@Valid` 使用
- [ ] Bean Validationアノテーション設定
- [ ] カスタムバリデータ実装（必要時）

### テスト
- [ ] 単体テスト（モック使用）
- [ ] 統合テスト（Testcontainers使用）
- [ ] データセットアップ/クリーンアップ

### 監視
- [ ] Actuator有効化
- [ ] Prometheusメトリクス公開
- [ ] ヘルスチェック設定

---
