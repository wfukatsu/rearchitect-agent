# 値オブジェクト実装例

値オブジェクトの詳細な実装パターンとベストプラクティス。

## 基本原則

- **不変性**: `record` または `final` fields
- **バリデーション**: コンストラクタで実行
- **ファクトリメソッド**: `of()`, `generate()` 提供
- **equals/hashCode**: 値で比較（recordは自動実装）

## 1. ID値オブジェクト

```java
package com.example.order.domain.model;

import java.util.Objects;
import java.util.UUID;

/**
 * 注文IDを表す値オブジェクト
 */
public record OrderId(String value) {

    public OrderId {
        Objects.requireNonNull(value, "Order ID must not be null");
        if (value.isBlank()) {
            throw new IllegalArgumentException("Order ID must not be blank");
        }
        // UUID形式検証（任意）
        try {
            UUID.fromString(value);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Order ID must be a valid UUID: " + value);
        }
    }

    /**
     * 新規IDを生成
     */
    public static OrderId generate() {
        return new OrderId(UUID.randomUUID().toString());
    }

    /**
     * 既存の値からIDを生成
     */
    public static OrderId of(String value) {
        return new OrderId(value);
    }

    @Override
    public String toString() {
        return value;
    }
}
```

### 使用例
```java
// 新規生成
OrderId newId = OrderId.generate();

// 既存値から生成
OrderId existingId = OrderId.of("550e8400-e29b-41d4-a716-446655440000");
```

## 2. 金額値オブジェクト

```java
package com.example.shared.domain.model;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Currency;
import java.util.Objects;

/**
 * 金額を表す値オブジェクト
 */
public record Money(BigDecimal amount, Currency currency) {

    private static final Currency DEFAULT_CURRENCY = Currency.getInstance("JPY");

    public Money {
        Objects.requireNonNull(amount, "Amount must not be null");
        Objects.requireNonNull(currency, "Currency must not be null");
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount must not be negative: " + amount);
        }
        // 小数点以下の桁数を通貨に合わせる
        amount = amount.setScale(currency.getDefaultFractionDigits(), RoundingMode.HALF_UP);
    }

    public static Money of(long amount) {
        return new Money(BigDecimal.valueOf(amount), DEFAULT_CURRENCY);
    }

    public static Money of(BigDecimal amount) {
        return new Money(amount, DEFAULT_CURRENCY);
    }

    public static Money of(BigDecimal amount, Currency currency) {
        return new Money(amount, currency);
    }

    public static Money zero() {
        return new Money(BigDecimal.ZERO, DEFAULT_CURRENCY);
    }

    public Money add(Money other) {
        requireSameCurrency(other);
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public Money subtract(Money other) {
        requireSameCurrency(other);
        BigDecimal result = this.amount.subtract(other.amount);
        if (result.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Result cannot be negative");
        }
        return new Money(result, this.currency);
    }

    public Money multiply(int quantity) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(quantity)), this.currency);
    }

    public boolean isGreaterThan(Money other) {
        requireSameCurrency(other);
        return this.amount.compareTo(other.amount) > 0;
    }

    public boolean isZero() {
        return this.amount.compareTo(BigDecimal.ZERO) == 0;
    }

    private void requireSameCurrency(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException(
                "Currency mismatch: " + this.currency + " vs " + other.currency);
        }
    }

    /**
     * 永続化用: 最小単位（円）で取得
     */
    public long toMinorUnits() {
        return amount.movePointRight(currency.getDefaultFractionDigits()).longValue();
    }

    /**
     * 永続化から復元
     */
    public static Money fromMinorUnits(long minorUnits, Currency currency) {
        BigDecimal amount = BigDecimal.valueOf(minorUnits)
            .movePointLeft(currency.getDefaultFractionDigits());
        return new Money(amount, currency);
    }
}
```

### 使用例
```java
// 生成
Money price = Money.of(1000L);  // 1000円
Money total = price.multiply(3); // 3000円

// 計算
Money subtotal = Money.of(500L).add(Money.of(300L)); // 800円

// 永続化
long storedValue = price.toMinorUnits(); // DB保存用
Money restored = Money.fromMinorUnits(storedValue, Currency.getInstance("JPY"));
```

## 3. 列挙型値オブジェクト（状態遷移付き）

```java
package com.example.order.domain.model;

import java.util.Set;
import java.util.Map;

/**
 * 注文ステータス
 */
public enum OrderStatus {
    PENDING("保留中"),
    CONFIRMED("確定"),
    PROCESSING("処理中"),
    SHIPPED("発送済み"),
    DELIVERED("配達完了"),
    CANCELLED("キャンセル"),
    REFUNDED("返金済み");

    private final String displayName;

    private static final Map<OrderStatus, Set<OrderStatus>> VALID_TRANSITIONS = Map.of(
        PENDING, Set.of(CONFIRMED, CANCELLED),
        CONFIRMED, Set.of(PROCESSING, CANCELLED),
        PROCESSING, Set.of(SHIPPED, CANCELLED),
        SHIPPED, Set.of(DELIVERED, CANCELLED),
        DELIVERED, Set.of(),
        CANCELLED, Set.of(REFUNDED),
        REFUNDED, Set.of()
    );

    OrderStatus(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }

    public boolean canTransitionTo(OrderStatus next) {
        return VALID_TRANSITIONS.getOrDefault(this, Set.of()).contains(next);
    }

    public OrderStatus transitionTo(OrderStatus next) {
        if (!canTransitionTo(next)) {
            throw new IllegalStateException(
                "Invalid transition: " + this + " -> " + next);
        }
        return next;
    }
}
```

### 使用例
```java
OrderStatus status = OrderStatus.PENDING;

// 状態遷移チェック
if (status.canTransitionTo(OrderStatus.CONFIRMED)) {
    status = status.transitionTo(OrderStatus.CONFIRMED);
}

// 不正な遷移は例外
status.transitionTo(OrderStatus.DELIVERED); // IllegalStateException
```

## チェックリスト

値オブジェクト作成時:
- [ ] `record` を使用（またはimmutableクラス）
- [ ] コンストラクタでバリデーション実行
- [ ] ファクトリメソッド提供（`of`, `generate`）
- [ ] ビジネスロジックを値オブジェクト内に実装
- [ ] equals/hashCodeは値で比較
- [ ] 永続化用のメソッド提供（必要な場合）
