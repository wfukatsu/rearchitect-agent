# Mermaid ベストプラクティス

スキルがMermaid図を生成する際の必須ルール。15/27スキルがMermaid図を出力するため、全スキル共通で適用。

## 必須ルール

### 1. 日本語テキストは必ずダブルクオートで囲む

```mermaid
%% NG: スペースや特殊文字でパースエラー
A[監査セット 作成] --> B[ユーザー認証]

%% OK: ダブルクオートで囲む
A["監査セット作成"] --> B["ユーザー認証"]
```

### 2. HTMLタグ（`<br/>`等）はダブルクオート必須

```mermaid
%% NG
A[複数行<br/>テキスト]

%% OK
A["複数行<br/>テキスト"]
```

### 3. サブグラフ名はダブルクオートで囲む

```mermaid
%% NG
subgraph Phase 1 分析

%% OK
subgraph "Phase 1 分析"
```

### 4. エッジラベルにハイフン・特殊文字があればダブルクオート

```mermaid
%% NG
A -->|Customer-Supplier| B

%% OK
A -->|"Customer-Supplier"| B
```

### 5. ノードIDは英数字のみ（数字始まり不可）

```mermaid
%% NG
1[First] --> 2[Second]

%% OK
node1["First"] --> node2["Second"]
```

### 6. classDiagram のメソッド定義で日本語は使わない

```mermaid
%% NG
class Order {
  +注文作成()
}

%% OK
class Order {
  +createOrder()
}
```

## 図の種類と推奨用途

| 図の種類 | 用途 | 使用スキル例 |
|----------|------|-------------|
| `graph TD/LR` | アーキテクチャ、依存関係、フロー | system-investigation, design-microservices |
| `classDiagram` | ドメインモデル、エンティティ関係 | ddd-redesign, design-implementation |
| `erDiagram` | データベーススキーマ | design-scalardb, analyze-system |
| `sequenceDiagram` | API呼び出し、サービス間通信 | design-api, create-domain-story |
| `flowchart` | ビジネスプロセス、状態遷移 | map-domains, evaluate-mmi |

## 生成後の検証

Mermaid図を含むMarkdownを出力した後、`/fix-mermaid` で検証可能。
パイプライン実行時は `/full-pipeline` が最終ステップで自動検証を実行。
