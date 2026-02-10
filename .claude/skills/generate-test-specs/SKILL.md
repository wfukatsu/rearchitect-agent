---
name: generate-test-specs
description: テスト仕様生成エージェント - AIエージェントがテストコードを実装可能なBDDシナリオ・ユニットテスト・統合テスト仕様を生成。Gherkin形式のシナリオとJUnit/Jest形式のテストケースを策定。/generate-test-specs [対象パス] で呼び出し。
user_invocable: true
---

# Test Specification Generator Agent

AIエージェントがテストコードを実装可能なレベルのテスト仕様を生成するエージェントです。

## 概要

このエージェントは、実装仕様から以下のテスト仕様を生成します：

1. **BDDシナリオ (Gherkin)** - ビジネス要件ベースのシナリオ
2. **ユニットテスト仕様** - クラス・メソッド単位のテスト
3. **統合テスト仕様** - サービス間連携のテスト
4. **エッジケース・エラーケース** - 境界値・異常系テスト
5. **パフォーマンステスト仕様** - 負荷・応答時間テスト

## 前提条件

以下のファイルが存在すること：

**必須:**
- `reports/06_implementation/domain-services-spec.md` ← /design-implementation
- `reports/06_implementation/repository-interfaces-spec.md` ← /design-implementation

**推奨:**
- `reports/06_implementation/value-objects-spec.md` ← /design-implementation
- `reports/06_implementation/exception-mapping.md` ← /design-implementation
- `reports/06_implementation/saga-orchestration-spec.md` ← /design-implementation
- `reports/03_design/api-specifications/` ← /design-api

## 出力先ディレクトリ

結果は `reports/07_test-specs/` に出力します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

```
reports/07_test-specs/
├── bdd-scenarios/              # Step 2完了時
│   ├── order-scenarios.feature
│   └── [domain]-scenarios.feature
├── unit-test-specs.md          # Step 3完了時
├── integration-test-specs.md   # Step 4完了時
├── edge-case-specs.md          # Step 5完了時
├── performance-test-specs.md   # Step 6完了時
└── test-data-requirements.md   # Step 7完了時
```

## 実行プロンプト

あなたはテスト設計の専門家です。AIエージェントがテストコードを実装可能な詳細仕様を生成してください。

### Step 0: 前提条件の検証

**重要**: 実行前に必ず前提条件を確認してください。

```
必須ファイルの確認:
├── reports/06_implementation/domain-services-spec.md    [必須]
└── reports/06_implementation/repository-interfaces-spec.md [必須]

推奨ファイルの確認:
├── reports/06_implementation/value-objects-spec.md      [推奨]
├── reports/06_implementation/exception-mapping.md       [推奨]
├── reports/06_implementation/saga-orchestration-spec.md [推奨]
└── reports/03_design/api-specifications/                [推奨]
```

**エラーハンドリング:**
- 必須ファイルが存在しない場合 → `/design-implementation` を先に実行するよう案内
- 推奨ファイルが存在しない場合 → 警告を表示して続行

### Step 1: 実装仕様の読み込み

前提ファイルから以下の情報を抽出：

1. **ドメインサービス** - メソッド、バリデーション、例外
2. **リポジトリ** - メソッド、クエリ
3. **値オブジェクト** - バリデーションルール
4. **例外** - 発生条件、HTTPマッピング
5. **Saga** - ステップ、補償トランザクション

### Step 2: BDDシナリオ (Gherkin) の生成

**出力**: `reports/07_test-specs/bdd-scenarios/[domain]-scenarios.feature`

各ドメインのビジネスシナリオをGherkin形式で出力：

```gherkin
# order-scenarios.feature

@order @acceptance
Feature: 注文管理
  ユーザーとして
  商品を注文したい
  購入手続きを完了するために

  Background:
    Given 以下の商品が存在する:
      | productId | name      | price | stock |
      | PROD-001  | 商品A     | 1000  | 100   |
      | PROD-002  | 商品B     | 2000  | 50    |
    And 顧客 "customer-123" が認証済みである

  # ==============================
  # 正常系シナリオ
  # ==============================

  @happy-path
  Scenario: 単一商品の注文を作成できる
    Given 商品 "PROD-001" の在庫が 100 個ある
    When 以下の注文を作成する:
      | productId | quantity |
      | PROD-001  | 2        |
    Then 注文が作成される
    And 注文ステータスは "PENDING" である
    And 合計金額は 2000 円である
    And 在庫が 98 個に減少する
    And "OrderCreated" イベントが発行される

  @happy-path
  Scenario: 複数商品の注文を作成できる
    Given 商品 "PROD-001" の在庫が 100 個ある
    And 商品 "PROD-002" の在庫が 50 個ある
    When 以下の注文を作成する:
      | productId | quantity |
      | PROD-001  | 2        |
      | PROD-002  | 3        |
    Then 注文が作成される
    And 合計金額は 8000 円である

  @happy-path
  Scenario: 注文をキャンセルできる
    Given 注文 "order-123" が "PENDING" ステータスで存在する
    When 注文 "order-123" をキャンセルする
    Then 注文ステータスは "CANCELLED" に変更される
    And 予約在庫が解放される
    And "OrderCancelled" イベントが発行される

  # ==============================
  # 異常系シナリオ
  # ==============================

  @error-case
  Scenario: 在庫不足の場合は注文作成に失敗する
    Given 商品 "PROD-001" の在庫が 5 個ある
    When 以下の注文を作成する:
      | productId | quantity |
      | PROD-001  | 10       |
    Then エラーコード "INSUFFICIENT_INVENTORY" が返される
    And 注文は作成されない
    And 在庫は変更されない

  @error-case
  Scenario: 存在しない商品の注文は失敗する
    When 以下の注文を作成する:
      | productId     | quantity |
      | NON-EXISTENT  | 1        |
    Then エラーコード "PRODUCT_NOT_FOUND" が返される

  @error-case
  Scenario: 数量0の注文は失敗する
    When 以下の注文を作成する:
      | productId | quantity |
      | PROD-001  | 0        |
    Then エラーコード "INVALID_ORDER" が返される
    And エラーメッセージに "数量は1以上" が含まれる

  @error-case
  Scenario: 既にキャンセル済みの注文は再キャンセルできない
    Given 注文 "order-123" が "CANCELLED" ステータスで存在する
    When 注文 "order-123" をキャンセルする
    Then エラーコード "ORDER_ALREADY_CANCELLED" が返される

  # ==============================
  # 境界値シナリオ
  # ==============================

  @boundary
  Scenario: 最大数量での注文
    Given 商品 "PROD-001" の在庫が 10000 個ある
    When 以下の注文を作成する:
      | productId | quantity |
      | PROD-001  | 9999     |
    Then 注文が作成される

  @boundary
  Scenario: 最大数量超過の注文は失敗
    When 以下の注文を作成する:
      | productId | quantity |
      | PROD-001  | 10000    |
    Then エラーコード "INVALID_ORDER" が返される
    And エラーメッセージに "数量は9999以下" が含まれる

  @boundary
  Scenario: 最大商品数での注文
    Given 100種類の商品が存在する
    When 100種類の商品を各1個ずつ注文する
    Then 注文が作成される

  @boundary
  Scenario: 商品数超過の注文は失敗
    Given 101種類の商品が存在する
    When 101種類の商品を各1個ずつ注文する
    Then エラーコード "INVALID_ORDER" が返される
    And エラーメッセージに "100件以下" が含まれる

  # ==============================
  # 並行処理シナリオ
  # ==============================

  @concurrency
  Scenario: 同時注文による在庫競合
    Given 商品 "PROD-001" の在庫が 10 個ある
    When 以下の注文が同時に実行される:
      | customerId    | productId | quantity |
      | customer-001  | PROD-001  | 8        |
      | customer-002  | PROD-001  | 8        |
    Then 1件の注文が成功する
    And 1件の注文は "INSUFFICIENT_INVENTORY" で失敗する
    And 在庫の整合性が保たれる

  @concurrency
  Scenario: 同一注文の同時更新
    Given 注文 "order-123" が "PENDING" ステータスで存在する
    When 以下の操作が同時に実行される:
      | operation | orderId   |
      | cancel    | order-123 |
      | confirm   | order-123 |
    Then 1件の操作が成功する
    And 1件の操作は "CONCURRENT_MODIFICATION" で失敗する
```

### Step 3: ユニットテスト仕様の生成

**出力**: `reports/07_test-specs/unit-test-specs.md`

```markdown
# ユニットテスト仕様

## Order Service

### OrderApplicationService

#### createOrder

| テストケース | Given | When | Then | Mock |
|------------|-------|------|------|------|
| 正常系_単一商品 | 顧客存在, 在庫十分 | createOrder(1商品) | 注文作成, イベント発行 | CustomerRepo, InventoryService |
| 正常系_複数商品 | 顧客存在, 全商品在庫十分 | createOrder(3商品) | 注文作成, 合計金額正確 | - |
| 異常系_顧客不在 | 顧客不存在 | createOrder | CustomerNotFoundException | CustomerRepo returns empty |
| 異常系_在庫不足 | 在庫 < 要求数量 | createOrder | InsufficientInventoryException | InventoryService throws |
| 異常系_空の商品リスト | items = [] | createOrder | InvalidOrderException | - |
| 異常系_数量0 | quantity = 0 | createOrder | InvalidOrderException | - |
| 異常系_数量マイナス | quantity = -1 | createOrder | InvalidOrderException | - |

```java
// テストクラステンプレート

@ExtendWith(MockitoExtension.class)
class OrderApplicationServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private CustomerRepository customerRepository;

    @Mock
    private InventoryService inventoryService;

    @Mock
    private EventPublisher eventPublisher;

    @InjectMocks
    private OrderApplicationService sut;

    @Nested
    @DisplayName("createOrder")
    class CreateOrderTest {

        @Test
        @DisplayName("正常系: 単一商品の注文を作成できる")
        void shouldCreateOrderWithSingleItem() {
            // Given
            CustomerId customerId = CustomerId.of("customer-123");
            ProductId productId = ProductId.of("product-456");
            CreateOrderCommand command = CreateOrderCommand.builder()
                .customerId(customerId)
                .items(List.of(
                    OrderItemCommand.of(productId, Quantity.of(2))
                ))
                .shippingAddress(testAddress())
                .build();

            when(customerRepository.findById(customerId))
                .thenReturn(Optional.of(testCustomer()));
            when(inventoryService.reserveInventory(any()))
                .thenReturn(ReservationResult.success("res-123"));

            // When
            Order result = sut.createOrder(command);

            // Then
            assertThat(result).isNotNull();
            assertThat(result.getStatus()).isEqualTo(OrderStatus.PENDING);
            assertThat(result.getItems()).hasSize(1);

            verify(orderRepository).save(any(Order.class));
            verify(eventPublisher).publish(any(OrderCreatedEvent.class));
        }

        @Test
        @DisplayName("異常系: 顧客が存在しない場合はCustomerNotFoundExceptionをスロー")
        void shouldThrowWhenCustomerNotFound() {
            // Given
            CustomerId customerId = CustomerId.of("non-existent");
            CreateOrderCommand command = CreateOrderCommand.builder()
                .customerId(customerId)
                .items(List.of(testOrderItem()))
                .shippingAddress(testAddress())
                .build();

            when(customerRepository.findById(customerId))
                .thenReturn(Optional.empty());

            // When & Then
            assertThatThrownBy(() -> sut.createOrder(command))
                .isInstanceOf(CustomerNotFoundException.class)
                .hasMessageContaining("non-existent");

            verify(orderRepository, never()).save(any());
            verify(eventPublisher, never()).publish(any());
        }

        @Test
        @DisplayName("異常系: 在庫不足の場合はInsufficientInventoryExceptionをスロー")
        void shouldThrowWhenInsufficientInventory() {
            // Given
            when(customerRepository.findById(any()))
                .thenReturn(Optional.of(testCustomer()));
            when(inventoryService.reserveInventory(any()))
                .thenThrow(new InsufficientInventoryException(
                    ProductId.of("prod-123"),
                    Quantity.of(10),
                    Quantity.of(3)
                ));

            // When & Then
            assertThatThrownBy(() -> sut.createOrder(testCommand()))
                .isInstanceOf(InsufficientInventoryException.class);

            verify(orderRepository, never()).save(any());
        }
    }
}
```

### Order (集約ルート)

| テストケース | Given | When | Then |
|------------|-------|------|------|
| 作成_正常 | 有効なパラメータ | Order.create() | Orderインスタンス, ステータスPENDING |
| キャンセル_PENDING | status=PENDING | cancel() | status=CANCELLED, イベント記録 |
| キャンセル_CONFIRMED | status=CONFIRMED | cancel() | status=CANCELLED |
| キャンセル_SHIPPED | status=SHIPPED | cancel() | InvalidStateTransitionException |
| キャンセル_既にCANCELLED | status=CANCELLED | cancel() | OrderAlreadyCancelledException |
| 確定_PENDING | status=PENDING | confirm() | status=CONFIRMED |
| 確定_CANCELLED | status=CANCELLED | confirm() | InvalidStateTransitionException |

```java
@DisplayName("Order 集約ルートのテスト")
class OrderTest {

    @Nested
    @DisplayName("cancel")
    class CancelTest {

        @Test
        @DisplayName("PENDINGステータスの注文をキャンセルできる")
        void canCancelPendingOrder() {
            // Given
            Order order = createOrderWithStatus(OrderStatus.PENDING);

            // When
            order.cancel("顧客都合");

            // Then
            assertThat(order.getStatus()).isEqualTo(OrderStatus.CANCELLED);
            assertThat(order.getDomainEvents())
                .hasSize(1)
                .first()
                .isInstanceOf(OrderCancelledEvent.class);
        }

        @Test
        @DisplayName("SHIPPEDステータスの注文はキャンセルできない")
        void cannotCancelShippedOrder() {
            // Given
            Order order = createOrderWithStatus(OrderStatus.SHIPPED);

            // When & Then
            assertThatThrownBy(() -> order.cancel("顧客都合"))
                .isInstanceOf(InvalidStateTransitionException.class)
                .hasMessageContaining("SHIPPED")
                .hasMessageContaining("CANCELLED");
        }
    }
}
```

### 値オブジェクトテスト

#### Money

| テストケース | 入力 | 期待結果 |
|------------|-----|---------|
| 生成_正常 | 1000, JPY | Moneyインスタンス |
| 生成_0円 | 0, JPY | Moneyインスタンス |
| 生成_負の金額 | -100, JPY | IllegalArgumentException |
| 生成_上限超過 | 10^12, JPY | IllegalArgumentException |
| 加算_同一通貨 | 1000 + 500 | 1500 |
| 加算_異なる通貨 | 1000 JPY + 10 USD | CurrencyMismatchException |
| 減算_結果正 | 1000 - 300 | 700 |
| 減算_結果負 | 100 - 200 | NegativeMoneyException |
| 乗算 | 1000 * 1.1 | 1100 (HALF_UP) |
| 等価性 | 同額同通貨 | true |

```java
@DisplayName("Money 値オブジェクトのテスト")
class MoneyTest {

    @Test
    @DisplayName("正の金額でMoneyを生成できる")
    void canCreateWithPositiveAmount() {
        Money money = Money.of(1000);
        assertThat(money.amount()).isEqualTo(1000);
        assertThat(money.currency()).isEqualTo(Currency.JPY);
    }

    @Test
    @DisplayName("負の金額ではIllegalArgumentExceptionをスロー")
    void throwsForNegativeAmount() {
        assertThatThrownBy(() -> Money.of(-100))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("金額は0以上");
    }

    @ParameterizedTest
    @CsvSource({
        "1000, 500, 1500",
        "0, 100, 100",
        "999999999999, 0, 999999999999"
    })
    @DisplayName("同一通貨の加算")
    void addSameCurrency(long a, long b, long expected) {
        Money result = Money.of(a).add(Money.of(b));
        assertThat(result.amount()).isEqualTo(expected);
    }

    @Test
    @DisplayName("異なる通貨の加算はCurrencyMismatchExceptionをスロー")
    void throwsForDifferentCurrency() {
        Money jpy = Money.of(1000, Currency.JPY);
        Money usd = Money.of(10, Currency.USD);

        assertThatThrownBy(() -> jpy.add(usd))
            .isInstanceOf(CurrencyMismatchException.class);
    }
}
```
```

### Step 4: 統合テスト仕様の生成

**出力**: `reports/07_test-specs/integration-test-specs.md`

```markdown
# 統合テスト仕様

## API統合テスト

### Order API

| エンドポイント | メソッド | シナリオ | 期待ステータス | 検証項目 |
|--------------|--------|---------|--------------|---------|
| /api/v1/orders | POST | 正常な注文作成 | 201 | Location, Body |
| /api/v1/orders | POST | 認証なし | 401 | エラーレスポンス |
| /api/v1/orders | POST | 無効なリクエスト | 400 | バリデーションエラー |
| /api/v1/orders | POST | 在庫不足 | 422 | ビジネスエラー |
| /api/v1/orders/{id} | GET | 存在する注文 | 200 | 注文詳細 |
| /api/v1/orders/{id} | GET | 存在しない注文 | 404 | NOT_FOUND |
| /api/v1/orders/{id} | GET | 他人の注文 | 403 | FORBIDDEN |
| /api/v1/orders | GET | 一覧取得 | 200 | ページング, フィルタ |

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class OrderApiIntegrationTest {

    @Container
    static ScalarDbContainer scalarDb = new ScalarDbContainer();

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private OrderRepository orderRepository;

    @BeforeEach
    void setUp() {
        // テストデータ初期化
    }

    @Nested
    @DisplayName("POST /api/v1/orders")
    class CreateOrderTest {

        @Test
        @DisplayName("正常: 注文を作成できる")
        void shouldCreateOrder() {
            // Given
            String token = getAuthToken("customer-123");
            CreateOrderRequest request = CreateOrderRequest.builder()
                .items(List.of(new OrderItemRequest("prod-001", 2)))
                .shippingAddress(testAddress())
                .build();

            // When
            ResponseEntity<OrderResponse> response = restTemplate.exchange(
                "/api/v1/orders",
                HttpMethod.POST,
                new HttpEntity<>(request, authHeaders(token)),
                OrderResponse.class
            );

            // Then
            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
            assertThat(response.getHeaders().getLocation()).isNotNull();

            OrderResponse body = response.getBody();
            assertThat(body.id()).isNotNull();
            assertThat(body.status()).isEqualTo("PENDING");
            assertThat(body.items()).hasSize(1);

            // DB検証
            Optional<Order> saved = orderRepository.findById(OrderId.of(body.id()));
            assertThat(saved).isPresent();
        }

        @Test
        @DisplayName("異常: 認証なしで401")
        void shouldReturn401WhenNoAuth() {
            CreateOrderRequest request = testRequest();

            ResponseEntity<ErrorResponse> response = restTemplate.exchange(
                "/api/v1/orders",
                HttpMethod.POST,
                new HttpEntity<>(request),
                ErrorResponse.class
            );

            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
        }

        @Test
        @DisplayName("異常: バリデーションエラーで400")
        void shouldReturn400ForInvalidRequest() {
            String token = getAuthToken("customer-123");
            CreateOrderRequest request = CreateOrderRequest.builder()
                .items(List.of())  // 空のitems
                .build();

            ResponseEntity<ErrorResponse> response = restTemplate.exchange(
                "/api/v1/orders",
                HttpMethod.POST,
                new HttpEntity<>(request, authHeaders(token)),
                ErrorResponse.class
            );

            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
            assertThat(response.getBody().code()).isEqualTo("VALIDATION_ERROR");
        }
    }
}
```

## サービス間統合テスト

### Order-Inventory連携

| シナリオ | 手順 | 期待結果 | 検証項目 |
|---------|-----|---------|---------|
| 正常な在庫予約 | 注文作成 → 在庫確認 | 在庫減少, 予約作成 | 在庫数, 予約レコード |
| 注文キャンセル時の在庫解放 | 注文作成 → キャンセル | 在庫復元 | 在庫数が元に戻る |
| 在庫サービス障害時のリトライ | 注文作成 (在庫API一時障害) | リトライ後成功 | リトライ回数, 最終結果 |
| 在庫サービス長期障害時のフォールバック | 注文作成 (在庫API長期障害) | 適切なエラー | エラーメッセージ, 注文未作成 |

```java
@SpringBootTest
@Testcontainers
class OrderInventoryIntegrationTest {

    @Container
    static KafkaContainer kafka = new KafkaContainer();

    @MockBean
    private InventoryServiceClient inventoryClient;

    @Autowired
    private OrderApplicationService orderService;

    @Test
    @DisplayName("注文作成時に在庫が予約される")
    void shouldReserveInventoryOnOrderCreation() {
        // Given
        when(inventoryClient.reserveInventory(any()))
            .thenReturn(ReservationResult.success("res-123"));

        // When
        Order order = orderService.createOrder(testCommand());

        // Then
        verify(inventoryClient).reserveInventory(argThat(req ->
            req.getItems().size() == 1 &&
            req.getItems().get(0).getQuantity() == 2
        ));
    }

    @Test
    @DisplayName("注文キャンセル時に在庫予約が解放される")
    void shouldReleaseInventoryOnCancel() {
        // Given
        Order order = createTestOrder();

        // When
        orderService.cancelOrder(order.getId(), "顧客都合");

        // Then
        verify(inventoryClient).releaseInventory("res-123");
    }

    @Test
    @DisplayName("在庫サービス障害時にリトライする")
    void shouldRetryOnInventoryServiceFailure() {
        // Given
        when(inventoryClient.reserveInventory(any()))
            .thenThrow(new ServiceUnavailableException())
            .thenThrow(new ServiceUnavailableException())
            .thenReturn(ReservationResult.success("res-123"));

        // When
        Order order = orderService.createOrder(testCommand());

        // Then
        verify(inventoryClient, times(3)).reserveInventory(any());
        assertThat(order).isNotNull();
    }
}
```

## Sagaテスト

### CreateOrderSaga

| シナリオ | ステップ | 期待動作 | 補償確認 |
|---------|---------|---------|---------|
| 全ステップ成功 | 注文→在庫→決済→確定 | 注文CONFIRMED | - |
| 在庫予約失敗 | 注文→在庫(失敗) | 注文CANCELLED | 注文キャンセル |
| 決済失敗 | 注文→在庫→決済(失敗) | 注文CANCELLED | 在庫解放, 注文キャンセル |
| 確定失敗 | 注文→在庫→決済→確定(失敗) | 注文CANCELLED | 返金, 在庫解放, 注文キャンセル |

```java
@SpringBootTest
class CreateOrderSagaIntegrationTest {

    @Test
    @DisplayName("全ステップ成功時に注文が確定される")
    void shouldConfirmOrderWhenAllStepsSucceed() {
        // Given
        mockInventorySuccess();
        mockPaymentSuccess();

        // When
        SagaResult result = sagaOrchestrator.execute(createOrderSaga());

        // Then
        assertThat(result.isSuccess()).isTrue();
        assertThat(orderRepository.findById(orderId).get().getStatus())
            .isEqualTo(OrderStatus.CONFIRMED);
    }

    @Test
    @DisplayName("決済失敗時に補償トランザクションが実行される")
    void shouldCompensateWhenPaymentFails() {
        // Given
        mockInventorySuccess();
        mockPaymentFailure();

        // When
        SagaResult result = sagaOrchestrator.execute(createOrderSaga());

        // Then
        assertThat(result.isSuccess()).isFalse();

        // 補償確認
        verify(inventoryService).releaseInventory(any());
        assertThat(orderRepository.findById(orderId).get().getStatus())
            .isEqualTo(OrderStatus.CANCELLED);
    }
}
```
```

### Step 5: エッジケース・エラーケース仕様の生成

**出力**: `reports/07_test-specs/edge-case-specs.md`

```markdown
# エッジケース・エラーケース仕様

## 境界値テスト

### Money

| ケース | 入力 | 期待結果 |
|-------|-----|---------|
| 最小値 | 0 | 成功 |
| 最小値-1 | -1 | IllegalArgumentException |
| 最大値 | 999,999,999,999 | 成功 |
| 最大値+1 | 1,000,000,000,000 | IllegalArgumentException |
| 加算でオーバーフロー | MAX + 1 | ArithmeticException |

### Quantity

| ケース | 入力 | 期待結果 |
|-------|-----|---------|
| 最小値 | 1 | 成功 |
| 最小値-1 | 0 | IllegalArgumentException |
| 最大値 | 9999 | 成功 |
| 最大値+1 | 10000 | IllegalArgumentException |

### Order Items

| ケース | 入力 | 期待結果 |
|-------|-----|---------|
| 最小商品数 | 1件 | 成功 |
| 最小商品数-1 | 0件 | InvalidOrderException |
| 最大商品数 | 100件 | 成功 |
| 最大商品数+1 | 101件 | InvalidOrderException |

## Null/Empty処理

| フィールド | null | 空文字 | 空白のみ | 期待結果 |
|-----------|------|-------|---------|---------|
| customerId | ❌ | ❌ | ❌ | NullPointerException / IllegalArgumentException |
| items | ❌ | - | - | InvalidOrderException |
| shippingAddress | ❌ | - | - | NullPointerException |
| postalCode | ❌ | ❌ | ❌ | ValidationException |
| notes (任意) | ✅ | ✅ | ✅ | 許可 |

## 同時実行・競合

| シナリオ | 条件 | 期待結果 |
|---------|-----|---------|
| 楽観ロック競合 | 同一注文を2トランザクションで更新 | 1件成功, 1件OptimisticLockException |
| 在庫競合 | 残り10個を2顧客が8個ずつ注文 | 1件成功, 1件InsufficientInventoryException |
| デッドロック回避 | Order→Inventory, Inventory→Order同時 | タイムアウトでリトライ |

## タイムアウト・リトライ

| シナリオ | 条件 | 期待結果 |
|---------|-----|---------|
| 在庫サービスタイムアウト | 応答 > 3秒 | リトライ3回後ServiceUnavailableException |
| 決済サービス一時障害 | 1,2回目失敗, 3回目成功 | 最終成功 |
| 決済サービス永続障害 | 全リトライ失敗 | PaymentFailedException + 補償 |

## セキュリティ

| シナリオ | 入力 | 期待結果 |
|---------|-----|---------|
| 他人の注文参照 | /orders/{他人のID} | 403 Forbidden |
| 他人の注文キャンセル | 他人の注文をキャンセル | 403 Forbidden |
| 不正なJWT | 期限切れトークン | 401 Unauthorized |
| スコープ不足 | orders:read のみでPOST | 403 Forbidden |
| SQLインジェクション | productId: "'; DROP TABLE--" | 無害化されエラー |

## データ整合性

| シナリオ | 条件 | 検証 |
|---------|-----|------|
| 注文作成中断 | 在庫予約後にプロセスクラッシュ | 孤立予約の検出・クリーンアップ |
| イベント発行失敗 | Kafkaダウン | 注文ロールバック or Outbox |
| DB接続断 | トランザクション中に切断 | ロールバック確認 |
```

### Step 6: パフォーマンステスト仕様の生成

**出力**: `reports/07_test-specs/performance-test-specs.md`

```markdown
# パフォーマンステスト仕様

## SLA要件

| API | p50 | p95 | p99 | スループット |
|-----|-----|-----|-----|------------|
| POST /orders | 100ms | 300ms | 500ms | 100 req/s |
| GET /orders/{id} | 50ms | 100ms | 200ms | 500 req/s |
| GET /orders | 100ms | 300ms | 500ms | 200 req/s |

## 負荷テストシナリオ

### 通常負荷

```yaml
scenario: normal_load
duration: 10m
users:
  constant: 50
requests:
  - endpoint: POST /orders
    weight: 20%
    think_time: 2s
  - endpoint: GET /orders/{id}
    weight: 50%
    think_time: 1s
  - endpoint: GET /orders
    weight: 30%
    think_time: 3s
assertions:
  - p95 < 300ms
  - error_rate < 0.1%
```

### ピーク負荷

```yaml
scenario: peak_load
duration: 5m
users:
  ramp_up: 100 over 2m
  hold: 100 for 3m
assertions:
  - p99 < 1s
  - error_rate < 1%
```

### スパイク負荷

```yaml
scenario: spike_load
duration: 5m
users:
  pattern:
    - 10 for 1m
    - 200 for 30s
    - 10 for 1m
    - 200 for 30s
    - 10 for 2m
assertions:
  - recovery_time < 30s
  - no_5xx_after_recovery
```

## k6スクリプト例

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function() {
  const token = getAuthToken();

  // 注文作成 (20%)
  if (Math.random() < 0.2) {
    const payload = JSON.stringify({
      items: [{ productId: 'prod-001', quantity: 1 }],
      shippingAddress: testAddress(),
    });

    const res = http.post(
      `${BASE_URL}/api/v1/orders`,
      payload,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    check(res, {
      'create order status 201': (r) => r.status === 201,
      'create order time < 500ms': (r) => r.timings.duration < 500,
    });
  }

  // 注文参照 (50%)
  else if (Math.random() < 0.7) {
    const orderId = getRandomOrderId();
    const res = http.get(
      `${BASE_URL}/api/v1/orders/${orderId}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    check(res, {
      'get order status 200': (r) => r.status === 200,
      'get order time < 200ms': (r) => r.timings.duration < 200,
    });
  }

  // 注文一覧 (30%)
  else {
    const res = http.get(
      `${BASE_URL}/api/v1/orders?pageSize=20`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    check(res, {
      'list orders status 200': (r) => r.status === 200,
      'list orders time < 500ms': (r) => r.timings.duration < 500,
    });
  }

  sleep(1);
}
```
```

### Step 7: テストデータ要件の生成

**出力**: `reports/07_test-specs/test-data-requirements.md`

```markdown
# テストデータ要件

## マスターデータ

### 顧客

| ID | 名前 | ステータス | 用途 |
|----|-----|----------|-----|
| customer-001 | テスト顧客A | ACTIVE | 正常系テスト |
| customer-002 | テスト顧客B | ACTIVE | 並行テスト |
| customer-003 | 休止顧客 | SUSPENDED | 異常系テスト |

### 商品

| ID | 名前 | 価格 | 初期在庫 | 用途 |
|----|-----|------|---------|-----|
| prod-001 | 標準商品A | 1000 | 1000 | 正常系 |
| prod-002 | 標準商品B | 2000 | 500 | 正常系 |
| prod-003 | 高額商品 | 999999 | 10 | 境界値 |
| prod-004 | 在庫少商品 | 1000 | 5 | 在庫不足テスト |
| prod-005 | 在庫なし商品 | 1000 | 0 | 在庫なしテスト |

## トランザクションデータ

### 注文

| ID | 顧客 | ステータス | 用途 |
|----|-----|----------|-----|
| order-pending-001 | customer-001 | PENDING | キャンセルテスト |
| order-confirmed-001 | customer-001 | CONFIRMED | ステータス遷移テスト |
| order-shipped-001 | customer-001 | SHIPPED | キャンセル不可テスト |
| order-cancelled-001 | customer-001 | CANCELLED | 再キャンセルテスト |

## データセットアップ

### JUnitセットアップ

```java
@TestConfiguration
public class TestDataConfig {

    @Bean
    public TestDataInitializer testDataInitializer(
        CustomerRepository customerRepository,
        ProductRepository productRepository,
        InventoryRepository inventoryRepository
    ) {
        return new TestDataInitializer(
            customerRepository,
            productRepository,
            inventoryRepository
        );
    }
}

@Component
public class TestDataInitializer {

    @PostConstruct
    public void init() {
        // 顧客データ
        customerRepository.save(Customer.builder()
            .id(CustomerId.of("customer-001"))
            .name("テスト顧客A")
            .status(CustomerStatus.ACTIVE)
            .build());

        // 商品データ
        productRepository.save(Product.builder()
            .id(ProductId.of("prod-001"))
            .name("標準商品A")
            .price(Money.of(1000))
            .build());

        // 在庫データ
        inventoryRepository.save(Inventory.builder()
            .productId(ProductId.of("prod-001"))
            .quantity(Quantity.of(1000))
            .build());
    }
}
```

### SQLセットアップ

```sql
-- test-data.sql

-- 顧客
INSERT INTO customers (id, name, status) VALUES
  ('customer-001', 'テスト顧客A', 'ACTIVE'),
  ('customer-002', 'テスト顧客B', 'ACTIVE'),
  ('customer-003', '休止顧客', 'SUSPENDED');

-- 商品
INSERT INTO products (id, name, price) VALUES
  ('prod-001', '標準商品A', 1000),
  ('prod-002', '標準商品B', 2000),
  ('prod-003', '高額商品', 999999),
  ('prod-004', '在庫少商品', 1000),
  ('prod-005', '在庫なし商品', 1000);

-- 在庫
INSERT INTO inventory (product_id, quantity) VALUES
  ('prod-001', 1000),
  ('prod-002', 500),
  ('prod-003', 10),
  ('prod-004', 5),
  ('prod-005', 0);
```

## データクリーンアップ

```java
@AfterEach
void cleanUp() {
    // トランザクションデータのみ削除
    // マスターデータは保持
    orderRepository.deleteAll();
    inventoryReservationRepository.deleteAll();
}
```
```

### Step 8: Mermaid図の検証

出力したファイルのMermaid図を検証し、エラーがあれば修正：

```bash
/fix-mermaid ./reports/07_test-specs
```

## 出力フォーマット

| ファイル | 内容 |
|---------|------|
| `bdd-scenarios/*.feature` | Gherkin形式のBDDシナリオ |
| `unit-test-specs.md` | ユニットテスト仕様とコード例 |
| `integration-test-specs.md` | 統合テスト仕様 |
| `edge-case-specs.md` | 境界値・エラーケース仕様 |
| `performance-test-specs.md` | パフォーマンステスト仕様 |
| `test-data-requirements.md` | テストデータ定義 |

## ツール活用ガイドライン

### 実装仕様読み込み

```bash
# ドメインサービス仕様
Read reports/06_implementation/domain-services-spec.md

# 例外マッピング
Read reports/06_implementation/exception-mapping.md
```

## エラーハンドリング

- 前提ファイル不足 → `/design-implementation` の実行を案内
- 仕様情報不足 → 最小限のテストケースを生成、TODO注記を追加

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/design-implementation` | 実装仕様（入力） |
| `/design-api` | API仕様（入力） |
